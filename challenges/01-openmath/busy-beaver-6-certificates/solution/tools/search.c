// Parallel search: random 6-state 2-symbol TMs (blank tape).
// Finds halting runs that REACH ALL SIX STATES, maximizing steps under a cap.
// Span convention matches the hill's evaluator: the halting transition's move is
// applied and included in the span.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>

#define NSTATE 6
#define HALT 6
#define BUFSZ (1u << 21)
#define CENTER (BUFSZ / 2)

typedef struct { uint8_t w, m, n; } T;   // n == HALT means halt

typedef struct {
    uint32_t *tape;
    uint32_t gen;
} Ctx;

typedef struct {
    unsigned long long steps;
    uint64_t ones, span;
    T m[NSTATE][2];
} Best;

static inline uint64_t xrand(uint64_t *s) {
    uint64_t x = *s; x ^= x << 13; x ^= x >> 7; x ^= x << 17; *s = x; return x;
}

// Returns 1 if halted. Requires all six states to have executed a transition.
static inline int simulate(Ctx *c, const T m[NSTATE][2], uint64_t cap,
                           unsigned long long *steps_out, uint64_t *ones_out,
                           uint64_t *span_out) {
    c->gen++;
    uint32_t tag = c->gen << 8;
    uint32_t *tape = c->tape;
    size_t head = CENTER;
    int cur = 0;
    unsigned long long steps = 0;
    uint64_t ones = 0;
    size_t lo = CENTER, hi = CENTER;
    unsigned reached = 1u;

    while (steps < cap) {
        uint32_t cell = tape[head];
        int sym = ((cell >> 8) == c->gen) ? (int)(cell & 1u) : 0;
        T t = m[cur][sym];
        steps++;
        if (t.w != sym) {
            if (t.w) { tape[head] = tag | 1u; ones++; }
            else     { tape[head] = tag | 0u; ones--; }
        }
        // the evaluator applies the move and span update BEFORE testing halt
        if (t.m) { head++; if (head > hi) hi = head; }
        else     { head--; if (head < lo) lo = head; }
        if (t.n == HALT) {
            if (reached != 0x3Fu) return 0;      // must have used all six states
            *steps_out = steps; *ones_out = ones; *span_out = (uint64_t)(hi - lo + 1);
            return 1;
        }
        cur = t.n;
        reached |= (1u << cur);
    }
    return 0;
}

static unsigned long long CAP;
static volatile int stop_flag = 0;
static Best global_best;
static pthread_mutex_t best_mu = PTHREAD_MUTEX_INITIALIZER;

static void *worker(void *arg) {
    uint64_t seed = (uint64_t)(uintptr_t)arg * 0x9E3779B97F4A7C15ULL + 12345;
    Ctx c;
    c.gen = 0;
    c.tape = calloc(BUFSZ, sizeof(uint32_t));
    if (!c.tape) return NULL;
    Best best; memset(&best, 0, sizeof best);
    for (;;) {
        if (stop_flag) break;
        T m[NSTATE][2];
        m[0][0].w = 1; m[0][0].m = 1; m[0][0].n = 1;   // canonical A0 = 1RB
        unsigned seen = 1u << 1;
        for (int s = 0; s < NSTATE; s++)
            for (int k = 0; k < 2; k++) {
                if (s == 0 && k == 0) continue;
                uint64_t r = xrand(&seed);
                m[s][k].w = (r >> 1) & 1;
                m[s][k].m = r & 1;
                m[s][k].n = (r >> 3) % 7;
                if (m[s][k].n < NSTATE) seen |= 1u << m[s][k].n;
            }
        if (seen != 0x3Fu) continue;   // cheap necessary condition
        unsigned long long st; uint64_t on, sp;
        if (simulate(&c, m, CAP, &st, &on, &sp) && st > best.steps) {
            best.steps = st; best.ones = on; best.span = sp;
            memcpy(best.m, m, sizeof m);
            pthread_mutex_lock(&best_mu);
            if (st > global_best.steps) global_best = best;
            pthread_mutex_unlock(&best_mu);
        }
    }
    free(c.tape);
    return NULL;
}

static const char *mn(int n) {
    static const char *s[] = {"A", "B", "C", "D", "E", "F", "H"};
    return s[n];
}

int main(int argc, char **argv) {
    // Self-test mode: ./search --selftest <spec> <cap>  -> prints steps/ones/span
    if (argc > 2 && strcmp(argv[1], "--selftest") == 0) {
        Ctx c; c.gen = 0; c.tape = calloc(BUFSZ, sizeof(uint32_t));
        T m[NSTATE][2];
        const char *g = argv[2];
        for (int s = 0; s < NSTATE; s++) {
            for (int k = 0; k < 2; k++) {
                m[s][k].w = g[k * 3] - '0';
                m[s][k].m = (g[k * 3 + 1] == 'R');
                char ch = g[k * 3 + 2];
                m[s][k].n = (ch >= 'A' && ch <= 'F') ? ch - 'A' : HALT;
            }
            g += (s < NSTATE - 1) ? 7 : 6;
        }
        unsigned long long st; uint64_t on, sp;
        int ok = simulate(&c, m, strtoull(argv[3] ? argv[3] : "250000", NULL, 10), &st, &on, &sp);
        printf("selftest halted=%d steps=%llu ones=%llu span=%llu\n", ok, st, (unsigned long long)on, (unsigned long long)sp);
        return 0;
    }
    CAP = (argc > 1) ? strtoull(argv[1], NULL, 10) : 250000ull;
    int secs = (argc > 2) ? atoi(argv[2]) : 60;
    int nthreads = (argc > 3) ? atoi(argv[3]) : 8;

    pthread_t th[128];
    for (int i = 0; i < nthreads; i++) pthread_create(&th[i], NULL, worker, (void *)(uintptr_t)(i + 1));
    for (int t = 0; t < secs; t++) {
        sleep(1);
        pthread_mutex_lock(&best_mu);
        Best b = global_best;
        pthread_mutex_unlock(&best_mu);
        if (b.steps) printf("[%4ds] best steps=%llu ones=%llu span=%llu\n", t + 1, b.steps, (unsigned long long)b.ones, (unsigned long long)b.span);
        else printf("[%4ds] none yet\n", t + 1);
        fflush(stdout);
    }
    stop_flag = 1;
    for (int i = 0; i < nthreads; i++) pthread_join(th[i], NULL);

    Best b = global_best;
    if (!b.steps) { printf("NOTHING FOUND\n"); return 0; }
    char spec[256]; spec[0] = 0;
    for (int s = 0; s < NSTATE; s++) {
        char part[32];
        if (s) strcat(spec, "_");
        snprintf(part, sizeof part, "%d%s%s", b.m[s][0].w, b.m[s][0].m ? "R" : "L", mn(b.m[s][0].n));
        strcat(spec, part);
        snprintf(part, sizeof part, "%d%s%s", b.m[s][1].w, b.m[s][1].m ? "R" : "L", mn(b.m[s][1].n));
        strcat(spec, part);
    }
    printf("BEST steps=%llu ones=%llu span=%llu spec=%s\n",
           b.steps, (unsigned long long)b.ones, (unsigned long long)b.span, spec);
    return 0;
}
