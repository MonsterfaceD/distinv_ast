#!/usr/bin/env python3
"""Run all paper synthesis experiments with the same engine and settings."""
import argparse
import json
import platform
from pathlib import Path
from time import perf_counter
import z3 as z
from engine import synthesize, Inconclusive
from examples import base_examples, piecewise_examples, random_walk


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("results.json"))
    parser.add_argument("--suite",choices=("base","piecewise","all"),default="all")
    parser.add_argument("--bounds",type=int,nargs="+",default=[1,2,4,8,16])
    parser.add_argument("--timeout-ms",type=int,default=10000)
    parser.add_argument("--max-candidates",type=int,default=500)
    args=parser.parse_args()
    loops=(base_examples() if args.suite in ("base","all") else [])+(piecewise_examples() if args.suite in ("piecewise","all") else [])
    started=perf_counter()
    output={"z3_version":z.get_version_string(),"python_version":platform.python_version(),
            "method":"guarded full affine / supplied-partition affine integer CEGIS, U <= V",
            "timing_note":"wall-clock seconds in this run; not a benchmark", "examples":[]}
    failed=False
    for loop in loops:
        try:
            result=synthesize(loop,tuple(args.bounds),args.timeout_ms,args.max_candidates)
        except Inconclusive as exc:
            result={"name":loop.name,"status":"inconclusive","reason":str(exc)}
        output["examples"].append(result)
        print(f"{loop.name}: {result['status']}, candidates={len(result.get('trace',[]))}, bound={result.get('coefficient_bound')}",flush=True)
        failed |= result["status"] != "verified"
        args.output.write_text(json.dumps(output,indent=2)+"\n")
    # This only excludes bounded templates; the all-bounds impossibility proof
    # for the two-sided affine walk is mathematical, in Section 6.
    if args.suite=="all":
        output["negative_template_experiment"]=synthesize(random_walk(two_sided=True),tuple(args.bounds),args.timeout_ms,args.max_candidates)
    output["total_wall_seconds"]=perf_counter()-started
    args.output.write_text(json.dumps(output,indent=2)+"\n")
    if failed:
        raise SystemExit("At least one requested synthesis result is not verified; see JSON")

if __name__=="__main__":
    main()
