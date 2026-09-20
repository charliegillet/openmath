"""Structural analysis of the 93-triangle arrangement: bounded faces, mutation candidates."""
import json
import sys
from fractions import Fraction
from itertools import combinations
from math import gcd

sys.path.insert(0, "hill")
import eval as H  # noqa: E402

LINES = [tuple(l) for l in json.load(open("solution/solution.json"))["lines"]]


def pts(lines):
    out = {}
    for i, j in combinations(range(len(lines)), 2):
        out[(i, j)] = H._intersection(lines[i], lines[j])
    return out


def bounded_faces(lines):
    """Face count + face shapes via the planar rotation system (exact)."""
    n = len(lines)
    P = pts(lines)
    # vertex key: exact rational point
    vertex_lines = {}
    for (i, j), p in P.items():
        if p is None:
            continue
        vertex_lines.setdefault(p, []).append(i)
        vertex_lines.setdefault(p, []).append(j)
    # for each (line, vertex) the neighbours along the line (prev/next in order)
    order = {}
    for li, line in enumerate(lines):
        vs = sorted({p for p in vertex_lines if li in vertex_lines[p]},
                    key=lambda p: Fraction(p[0 if line[1] else 1], p[2]))
        order[li] = vs
    rank = {li: {p: r for r, p in enumerate(vs)} for li, vs in order.items()}
    # directed edge on line li from vertex u to vertex v (consecutive)
    # trace faces: given directed edge (line, from_vertex, to_vertex), the next
    # edge is on the other line through to_vertex, going to its next neighbour in
    # the direction that keeps the face on the left/right consistently -> use the
    # "always turn to the angular next line at the vertex" rule with geometry.
    def angle_at(line_idx, v, going_to_line):
        """angle of the outgoing edge from vertex v along line going_to_line"""
        line = lines[going_to_line]
        # direction of travel along going_to_line at v: sign = order
        vs = order[going_to_line]
        r = rank[going_to_line][v]
        # pick a reference: direction of increasing coordinate
        other = vs[r + 1] if r + 1 < len(vs) else vs[r - 1]
        dx = Fraction(other[0], other[2]) - Fraction(v[0], v[2])
        dy = Fraction(other[1], other[2]) - Fraction(v[1], v[2])
        if r + 1 >= len(vs):
            dx, dy = -dx, -dy
        import math
        return math.atan2(float(dy), float(dx))

    faces = []
    visited = set()
    for li, vs in order.items():
        for a in range(len(vs) - 1):
            for d in (1, -1):  # direction along the line
                start = (li, vs[a], vs[a + 1]) if d == 1 else (li, vs[a + 1], vs[a])
                if start in visited:
                    continue
                walk = []
                cur = start
                ok = True
                while cur not in visited:
                    visited.add(cur)
                    walk.append(cur)
                    cl, cu, cv = cur
                    # at cv, arrive along cl; turn left (counter-clockwise) to the
                    # next line by angle
                    ang_in = angle_at(cl, cv, cl)
                    # incoming direction is toward cv
                    vlines = sorted(set(vertex_lines[cv]))
                    best = None
                    for nl in vlines:
                        if nl == cl:
                            continue
                        a_out = angle_at(cl, cv, nl)
                        delta = (a_out - ang_in) % (2 * 3.141592653589793)
                        # left turn = smallest positive delta
                        if best is None or delta < best[0]:
                            best = (delta, nl)
                    if best is None:
                        ok = False
                        break
                    nl = best[1]
                    nvs = order[nl]
                    r = rank[nl][cv]
                    nxt = nvs[r + 1] if r + 1 < len(nvs) else nvs[r - 1]
                    cur = (nl, cv, nxt)
                    if cur == start:
                        break
                if ok:
                    faces.append(walk)
    shapes = {}
    for f in faces:
        k = len(f)
        shapes[k] = shapes.get(k, 0) + 1
    return shapes, faces


if __name__ == "__main__":
    print("lines:", len(LINES))
    sh, faces = bounded_faces(LINES)
    print("face sizes (vertex count -> number):", dict(sorted(sh.items())))
    print("total faces traced:", len(faces))
