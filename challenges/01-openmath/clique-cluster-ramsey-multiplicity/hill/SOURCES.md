# Sources, selection, and frozen research baseline

Literature check: 2026-09-19. This is evidence for choosing a research target, not a complete mathematical review or a guarantee of novelty. Recheck status before the competition freeze and review every result against prior work.

## Primary research

- Olaf Parczyk, Sebastian Pokutta, Christoph Spiegel and Tibor Szabo, *New Ramsey Multiplicity Bounds and Search Heuristics*, arXiv:2206.04036v3, 13 September 2024; Foundations of Computational Mathematics 25 (2025), 1777-1814. https://arxiv.org/html/2206.04036v3 and https://doi.org/10.1007/s10208-024-09675-6 . Section 1 defines c4 and records the open exact-value problem; section 3 gives constructive search methods and blow-ups. The FINAL NOTE records McKay's improved upper bound 10486266368/768^4, used here rather than the weaker headline theorem.
- Their openly supplied construction data: https://doi.org/10.5281/zenodo.6364588 , resolving to record 6602512. The 768-vertex graph in graphs/c4.graph6.txt is provided as an attributed starting construction. It is prior work and does not beat the final-note reference. The hill does not assert that this seed is McKay's later graph.
- Juanjo Rue and Christoph Spiegel, *The Rado multiplicity problem in vector spaces over finite fields*, Finite Fields and Their Applications 111 (2026), 102782, introduction. https://doi.org/10.1016/j.ffa.2025.102782 . This later paper still describes the unresolved gap for clique multiplicities beyond triangles. It does not claim a new c4 upper bound.

Searches for later K4 Ramsey multiplicity improvements, the exact McKay numerator, and the quoted density found no stronger c4 bound in the primary sources inspected. This bounded search does not prove the absence of a newer result. The evaluator deliberately names its milestone reference_beaten rather than world_record or conjecture_solved.

## Connection to the organizer's work

- Alejandro Zarzuelo Urdiales, *Clique-Size Dominance Threshold Distribution: Enumerating Labeled Graphs by Clique Number and the Minimum Coding Clique Size*, May 2026. https://doi.org/10.5281/zenodo.20004703 . The introduction describes replacing multigraph vertices with coding cliques and discusses clique counts and Ramsey theory.
- Associated code and statements: https://github.com/alejandrozu/Clique-OEIS ; research overview: https://alejandrozarzuelo.com/ . These establish the thematic connection. This hill uses its own explicit weighted blow-up semantics and assumes none of the organizer's embedding theorems.

## Why this target was selected

The old linear-arboricity hill contains a solved small catalog, and adding more sampled cases would still not certify a theorem beyond those cases. Small Ramsey-number records are very famous but often supply little gradual feedback. Broad list-coloring or linear-arboricity theorems need a precisely chosen unsolved class and a general proof checker before they can become honest automatic hills.

The selected c4 construction problem has a sourced open frontier, an exact objective, reusable public seeds, visual clique clusters, and a simple proven passage from a finite artifact to an unbounded graph family. This makes a concentrated week of AI-assisted search and certification plausible. It does not establish that a research breakthrough will happen in one week; the best-known bound is a serious target.

No OPDP competition difficulty, novelty ruling, or focus-set admission is invented here. Those require the handbook's independent assessment and review. This is a construction hill aimed at partial progress on the original problem, not a claim that choosing a finite template creates a new famous open problem.
