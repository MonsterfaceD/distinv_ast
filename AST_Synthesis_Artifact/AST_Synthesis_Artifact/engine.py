"""Shared finite-template CEGIS; all verification domains are unbounded.

Inputs are trusted executable encodings of one complete loop iteration.  The
solver checks their support and partition contracts, not source translation.
"""
from dataclasses import dataclass, field
from fractions import Fraction
from time import perf_counter
from typing import Callable
import z3 as z
from z3.z3util import get_vars


class Inconclusive(RuntimeError):
    """A solver returned no decision; context contains available partial checks."""

    def __init__(self, reason, **context):
        super().__init__(reason)
        self.context = context


@dataclass(frozen=True)
class Region:
    name: str
    predicate: Callable


@dataclass(frozen=True)
class Loop:
    name: str
    variables: tuple
    support: Callable
    guard: Callable
    outcomes: tuple  # (positive Fraction, update(state, descriptors))
    initial_condition: object
    initial_state: tuple
    descriptors: tuple = ()
    relation: Callable = lambda state, descriptors: z.BoolVal(True)
    regions: tuple = field(default_factory=lambda: (Region("active", lambda s: z.BoolVal(True)),))
    semantics: str = "exact, manually encoded complete body outcomes"

    @property
    def feature_indices(self):
        return tuple(i for i, x in enumerate(self.variables) if x.sort() == z.IntSort())


def rational(p):
    return z.RealVal(f"{p.numerator}/{p.denominator}")


def concrete(value):
    if z.is_true(value):
        return True
    if z.is_false(value):
        return False
    return value.as_long()


def query(condition, timeout_ms):
    solver = z.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(condition)
    status = solver.check()
    if status == z.unknown:
        raise Inconclusive(solver.reason_unknown())
    return status, solver


def domain(loop, state, descriptors):
    return z.And(loop.support(state), loop.guard(state), loop.relation(state, descriptors))


def certificate(loop, coefficients, state):
    terms = []
    for region, block in zip(loop.regions, coefficients):
        affine = sum(block[j] * state[i] for j, i in enumerate(loop.feature_indices)) + block[-1]
        terms.append(z.If(region.predicate(state), affine, 0))
    return z.If(loop.guard(state), sum(terms), 0)


def obligations(loop, vc, uc, state, descriptors=()):
    v, u = certificate(loop, vc, state), certificate(loop, uc, state)
    posts = [(p, update(state, descriptors)) for p, update in loop.outcomes]
    expected = sum(rational(p) * certificate(loop, vc, post) for p, post in posts)
    return {
        "V_positive": v >= 1,
        "U_positive": u >= 1,
        "U_le_V": u <= v,
        "supermartingale": expected <= v,
        "progress": z.Or(*(certificate(loop, uc, post) <= u - 1 for _, post in posts)),
    }


def check_input(loop, timeout_ms):
    weights = [p for p, _ in loop.outcomes]
    if not weights or any(not isinstance(p, Fraction) or p <= 0 for p in weights) or sum(weights) != 1:
        raise ValueError("Fixed positive rational outcome weights must sum to one")
    if not loop.regions:
        raise ValueError("Empty region list")
    declared = {x.get_id() for x in loop.variables}
    for region in loop.regions:
        expression = z.BoolVal(region.predicate(loop.variables)) if isinstance(region.predicate(loop.variables), bool) else region.predicate(loop.variables)
        if any(x.get_id() not in declared for x in get_vars(expression)):
            raise ValueError("Partition mentions an undeclared symbol or transition descriptor")
    state, descriptors = loop.variables, loop.descriptors
    enabled = z.And(loop.support(state), loop.guard(state))
    admitted = domain(loop, state, descriptors)
    coverage = loop.relation(state, descriptors)
    if descriptors:
        coverage = z.Exists(descriptors, coverage)
    checks = {
        "initialization": z.And(loop.initial_condition, z.Not(loop.support(loop.initial_state))),
        "transition_coverage": z.And(enabled, z.Not(coverage)),
        "partition_coverage": z.And(enabled, z.Not(z.Or(*(p.predicate(state) for p in loop.regions)))),
    }
    for i, region in enumerate(loop.regions):
        for j, other in enumerate(loop.regions[:i]):
            checks[f"partition_disjoint_{j}_{i}"] = z.And(enabled, region.predicate(state), other.predicate(state))
    for i, (_, update) in enumerate(loop.outcomes):
        checks[f"support_preservation_{i}"] = z.And(admitted, z.Not(loop.support(update(state, descriptors))))
    results = {}
    for name, condition in checks.items():
        try:
            status, solver = query(condition, timeout_ms)
        except Inconclusive as exc:
            exc.context.update(phase="input_validation", check=name,
                               input_checks=dict(results))
            raise
        results[name] = str(status)
        if status != z.unsat:
            raise ValueError(f"Invalid input {loop.name}: {name}; counterexample {solver.model()}")
    return results


