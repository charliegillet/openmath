"""Recover exact integer equations from the published Bader 18-line SVG."""

from fractions import Fraction
from itertools import combinations
from math import gcd


ENDPOINTS = [
    ("1.4257726932002015", "366.2570699732897", "798.5742273067998", "366.25706997328973"),
    ("1.239007507623512", "431.45903473558707", "798.7609924923765", "431.45903473558707"),
    ("3.7347410116465767", "345.4670327334634", "795.887903048619", "457.20811323376404"),
    ("67.42723582897867", "177.74933851246644", "741.7153980910228", "607.9196640712316"),
    ("109.47211809448754", "125.05718806359641", "734.475548219329", "619.3766342238374"),
    ("172.56794590218027", "70.94884779286002", "623.8984956783029", "731.46562964053"),
    ("239.21865350792504", "33.73594413293108", "620.8966061968683", "733.473671180658"),
    ("181.15842249094683", "65.17412890675683", "563.0308168919271", "765.2683297844901"),
    ("277.19482679036685", "19.317862997287477", "528.1636306124703", "778.9117097533808"),
    ("408.4617212894856", "0.08951092423313867", "376.9359009063686", "799.3345055626913"),
    ("426.5384753451968", "0.8813342797002406", "308.6911560036539", "789.438949012616"),
    ("572.275398167454", "38.999740739365734", "231.03359525514463", "762.5608280931597"),
    ("631.4395879249472", "73.75512702705862", "220.02581905249826", "757.2244311245746"),
    ("577.7085865557999", "41.64311327345774", "166.49923185618337", "724.7728302617811"),
    ("656.690547503782", "93.22652849014366", "138.21880329795408", "702.4410769939241"),
    ("755.1596555436522", "215.98473141036817", "50.692618783906084", "594.8957501536512"),
    ("781.947296002048", "281.1881189580604", "41.45152328746491", "577.3217128473574"),
    ("795.351825073872", "339.1975789070982", "3.5956195987614024", "453.5123088523574"),
]


def integer_line(endpoint):
    x1, y1, x2, y2 = map(Fraction, endpoint)
    coefficients = (y1 - y2, x2 - x1, x1 * y2 - x2 * y1)
    denominator = 1
    for value in coefficients:
        denominator = denominator * value.denominator // gcd(denominator, value.denominator)
    values = [int(value * denominator) for value in coefficients]
    divisor = gcd(gcd(abs(values[0]), abs(values[1])), abs(values[2]))
    values = [value // divisor for value in values]
    if next(value for value in values if value) < 0:
        values = [-value for value in values]
    return values


def integer_line_quantized(endpoint, scale):
    """Round published SVG coordinates to a fixed rational grid."""
    x1, y1, x2, y2 = (round(Fraction(value) * scale) for value in endpoint)
    values = [y1 - y2, x2 - x1, x1 * y2 - x2 * y1]
    divisor = gcd(gcd(abs(values[0]), abs(values[1])), abs(values[2]))
    values = [value // divisor for value in values]
    if next(value for value in values if value) < 0:
        values = [-value for value in values]
    return values


def intersection(first, second):
    a, b, c = first
    d, e, f = second
    w = a * e - b * d
    if w == 0:
        return None
    x, y = b * f - c * e, c * d - a * f
    divisor = gcd(gcd(abs(x), abs(y)), abs(w))
    if w < 0:
        divisor = -divisor
    return x // divisor, y // divisor, w // divisor


def count_triangles(lines):
    n = len(lines)
    points = [[None] * n for _ in range(n)]
    vertices = [set() for _ in lines]
    for i, j in combinations(range(n), 2):
        point = intersection(lines[i], lines[j])
        points[i][j] = points[j][i] = point
        if point is not None:
            vertices[i].add(point)
            vertices[j].add(point)
    ranks = []
    for line, line_vertices in zip(lines, vertices):
        axis = 0 if line[1] else 1
        ordered = sorted(line_vertices, key=lambda p: Fraction(p[axis], p[2]))
        ranks.append({point: rank for rank, point in enumerate(ordered)})
    triangles = []
    for i, j, k in combinations(range(n), 3):
        ij, ik, jk = points[i][j], points[i][k], points[j][k]
        if ij is None or ik is None or jk is None or ij == ik:
            continue
        if (
            abs(ranks[i][ij] - ranks[i][ik]) == 1
            and abs(ranks[j][ij] - ranks[j][jk]) == 1
            and abs(ranks[k][ik] - ranks[k][jk]) == 1
        ):
            triangles.append([i, j, k])
    return triangles


if __name__ == "__main__":
    for digits in range(0, 13):
        scale = 10**digits
        lines = [integer_line_quantized(endpoint, scale) for endpoint in ENDPOINTS]
        triangles = count_triangles(lines)
        maximum = max(abs(value) for line in lines for value in line)
        print(f"digits={digits} triangles={len(triangles)} max_coefficient={maximum}")
        if len(triangles) == 93:
            print({"lines": lines})
            break
