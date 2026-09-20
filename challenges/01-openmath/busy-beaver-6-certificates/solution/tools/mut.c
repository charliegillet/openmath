// Mutation search seeded from known long-running 6-state machines.
// Reads specs (one per line, first whitespace-separated token) and explores
// single- and double-cell mutations, keeping any halting run <= cap that
// reaches all six states. Maximises steps.
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
#define MAXSEED 8192

typedef struct { uint8_t w, m, n; } T;
typedef struct { uint32_t *tape; uint32_t gen; } Ctx;
typedef struct { unsigned long long steps; uint64_t ones, span; char spec[64]; } Best;

static unsigned long long CAP;
static volatile int stop_flag = 0;
static Best g_best;
static pthread_mutex_t mu = PTHREAD_MUTEX_INITIALIZER;
static char seeds[MAXSEED][64];
static int nseeds = 0;

static inline int simulate(Ctx *c, const T m[NSTATE][2], uint64_t cap,
                           unsigned long long *steps_out, uint64_t *ones_out, uint64_t *span_out) {
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
        if (t.w != sym) { if (t.w) { tape[head] = tag | 1u; ones++; } else { tape[head] = tag | 0u; ones--; } }
        if (t.m) { head++; if (head > hi) hi = head; } else { head--; if (head < lo) lo = head; }
        if (t.n == HALT) {
            if (reached != 0x3Fu) return 0;
            *steps_out = steps; *ones_out = ones; *span_out = (uint64_t)(hi - lo + 1);
            return 1;
        }
        cur = t.n; reached |= (1u << cur);
    }
    return 0;
}

static const char *MN = "ABCDEFH";

static void to_spec(const T m[NSTATE][2], char *out) {
    int p = 0;
    for (int s = 0; s < NSTATE; s++) {
        for (int k = 0; k < 2; k++)
            p += sprintf(out + p, "%d%c%c", m[s][k].w, m[s][k].m ? 'R' : 'L', MN[m[s][k].n]);
        if (s < NSTATE - 1) out[p++] = '_';
    }
    out[p] = 0;
}

static int parse_spec(const char *g, T m[NSTATE][2]) {
    if (strlen(g) < 41) return 0;
    for (int s = 0; s < NSTATE; s++) {
        for (int k = 0; k < 2; k++) {
            if (g[k*3] != '0' && g[k*3] != '1') return 0;
            if (g[k*3+1] != 'L' && g[k*3+1] != 'R') return 0;
            m[s][k].w = g[k*3] - '0';
            m[s][k].m = (g[k*3+1] == 'R');
            char ch = g[k*3+2];
            m[s][k].n = (ch >= 'A' && ch <= 'F') ? ch - 'A' : HALT;
        }
        g += (s < NSTATE - 1) ? 7 : 6;
    }
    return 1;
}

static void offer(Ctx *c, const T m[NSTATE][2]) {
    unsigned long long st; uint64_t on, sp;
    if (!simulate(c, m, CAP, &st, &on, &sp)) return;
    if (st <= g_best.steps) return;
    pthread_mutex_lock(&mu);
    if (st > g_best.steps) { g_best.steps = st; g_best.ones = on; g_best.span = sp; to_spec(m, g_best.spec); }
    pthread_mutex_unlock(&mu);
}

static void *worker(void *arg) {
    long id = (long)(uintptr_t)arg;
    Ctx c; c.gen = 0; c.tape = calloc(BUFSZ, sizeof(uint32_t));
    if (!c.tape) return NULL;

    for (int si = id; si < nseeds; si += 8) {
        T base[NSTATE][2];
        if (!parse_spec(seeds[si], base)) continue;
        // single mutations
        for (int s = 0; s < NSTATE; s++) for (int k = 0; k < 2; k++)
            for (int w = 0; w < 2; w++) for (int mv = 0; mv < 2; mv++) for (int n = 0; n < 7; n++) {
                if (stop_flag) { free(c.tape); return NULL; }
                T m[NSTATE][2]; memcpy(m, base, sizeof m);
                m[s][k].w = w; m[s][k].m = mv; m[s][k].n = n;
                offer(&c, m);
            }
        // double mutations on symbolic structure (writes/moves only)
        for (int a = 0; a < 12; a++) for (int b = a + 1; b < 12; b++) {
            for (int w = 0; w < 2; w++) {
                if (stop_flag) { free(c.tape); return NULL; }
                T m[NSTATE][2]; memcpy(m, base, sizeof m);
                m[a/2][a%2].w = w; m[b/2][b%2].w = 1 - w;
                offer(&c, m);
            }
        }
    }
    free(c.tape);
    return NULL;
}

int main(int argc, char **argv) {
    const char *seedfile = argc > 1 ? argv[1] : "6x2.txt";
    CAP = argc > 2 ? strtoull(argv[2], NULL, 10) : 250000ull;
    int secs = argc > 3 ? atoi(argv[3]) : 120;
    FILE *f = fopen(seedfile, "r");
    if (!f) { perror("seedfile"); return 1; }
    char line[512];
    while (fgets(line, sizeof line, f) && nseeds < MAXSEED) {
        char *sp = strpbrk(line, " \t\r\n");
        if (sp) *sp = 0;
        if (strlen(line) >= 41) snprintf(seeds[nseeds++], 64, "%s", line);
    }
    fclose(f);
    printf("loaded %d seeds, cap=%llu\n", nseeds, CAP); fflush(stdout);

    pthread_t th[8];
    for (long i = 0; i < 8; i++) pthread_create(&th[i], NULL, worker, (void *)(uintptr_t)i);
    for (int t = 0; t < secs; t++) {
        sleep(1);
        pthread_mutex_lock(&mu);
        Best b = g_best;
        pthread_mutex_unlock(&mu);
        printf("[%4ds] best steps=%llu ones=%llu span=%llu %s\n", t + 1, b.steps,
               (unsigned long long)b.ones, (unsigned long long)b.span, b.spec);
        fflush(stdout);
        if (t > 4 && b.steps == 0) break;
    }
    stop_flag = 1;
    for (int i = 0; i < 8; i++) pthread_join(th[i], NULL);
    printf("FINAL steps=%llu ones=%llu span=%llu spec=%s\n", g_best.steps,
           (unsigned long long)g_best.ones, (unsigned long long)g_best.span, g_best.spec);
    return 0;
}