def verify_candidate(loop, vc, uc, timeout_ms=10000):
    dimension = len(loop.feature_indices) + 1
    if any(len(c) != len(loop.regions) or any(len(b) != dimension for b in c) for c in (vc, uc)):
        raise ValueError("Wrong certificate coefficient dimensions")
    if any(not isinstance(a, int) or isinstance(a, bool) for c in (vc, uc) for b in c for a in b):
        raise ValueError("Integer coefficients required")
    results = {}
    for name, condition in obligations(loop, vc, uc, loop.variables, loop.descriptors).items():
        try:
            status, solver = query(z.And(domain(loop, loop.variables, loop.descriptors), z.Not(condition)), timeout_ms)
        except Inconclusive as exc:
            exc.context.update(phase="certificate_recheck", check=name,
                               certificate_checks=dict(results))
            raise
        results[name] = str(status)
        if status != z.unsat:
            raise ValueError(f"Invalid certificate {loop.name}: {name}; counterexample {solver.model()}")
    return results


def synthesize(loop, bounds=(1, 2, 4, 8, 16), timeout_ms=10000, max_candidates=500):
    started = perf_counter()
    state, descriptors = loop.variables, loop.descriptors
    samples, trace, attempts = [], [], []
    data = {
        "name": loop.name, "semantics": loop.semantics,
        "state_order": [str(x) for x in state],
        "descriptor_order": [str(x) for x in descriptors],
        "coefficient_order": [str(state[i]) for i in loop.feature_indices] + ["constant"],
        "regions": [p.name for p in loop.regions], "input_checks": {},
        "bounds": list(bounds), "timeout_ms": timeout_ms, "max_candidates": max_candidates,
        "samples": samples, "trace": trace, "bound_attempts": attempts,
        "phase": "input_validation", "current_bound": None,
    }

    def finish(status, **extra):
        return dict(data, status=status, wall_seconds=perf_counter()-started, **extra)

    def sample_from(model):
        return {"state": tuple(concrete(model.eval(x, model_completion=True)) for x in state),
                "descriptors": tuple(concrete(model.eval(x, model_completion=True)) for x in descriptors)}

    try:
        data["input_checks"] = check_input(loop, timeout_ms)
        data["epsilon"] = str(min(p for p, _ in loop.outcomes))
        enabled = domain(loop, state, descriptors)
        data["phase"] = "seed_selection"
        status, seed_solver = query(enabled, timeout_ms)
        if status == z.unsat:
            return finish("no_enabled_states")
        samples.append(sample_from(seed_solver.model()))
        dimension = len(loop.feature_indices) + 1
        vc = [[z.Int(f"{loop.name}_V_{j}_{i}") for i in range(dimension)] for j in range(len(loop.regions))]
        uc = [[z.Int(f"{loop.name}_U_{j}_{i}") for i in range(dimension)] for j in range(len(loop.regions))]
        coefficients = [a for c in (vc, uc) for block in c for a in block]
        for bound in bounds:
            if bound < 0:
                raise ValueError("Coefficient bounds must be nonnegative")
            data["current_bound"] = bound
            learner = z.Optimize()
            learner.set(timeout=timeout_ms)
            learner.add(*(z.And(a >= -bound, a <= bound) for a in coefficients))
            learner.minimize(sum(z.If(a >= 0, a, -a) for a in coefficients))
            for sample in samples:
                learner.add(*obligations(loop, vc, uc, sample["state"], sample["descriptors"]).values())
            attempt = {"bound": bound, "candidates": 0}
            attempts.append(attempt)
            while len(trace) < max_candidates:
                data["phase"] = "learner"
                outcome = learner.check()
                if outcome == z.unsat:
                    attempt["status"] = "no_certificate_in_bounded_template"
                    break
                if outcome != z.sat:
                    raise Inconclusive(learner.reason_unknown())
                model = learner.model()
                va = [[model.eval(a).as_long() for a in block] for block in vc]
                ua = [[model.eval(a).as_long() for a in block] for block in uc]
                entry = {"candidate": len(trace)+1, "bound": bound,
                         "V_coefficients": va, "U_coefficients": ua, "result": "pending"}
                attempt["candidates"] += 1
                trace.append(entry)
                conditions = obligations(loop, va, ua, state, descriptors)
                data["phase"] = "verifier"
                status, verifier = query(z.And(enabled, z.Not(z.And(*conditions.values()))), timeout_ms)
                if status == z.unsat:
                    # A successful combined query does not bypass the individual rechecks.
                    data["phase"] = "certificate_recheck"
                    checks = verify_candidate(loop, va, ua, timeout_ms)
                    entry["result"] = "verified"
                    attempt["status"] = "verified"
                    return finish("verified", coefficient_bound=bound,
                                  V_coefficients=va, U_coefficients=ua,
                                  certificate_checks=checks)
                model = verifier.model()
                sample = sample_from(model)
                entry.update(result="counterexample", counterexample=sample,
                             violations=[name for name, condition in conditions.items() if z.is_false(model.eval(condition, model_completion=True))])
                samples.append(sample)
                learner.add(*obligations(loop, vc, uc, sample["state"], sample["descriptors"]).values())
            else:
                data["phase"] = "candidate_limit"
                attempt["status"] = "candidate_limit_inconclusive"
                return finish("candidate_limit_inconclusive", reason="Maximum candidate count reached")
        return finish("no_certificate_in_bounded_template")
    except Inconclusive as exc:
        data.update(exc.context)
        if attempts:
            attempts[-1]["status"] = "inconclusive"
        if trace and trace[-1]["result"] == "pending":
            trace[-1]["result"] = "inconclusive"
        return finish("inconclusive", reason=str(exc))
