#!/usr/bin/env python3
"""Synthesize guarded affine AST certificates for two integer-state loops.

Run: python3 synthesis_examples.py --output results.json
Dependency: z3-solver (the exact version is recorded in the output).

The shared CEGIS engine takes manually encoded loop semantics and a supplied
inductive state predicate. It does not infer these predicates or parse programs.
V and U have independent integer affine templates, set to zero off the guard.
The finite coefficient range defaults to [-2, 2]. The sufficient condition
U <= V replaces the proof rule's more general sublevel-boundedness obligation.
All final verification queries range over UNBOUNDED integer program states.
UNSAT is accepted; SAT refutes the candidate; UNKNOWN is inconclusive.
"""

import argparse
from dataclasses import dataclass, replace
from fractions import Fraction
import json
from pathlib import Path
from typing import Callable

import z3 as z


@dataclass
class Loop:
    name: str
    variables: tuple
    support: Callable
    guard: Callable
    outcomes: tuple  # (positive Fraction, total deterministic state update)
    initial_condition: object
    initial_state: tuple
    seed: tuple


def rational(value):
    return z.RealVal(f"{value.numerator}/{value.denominator}")


def affine_certificate(loop, coefficients, state):
    affine = sum(a * x for a, x in zip(coefficients[:-1], state)) + coefficients[-1]
    return z.If(loop.guard(state), affine, 0)


def obligations(loop, vc, uc, state):
    value_v = affine_certificate(loop, vc, state)
    value_u = affine_certificate(loop, uc, state)
    next_states = [(p, update(state)) for p, update in loop.outcomes]
    expected_v = sum(
        rational(p) * affine_certificate(loop, vc, post)
        for p, post in next_states
    )
    # One strictly decreasing positive-probability outcome suffices: the minimum
    # fixed outcome weight is a uniform, state-independent lower bound epsilon.
    progress = z.Or(*[
        affine_certificate(loop, uc, post) <= value_u - 1
        for _, post in next_states
    ])
    return {
        "V_positive": value_v >= 1,
        "U_positive": value_u >= 1,
        "sublevel_bound_U_le_V": value_u <= value_v,
        "supermartingale": expected_v <= value_v,
        "progress": progress,
    }


def counterexample_query(condition, timeout_ms):
    solver = z.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(condition)
    result = solver.check()
    if result == z.unknown:
        raise RuntimeError(f"Inconclusive SMT result: {solver.reason_unknown()}")
    return result, solver


def verify_support(loop, timeout_ms):
    checks = {}
    queries = {
        "initialization": z.And(loop.initial_condition, z.Not(loop.support(loop.initial_state))),
    }
    state = loop.variables
    enabled = z.And(loop.support(state), loop.guard(state))
    for i, (_, update) in enumerate(loop.outcomes):
        queries[f"support_preservation_outcome_{i}"] = z.And(
            enabled, z.Not(loop.support(update(state)))
        )
    for name, query in queries.items():
        status, _ = counterexample_query(query, timeout_ms)
        checks[name] = str(status)
        if status != z.unsat:
            raise RuntimeError(f"Invalid supplied support: {loop.name}: {name}")
    return checks


def verify_candidate(loop, vc, uc, timeout_ms):
    state = loop.variables
    enabled = z.And(loop.support(state), loop.guard(state))
    checks = {}
    for name, condition in obligations(loop, vc, uc, state).items():
        status, _ = counterexample_query(z.And(enabled, z.Not(condition)), timeout_ms)
        checks[name] = str(status)
        if status != z.unsat:
            raise RuntimeError(f"Invalid candidate: {loop.name}: {name}")
    return checks


def synthesize(loop, coefficient_bound=2, timeout_ms=10000, max_iterations=200):
    weights = [p for p, _ in loop.outcomes]
    if not weights or any(p <= 0 for p in weights) or sum(weights) != 1:
        raise ValueError("Outcomes must have fixed positive rational weights summing to one")
    support_checks = verify_support(loop, timeout_ms)
    state = loop.variables
    dimension = len(state) + 1
    vc = [z.Int(f"{loop.name}_V_{i}") for i in range(dimension)]
    uc = [z.Int(f"{loop.name}_U_{i}") for i in range(dimension)]
    learner = z.Optimize()
    learner.set(timeout=timeout_ms)
    for a in vc + uc:
        learner.add(a >= -coefficient_bound, a <= coefficient_bound)
    learner.minimize(sum(z.If(a >= 0, a, -a) for a in vc + uc))

    enabled = z.And(loop.support(state), loop.guard(state))
    samples = [loop.seed]
    trace = []
    for iteration in range(1, max_iterations + 1):
        sample = samples[-1]
        # A counterexample must belong to the prescribed enabled state domain.
        status, _ = counterexample_query(z.Not(z.And(loop.support(sample), loop.guard(sample))), timeout_ms)
        if status != z.unsat:
            raise RuntimeError("Invalid seed or counterexample state")
        learner.add(*obligations(loop, vc, uc, sample).values())
        result = learner.check()
        if result == z.unsat:
            return {"name": loop.name, "status": "no_certificate_in_finite_template", "trace": trace}
        if result != z.sat:
            raise RuntimeError(f"Template search inconclusive: {learner.reason_unknown()}")
        model = learner.model()
        va = [model.eval(a).as_long() for a in vc]
        ua = [model.eval(a).as_long() for a in uc]
        conditions = obligations(loop, va, ua, state)
        result, verifier = counterexample_query(
            z.And(enabled, z.Not(z.And(*conditions.values()))), timeout_ms
        )
        entry = {"iteration": iteration, "V_coefficients": va, "U_coefficients": ua}
        if result == z.unsat:
            entry["result"] = "verified"
            trace.append(entry)
            checks = verify_candidate(loop, va, ua, timeout_ms)
            return {
                "name": loop.name,
                "status": "verified",
                "state_order": [str(x) for x in state],
                "coefficient_order": [str(x) for x in state] + ["constant"],
                "coefficient_bound": coefficient_bound,
                "V_coefficients": va,
                "U_coefficients": ua,
                "epsilon": str(min(weights)),
                "samples": samples,
                "trace": trace,
                "support_checks": support_checks,
                "certificate_checks": checks,
                "domain": "all integer states satisfying the supplied support and loop guard",
            }
        model = verifier.model()
        sample = tuple(model.eval(x).as_long() for x in state)
        entry.update({
            "result": "counterexample",
            "state": sample,
            "violations": [name for name, cond in conditions.items() if z.is_false(model.eval(cond))],
        })
        trace.append(entry)
        samples.append(sample)
    return {"name": loop.name, "status": "iteration_limit_inconclusive", "trace": trace}


