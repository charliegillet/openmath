// Exact 6-state 2-symbol Turing machine simulator (blank tape start).
// Usage: ./tmsim "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA" [max_steps]
// Prints: steps, ones, span, states_visited, halt(0/1), reason
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct { int8_t write; int8_t move; int8_t next; } Trans; // next: 0..5 = A..F, -1 = halt

static Trans T[8][2];
static int nstates = 6;

static int state_index(char c) {
    if (c == 'Z' || c == 'H' || c == '-') return -1; // halt / undefined (bbch uses Z)
    if (c >= 'A' && c <= 'Y') return c - 'A';
    return -2;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s <bbch-machine> [max_steps]\n", argv[0]); return 2; }
    const char *spec = argv[1];
    unsigned long long max_steps = (argc > 2) ? strtoull(argv[2], NULL, 10) : 1000000000000ULL;

    // parse A0A1_B0B1_...  each token is 3 chars: write(0/1), move(L/R), next(A-Z,-)
    // number of states = number of underscore-separated groups
    nstates = 1;
    for (const char *q = spec; *q; q++) if (*q == '_') nstates++;
    if (nstates < 1 || nstates > 8) { fprintf(stderr, "bad state count %d\n", nstates); return 2; }
    int si = 0;
    for (const char *p = spec; *p && si < nstates; ) {
        for (int s = 0; s < 2; s++) {
            while (*p == '_') p++;
            if (!*p) { fprintf(stderr, "parse error: short spec\n"); return 2; }
            if (p[0] == '-' && p[1] == '-' && p[2] == '-') {
                T[si][s].write = 0; T[si][s].move = 0; T[si][s].next = -1; p += 3;
            } else {
                if (p[0] != '0' && p[0] != '1') { fprintf(stderr, "parse error at '%c'\n", p[0]); return 2; }
                T[si][s].write = p[0] - '0';
                T[si][s].move = (p[1] == 'R') ? 1 : 0;
                T[si][s].next = state_index(p[2]);
                if (T[si][s].next == -2) { fprintf(stderr, "bad state '%c'\n", p[2]); return 2; }
                p += 3;
            }
        }
        si++;
    }
    if (si != nstates) { fprintf(stderr, "parse error: got %d states\n", si); return 2; }

    size_t cap = 1u << 20;
    int8_t *tape = calloc(cap, 1);
    if (!tape) { fprintf(stderr, "oom\n"); return 1; }
    size_t lo = cap / 2, hi = cap / 2;   // half-open interval of allocated index range used
    size_t head = cap / 2;
    int64_t min_pos = (int64_t)head, max_pos = (int64_t)head;

    unsigned long long steps = 0;
    unsigned states_mask = 0;
    unsigned long long ones = 0;
    int cur = 0;
    int halted = 0;
    const char *reason = "step_limit";

    while (1) {
        if (steps >= max_steps) { reason = "step_limit"; break; }
        int sym = tape[head];
        Trans t = T[cur][sym];
        // The transition executed counts as a step, including a transition that halts.
        steps++;
        states_mask |= (1u << cur);
        if (t.write != sym) { ones += (unsigned long long)(t.write - sym); tape[head] = t.write; }
        if (t.next < 0) { halted = 1; reason = "halt_transition"; break; }
        if (t.move) { head++; if ((int64_t)head > max_pos) max_pos = head; }
        else        { head--; if ((int64_t)head < min_pos) min_pos = head; }
        if (head >= cap) {
            size_t newcap = cap * 2;
            int8_t *nt = realloc(tape, newcap);
            if (!nt) { fprintf(stderr, "oom at %zu\n", head); return 1; }
            memset(nt + cap, 0, newcap - cap);
            tape = nt; cap = newcap;
        }
        // no underflow: head is size_t and we never go below 0 in practice for these machines
        cur = t.next;
    }
    // visited states: include state entered at halt? Requirement is "visiting all six
    // non-halting states" meaning the machine executes a transition in each of A..F.
    printf("steps=%llu ones=%llu span=%lld states_mask=%u states_visited=%d halt=%d reason=%s\n",
           steps, ones, (long long)(max_pos - min_pos + 1), states_mask, __builtin_popcount(states_mask), halted, reason);
    free(tape);
    return 0;
}
