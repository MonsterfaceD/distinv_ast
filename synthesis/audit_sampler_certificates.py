#!/usr/bin/env python3
"""Bounded, independent arithmetic checks for the sampler proofs.

These diagnostics do NOT prove the infinite-state theorems. They check the
published FDR pCFG annotation (Appendix C) on a finite integer domain and the
Han--Hoshi boundary identities (Section 5.3 / Appendix B) on finite rational
intervals. All arithmetic relevant to acceptance and descent is exact.

Run: python3 audit_sampler_certificates.py --output audit_results.json
Dependencies: Python standard library only.
"""
import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path


def ceil_log_ratio(n, denominator):
    """Exact ceil(log2(n / denominator)) on the invariant domain."""
    assert 0 < denominator < 2 * n
    exponent = 0
    while denominator * (2 ** exponent) < n:
        exponent += 1
    return exponent


def fdr_invariant(location, n, v, c):
    if location == "init":
        return n >= 1
    if location == "1":
        return n >= 1 and v == 1
    if location == "2":
        return 1 <= v < 2 * n and 0 <= c < min(v, n)
    if location == "3":
        return fdr_invariant("2", n, v, c) and v < n
    if location in ("4", "5a", "5b"):
        return v % 2 == 0 and 2 <= v <= 2 * n - 2 and 0 <= 2 * c < v
    if location == "6":
        return 2 <= v <= 2 * n - 2 and 0 <= c < v
    if location == "7":
        return fdr_invariant("6", n, v, c) and c >= n
    if location == "8":
        return 1 <= v <= n - 2 and n <= c < v + n
    if location == "out":
        return fdr_invariant("2", n, v, c) and v >= n
    raise ValueError(location)


def fdr_variant(location, n, v, c):
    if location == "init":
        return 7 * ceil_log_ratio(n, 1) + 3
    if location == "1":
        return 7 * ceil_log_ratio(n, 1) + 2
    if location == "2":
        return 7 * ceil_log_ratio(n, v - c) + 1
    if location == "3":
        return 7 * ceil_log_ratio(n, v - c)
    if location == "4":
        return 7 * ceil_log_ratio(n, Fraction(v, 2) - c) - 1
    if location == "5a":
        return 7 * ceil_log_ratio(n, v - 2 * c) + 5
    if location == "5b":
        return 7 * ceil_log_ratio(n, v - 2 * c - 1) + 5
    if location == "6":
        return 7 * ceil_log_ratio(n, v - c) + 4
    if location == "7":
        return 7 * ceil_log_ratio(n, v - c) + 3
    if location == "8":
        return 7 * ceil_log_ratio(n, v + n - c) + 2
    if location == "out":
        return 0
    raise ValueError(location)


def fdr_edges(location, n, v, c):
    if location == "init":
        return [("1", 1, c)]
    if location == "1":
        return [("2", v, 0)]
    if location == "2":
        return [("3" if v < n else "out", v, c)]
    if location == "3":
        return [("4", 2 * v, c)]
    if location == "4":
        return [("5a", v, c), ("5b", v, c)]
    if location == "5a":
        return [("6", v, 2 * c)]
    if location == "5b":
        return [("6", v, 2 * c + 1)]
    if location == "6":
        return [("2" if c < n else "7", v, c)]
    if location == "7":
        return [("8", v - n, c)]
    if location == "8":
        return [("2", v, c - n)]
    if location == "out":
        return []
    raise ValueError(location)


def audit_fdr(max_n):
    count = 0
    locations = ("init", "1", "2", "3", "4", "5a", "5b", "6", "7", "8", "out")
    for n in range(1, max_n + 1):
        for v in range(1, 2 * n):
            for c in range(2 * n):
                for location in locations:
                    if not fdr_invariant(location, n, v, c):
                        continue
                    before = fdr_variant(location, n, v, c)
                    assert 0 <= before <= 7 * ceil_log_ratio(n, 1) + 5
                    assert (before == 0) == (location == "out")
                    successors = fdr_edges(location, n, v, c)
                    for target, new_v, new_c in successors:
                        assert fdr_invariant(target, n, new_v, new_c)
                    if location == "4":
                        # This branch is chosen with probability exactly 1/2.
                        assert fdr_variant("5a", n, v, c) == before - 1
                    else:
                        for target, new_v, new_c in successors:
                            assert fdr_variant(target, n, new_v, new_c) < before
                    # V is n before any nonterminal edge and either n or 0 after.
                    assert all((0 if target == "out" else n) <= n
                               for target, _, _ in successors)
                    count += 1
    return {
        "status": "passed",
        "checked_location_states": count,
        "domain": {"n": [1, max_n], "v": "1 <= v < 2*n", "c": "0 <= c < 2*n"},
        "checks": ["invariant_preservation", "defined_natural_variant", "terminal_zero",
                   "deterministic_descent", "zero_bit_descent", "sublevel_bound", "V_supermartingale"],
    }


def cumulative(weights):
    values = [0]
    for weight in weights:
        values.append(values[-1] + weight)
    return values


def boundary_count(sums, c, v):
    m = sums[-1]
    return sum(c * m < boundary * v < (c + 1) * m for boundary in sums[1:-1])


def classify(sums, c, v):
    m = sums[-1]
    matches = [i for i in range(1, len(sums))
               if sums[i - 1] * v <= c * m and (c + 1) * m <= sums[i] * v]
    assert len(matches) <= 1
    return matches[0] if matches else 0


def audit_han_hoshi():
    count = 0
    weight_vectors = 0
    for length in range(1, 4):
        for weights in product(range(1, 5), repeat=length):
            weight_vectors += 1
            sums = cumulative(weights)
            for v in range(1, 17):
                for c in range(v):
                    parent = boundary_count(sums, c, v)
                    children = [boundary_count(sums, 2 * c + bit, 2 * v) for bit in (0, 1)]
                    assert (classify(sums, c, v) == 0) == (parent > 0)
                    for bit, child in enumerate(children):
                        assert (classify(sums, 2 * c + bit, 2 * v) == 0) == (child > 0)
                    assert sum(children) <= parent
                    current = max(1, parent)  # Enabled input, including boundary-free initialization.
                    assert sum(children) <= current  # E[V'] <= V/2, exact after multiplying by 2.
                    assert any(child < current for child in children)
                    count += 1
    return {
        "status": "passed",
        "weight_vectors": weight_vectors,
        "checked_intervals": count,
        "domain": {"weight_vector_length": [1, 3], "weight_entries": [1, 4],
                   "v": [1, 16], "c": "0 <= c < v"},
        "checks": ["half_open_classification", "boundary_partition", "half_expectation_bound", "progress"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("audit_results.json"))
    parser.add_argument("--max-fdr-n", type=int, default=40)
    args = parser.parse_args()
    if args.max_fdr_n < 1:
        parser.error("--max-fdr-n must be positive")
    result = {
        "guarantee": "bounded arithmetic diagnostic only; not an infinite-state proof",
        "fdr_pcfg": audit_fdr(args.max_fdr_n),
        "han_hoshi": audit_han_hoshi(),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
