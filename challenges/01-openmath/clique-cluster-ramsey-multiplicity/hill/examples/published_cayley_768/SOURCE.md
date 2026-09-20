# Published starting construction — prior work

Authors: Olaf Parczyk, Sebastian Pokutta, Christoph Spiegel, Tibor Szabo.
Paper: https://arxiv.org/html/2206.04036v3, Theorem 1.1.
Dataset: https://doi.org/10.5281/zenodo.6364588 (version record 6602512).
Source: `graphs.zip`, member `graphs/c4.graph6.txt`.
Archive SHA256: `6ff8a2496c545e86def3a12bd69ef557c50a890c732a8506d30b1bbe8467ec89`.

The graph6 upper triangle was decoded into a symmetric adjacency matrix,
with all block weights 1 and diagonal 0 (blue cliques / red independent
blocks). There are 768 vertices and 148608 red edges. The exact checker
reproduces `4551721/150994944`, the headline bound in the paper.

This is NOT McKay's later 768-vertex graph. It does NOT beat the frozen
reference `10486266368/768^4`, and is supplied only for reproduction and
as a starting point for new work. Published seed reproduction is a
regression test, not evidence of a new result.
