#!/usr/bin/env python3
"""Regression checks and exact arithmetic audits (not a theorem mechanization)."""
import argparse
from dataclasses import replace
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import z3 as z
from engine import Loop, Region, check_input, verify_candidate, obligations, certificate, query, domain, rational
from examples import random_walk, fdr, fldr_fixed, fldr_abstract, fldr_tree


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return True
    raise AssertionError("Invalid input/certificate was accepted")


def symbolic_checks():
    walk=random_walk()
    biased=replace(walk,outcomes=((Fraction(1,3),walk.outcomes[0][1]),(Fraction(2,3),walk.outcomes[1][1])))
    bad=replace(walk,relation=lambda s,a:z.BoolVal(False))
    unknown=z.Int("undeclared")
    descriptor=z.Int("descriptor")
    overlap=replace(walk,regions=(Region("one",lambda s:s[0]>=0),Region("two",lambda s:s[0]>0)))
    incomplete=replace(walk,regions=(Region("only small",lambda s:s[0]<3),))
    undeclared=replace(walk,regions=(Region("bad",lambda s:unknown>=0),))
    descriptor_region=replace(walk,descriptors=(descriptor,),regions=(Region("bad",lambda s:descriptor>=0),))
    results={
        "constant_variant_refuted":expect_rejection(lambda:verify_candidate(walk,[[1,0]],[[0,1]])),
        "positive_drift_refuted":expect_rejection(lambda:verify_candidate(biased,[[1,0]],[[1,0]])),
        "vacuous_transition_contract_rejected":expect_rejection(lambda:check_input(bad,10000)),
        "overlapping_partition_rejected":expect_rejection(lambda:check_input(overlap,10000)),
        "incomplete_partition_rejected":expect_rejection(lambda:check_input(incomplete,10000)),
        "undeclared_partition_symbol_rejected":expect_rejection(lambda:check_input(undeclared,10000)),
        "descriptor_partition_rejected":expect_rejection(lambda:check_input(descriptor_region,10000)),
    }
    x=z.Int("signed_x")
    step=lambda s,a:(z.If(s[0]>0,1-s[0],-1-s[0]),)
    signed=Loop("signed_countdown",(x,),lambda s:z.BoolVal(True),lambda s:s[0]!=0,
                ((Fraction(1),step),),z.BoolVal(True),(x,),
                regions=(Region("negative",lambda s:s[0]<0),Region("nonnegative",lambda s:s[0]>=0)))
    results["cross_region_countdown_input"]=check_input(signed,10000)
    results["cross_region_countdown_abs_x"]=verify_candidate(signed,[[-1,0],[1,0]],[[-1,0],[1,0]])
    # This uses exact SMT arithmetic for every integer state, not sampled runs.
    f=fdr(); u=[[1,-1,1,0]]
    current=certificate(f,u,f.variables)
    expected=sum(rational(p)*certificate(f,u,update(f.variables,())) for p,update in f.outcomes)
    status,_=query(z.And(domain(f,f.variables,()),expected>current-rational(Fraction(1,2))),10000)
    assert status==z.unsat
    results["fdr_expected_U_decreases_by_half"]=str(status)
    abstract=fldr_abstract()
    results["abstract_alternative_V_k_U_k_minus_c"]=verify_candidate(
        abstract,[[0,1,0,0,0,0]],[[0,1,0,-1,0,0]])
    return results


def finite_fldr_audit():
    tree=fldr_tree((4,5)); active=set(tree["active"])
    value=lambda s:s[0]-2*s[1]+2 if s in active else 0
    rows=[]
    for state in tree["active"]:
        posts=tree["edges"][state]
        values=[value(s) for s in posts]
        mean=sum(Fraction(v,2) for v in values)
        assert value(state)>0 and mean<=value(state) and min(values)<=value(state)-1
        rows.append({"state":state,"W":value(state),"successors":posts,
                     "successor_values":values,"mean":str(mean)})
    # No uniformly negative drift: the root and (1,0) have equality.
    assert rows[0]["mean"]==str(rows[0]["W"])
    # The depth variant rises in expectation at (2,0).
    u=lambda s:4-s[0] if s in active else 0
    mean=sum(Fraction(u(s),2) for s in tree["edges"][(2,0)])
    assert mean==Fraction(5,2)>u((2,0))
    return {"weights":[4,5],"rows":rows,"depth_variant_at_2_0":{"U":2,"expected_next_U":str(mean)}}


def tree_regression():
    count=0; nodes=0
    for n in range(1,5):
        for weights in product(range(1,7),repeat=n):
            tree=fldr_tree(weights); k=tree["k"]
            active=set(tree["active"])
            masses={i:Fraction(0) for i in range(1,n+2)}
            for (c,d),label in tree["leaves"].items():
                masses[label]+=Fraction(1,2**c)
            for i,w in enumerate(weights,1):
                assert masses[i]==Fraction(w,2**k)
            assert masses[n+1]==Fraction(tree["rejection"],2**k)
            for (c,d),posts in tree["edges"].items():
                assert c<k and d>=0
                reject=0
                for bit,post in enumerate(posts):
                    raw=(c+1,2*d+bit)
                    label=tree["leaves"].get(raw)
                    if label==n+1:
                        assert post==(0,0)
                        reject+=1
                    elif raw in active:
                        assert post==raw and c+1<k
                    else:
                        assert label in range(1,n+1) and post==raw
                assert reject<=1
                nodes+=1
            # Includes terminal root cases (1,), (2,), (4,).
            for c,d in active | {s for s,l in tree["leaves"].items() if l!=n+1}:
                assert 0<=c<=k and 0<=d<2*n
            count+=1
    for weights in [(1,),(2,),(4,)]:
        loop=fldr_fixed(weights)
        check_input(loop,10000)
        assert z.is_true(z.simplify(z.Not(loop.guard((0,0)))))
    return {"weight_vectors_checked":count,"enabled_nodes_checked":nodes,
            "scope":"1..4 outcomes, each weight 1..6; finite regression, not universal preprocessing proof",
            "properties":["exact binary leaf masses", "abstract transition contract", "finite height", "d < 2n", "root-terminal cases"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("diagnostics.json"))
    args=parser.parse_args()
    results={"z3_version":z.get_version_string(),"symbolic":symbolic_checks(),
             "fldr_exact_rational_audit":finite_fldr_audit(),"tree_regression":tree_regression()}
    args.output.write_text(json.dumps(results,indent=2)+"\n")
    print("All symbolic rejection checks and exact-arithmetic diagnostics passed.")
    print(f"FLDR tree regression: {results['tree_regression']['weight_vectors_checked']} weight vectors.")

if __name__=="__main__":
    main()