def random_walk():
    x = z.Int("x")
    return Loop(
        "random_walk", (x,),
        support=lambda s: s[0] >= 0,
        guard=lambda s: s[0] > 0,
        outcomes=((Fraction(1, 2), lambda s: (s[0] - 1,)),
                  (Fraction(1, 2), lambda s: (s[0] + 1,))),
        initial_condition=x >= 0, initial_state=(x,), seed=(1,),
    )


def fdr():
    n, v, c = z.Ints("n v c")

    def support(s):
        nn, vv, cc = s
        return z.And(nn >= 1, vv >= 1, vv < 2 * nn, cc >= 0, cc < vv, cc < nn)

    def update(s, bit):
        nn, vv, cc = s
        doubled_v, doubled_c = 2 * vv, 2 * cc + bit
        reject = doubled_c >= nn
        return (nn, z.If(reject, doubled_v - nn, doubled_v),
                z.If(reject, doubled_c - nn, doubled_c))

    return Loop(
        "fdr", (n, v, c), support=support, guard=lambda s: s[1] < s[0],
        outcomes=((Fraction(1, 2), lambda s: update(s, 0)),
                  (Fraction(1, 2), lambda s: update(s, 1))),
        initial_condition=n >= 1, initial_state=(n, 1, 0), seed=(2, 1, 0),
    )


def sanity_checks(timeout_ms):
    """Ensure the verifier rejects two specific invalid certificates."""
    walk = random_walk()
    state = walk.variables
    enabled = z.And(walk.support(state), walk.guard(state))
    # A constant positive U fails progress away from the terminating boundary.
    conditions = obligations(walk, [1, 0], [0, 1], state)
    status, _ = counterexample_query(z.And(enabled, z.Not(conditions["progress"])), timeout_ms)
    if status != z.sat:
        raise RuntimeError("Sanity check failed: constant U must be refuted")
    # V=x is not a supermartingale for a walk biased away from zero.
    biased = replace(walk, outcomes=(
        (Fraction(1, 3), walk.outcomes[0][1]),
        (Fraction(2, 3), walk.outcomes[1][1]),
    ))
    conditions = obligations(biased, [1, 0], [1, 0], state)
    status, _ = counterexample_query(z.And(enabled, z.Not(conditions["supermartingale"])), timeout_ms)
    if status != z.sat:
        raise RuntimeError("Sanity check failed: positive drift must be refuted")
    return {"constant_variant_refuted": True, "positive_drift_refuted": True}


def fdr_drift_diagnostic(timeout_ms):
    """FDR is a baseline: its synthesized U is itself a ranking supermartingale."""
    loop = fdr()
    state = loop.variables
    uc = [1, -1, 1, 0]
    u = affine_certificate(loop, uc, state)
    expected_u = sum(rational(p) * affine_certificate(loop, uc, update(state))
                     for p, update in loop.outcomes)
    status, _ = counterexample_query(z.And(
        loop.support(state), loop.guard(state), expected_u > u - rational(Fraction(1, 2))
    ), timeout_ms)
    if status != z.unsat:
        raise RuntimeError("FDR drift diagnostic was not established")
    return {"E_U_next_le_U_minus_half_counterexample_query": str(status)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    results = {
        "z3_version": z.get_version_string(),
        "method": "CEGIS with guarded affine integer templates and U <= V",
        "examples": [synthesize(random_walk()), synthesize(fdr())],
        "sanity_checks": sanity_checks(10000),
        "additional_diagnostics": {"fdr_ranking_supermartingale": fdr_drift_diagnostic(10000)},
    }
    # Independent checks of the readable certificates used in the write-up.
    results["presented_certificates"] = {
        "random_walk_V_x_U_x": verify_candidate(random_walk(), [1, 0], [1, 0], 10000),
        "fdr_V_n_U_n_minus_v_plus_c": verify_candidate(fdr(), [1, 0, 0, 0], [1, -1, 1, 0], 10000),
    }
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))
    if any(e["status"] != "verified" for e in results["examples"]):
        raise SystemExit("One or more synthesis runs did not finish with a verified certificate")


if __name__ == "__main__":
    main()
