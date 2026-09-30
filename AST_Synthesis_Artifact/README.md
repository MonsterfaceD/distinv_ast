# AST certificate synthesis artifact

This artifact accompanies Section 6, "Template-Based Certificate Synthesis".
It contains a shared CEGIS engine, exact and abstract program inputs, and
recorded outputs of actual executions. It is anonymous and self-contained.
No network access is used after installing the solver.

## Quick start

Tested with Python 3.12.14 and `z3-solver==4.15.4.0` (Z3 reports `4.15.4`).
Run these commands from this directory:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 synthesis_examples.py --output reproduced_results.json
python3 diagnostics.py --output reproduced_diagnostics.json
python3 audit_sampler_certificates.py --output reproduced_audit.json
```

On Windows, activate with `.venv\Scripts\activate` instead. The last command
uses only Python's standard library and can run without Z3. Compare statuses,
verified coefficients, and logical checks with the supplied JSON files.
Do not expect identical timings or solver-selected counterexamples.

## File map

| File | Purpose / corresponding paper result |
| --- | --- |
| `engine.py` | Shared guarded affine and supplied-partition affine CEGIS; Section 6 constraints and soundness proposition. |
| `examples.py` | Supplied invariants, complete body semantics, optional partitions; Random Walk, FDR, exact FLDR tree constructor, abstract FLDR family. |
| `synthesis_examples.py` | Reproduce all eight positive synthesis experiments and the bounded negative two-sided-walk experiment. |
| `results.json` | Recorded candidates, coefficients, counterexamples, bounds, SMT checks, solver/Python versions, and actual wall times. |
| `diagnostics.py` | Negative validation cases, cross-region countdown, symbolic FDR drift check, concrete FLDR rational audit, finite tree regressions. |
| `diagnostics.json` | Recorded output of these checks; Appendix D. |
| `audit_sampler_certificates.py` | Independent bounded exact-arithmetic audit of FDR pCFG certificates and the Han–Hoshi certificate; Section 5 and Appendix B. |
| `audit_results.json` | Recorded finite domains and results of that audit. |
| `requirements.txt` | Exact solver distribution version used in the recorded run. |

## Inputs versus inferred results

The caller supplies state variables, integer symbolic parameters, initial-state
description, guard, support invariant, and complete body outcomes with positive
fixed rational probabilities. There is no parser, invariant discovery, or
automatic abstraction discovery. All declared integer components plus a
constant are features; Boolean flags and transition descriptors are excluded.
Every coefficient of V and U is independently unknown. There is no supplied
relation between coefficient vectors or example-specific feature subset.

Both functions are zero outside the guard. On each active region the kernel
uses a full affine expression with unknown integer coefficients. The single
region `true` gives the ordinary guarded affine template. Optional predicates
are fixed by the caller; threshold positions are not synthesized. Successor
states select their own regions, so region crossings are included.

The default coefficient bounds are 1, 2, 4, 8, 16. The learner minimizes the sum
of absolute coefficients, with solver-dependent ties. Samples are selected
by SMT, not manually seeded. A failed range is enlarged while retaining
counterexamples. V and U are searched together because `U <= V` couples their
constraints, but their coefficient blocks are independent.

## Obligations and trust boundary

On every enabled state in the supplied support the kernel requires:

- V >= 1 and U >= 1;
- E[V after one complete body execution] <= V;
- at least one positive-probability outcome has U' <= U - 1;
- U <= V.

The last condition implies bounded U on every V-sublevel. It is sufficient,
not equivalent to the general rule. Integer coefficients and V >= 1 further
restrict the class. Epsilon is at least the smallest fixed outcome weight;
all paper synthesis examples use two fair-bit outcomes and epsilon = 1/2.

Initial inclusion and support preservation are separate SMT checks. Partitions
must cover the active invariant domain and be pairwise disjoint. Undeclared
partition symbols and transition descriptors in partitions are rejected.
Inputs are trusted executable Python/Z3 encodings, not a hardened parser for
arbitrary or hostile formulas. Shipped examples use Boolean combinations of
linear arithmetic and piecewise affine updates. Other nonlinear encodings
are outside the claimed supported fragment.

The verifier asks for **any integer state** violating a fixed candidate;
there is no artificial bound on x, n, or other symbolic parameters. Verifier
UNSAT establishes the supplied obligations universally, subject to the trusted
solver and encoding. Each successful candidate is checked again one obligation
at a time. Z3 proof objects are not extracted or independently checked.

Learner UNSAT instead excludes only the current bounded coefficient template.
UNKNOWN, timeouts, and candidate limits are inconclusive. With exact terminating
solvers and no resource limits, each counterexample excludes its candidate,
so finite-template CEGIS terminates. This is not completeness for all AST
programs or all affine certificates.

## Expected synthesis results

Expressions below hold on active states; terminal values are zero.
`results.json` contains the definitive recorded coefficients and counts.

| Input | Supplied numerical features | Verified result | Bound |
| --- | --- | --- | --- |
| Nonnegative random walk | x, 1 | V = U = x | 1 |
| FDR, symbolic n | n, v, c, 1 | V = n; U = n-v+c | 1 |
| FLDR, weights (4,5) | c, d, 1 | V = U = c-2d+2 | 2 |
| FLDR structural abstraction | m, k, n, c, d, 1 | V = m; U = m-c | 1 |
| Two-sided walk, x<0 / x>=0 | x, 1 per region | V = U = abs(x) | 1 |
| FDR, 2v<n / 2v>=n | n, v, c, 1 per region | V = n; U = n-v+c in both regions | 1 |
| FLDR (4,5), c<3 / c>=3 | c, d, 1 per region | V = U = c-2d+2 below 3; c at depth 3 | 2 |
| FLDR abstract, c<k-1 / c>=k-1 | m, k, n, c, d, 1 per region | V = k; U = k-c below k-1, 1 otherwise | 1 |

The unpartitioned two-sided walk returns `no_certificate_in_bounded_template`
for the configured bounds. The stronger all-bounds impossibility argument is
analytic: an affine positive function on both unbounded integer tails has
zero slope, and a constant cannot progress at x=2. Bounded search alone would
not prove this claim.

Individual actual wall times are recorded in `results.json`; they are
machine-specific measurements, not benchmark results. The delivered complete
synthesis run took seconds to tens of seconds. Each solver call is limited
to 10 seconds and each input to 500 candidates. If a slower machine reports
inconclusive, increase the timeout:

```bash
python3 synthesis_examples.py --timeout-ms 60000 --output reproduced_results.json
python3 synthesis_examples.py --suite base --output base_results.json
python3 synthesis_examples.py --suite piecewise --output piecewise_results.json
```

## Meaning of the FLDR models

The exact constructor takes positive integer weights. It processes binary
weight columns, placing internal nodes before leaves and leaf labels in
descending order (rejection first). A rejecting child resets to (0,0) inside
the complete body step. Immediately accepting roots are handled, including
weights (1,), (2,), and (4,). For (4,5), the five active nodes are (0,0),
(1,0), (1,1), (2,0), and (3,0).

The symbolic model is a supplied overapproximation, not symbolic array
execution. Each child is continuation, reset, or acceptance; continuation
increases depth, height is bounded by k, and both children cannot reject.
All integer state components, including d, remain in the templates; a Boolean
activity flag denotes the guard. The root initializer permits either guard
value consistent with the support. Coverage ensures an admitted descriptor
pair exists at each enabled abstract state; it does **not** establish a
connection with concrete preprocessing. That connection is supplied by the
mathematical tree argument in Section 5.

`diagnostics.py` supplements the proof with a finite regression of 1,554
weight vectors (1–4 outcomes, each weight 1–6), checking exact leaf masses,
height, reset targets, the abstract contract, and d<2n. This is finite
evidence, not universal verification of preprocessing. It also audits
W=c-2d+2 using rational arithmetic on the entire fixed tree, verifies
V=k/U=k-c as an alternative abstract certificate, and shows the manual depth
variant has expected next value 5/2 at (2,0), where its current value is 2.

## Limits

- No comparison establishes an advantage over other synthesis tools.
- Supplied invariants, semantics, and partitions are substantial input.
- Abstract FLDR depends on its stated structural contract.
- FDR's synthesized U is itself a ranking supermartingale, checked separately.
- Concrete FLDR has a shared certificate once d is included; the depth-only
  obstruction does not prove that distinct functions are necessary.
- The artifact does not mechanize the general AST metatheory.
- Bounded FDR/HH audits and tree regressions do not replace formal proofs.
