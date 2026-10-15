"""Manually supplied semantics, invariants, and optional fixed partitions."""
from dataclasses import replace
from fractions import Fraction
import z3 as z
from engine import Loop, Region

HALF = Fraction(1, 2)


def random_walk(two_sided=False, piecewise=False):
    x = z.Int("x")
    loop = Loop("walk_two_sided" if two_sided else "random_walk", (x,),
        support=lambda s: z.BoolVal(True) if two_sided else s[0] >= 0,
        guard=lambda s: s[0] != 0 if two_sided else s[0] > 0,
        outcomes=((HALF, lambda s, a: (s[0]-1,)), (HALF, lambda s, a: (s[0]+1,))),
        initial_condition=z.BoolVal(True) if two_sided else x >= 0, initial_state=(x,))
    if piecewise:
        loop = replace(loop, name=loop.name+"_piecewise", regions=(
            Region("x < 0", lambda s: s[0] < 0), Region("x >= 0", lambda s: s[0] >= 0)))
    return loop


def fdr(piecewise=False):
    n, v, c = z.Ints("n v c")
    def update(s, bit):
        nn, vv, cc = s
        reject = 2*cc+bit >= nn
        return nn, z.If(reject, 2*vv-nn, 2*vv), z.If(reject, 2*cc+bit-nn, 2*cc+bit)
    loop = Loop("fdr_symbolic", (n,v,c),
        support=lambda s: z.And(s[0]>=1, s[1]>=1, s[1]<2*s[0], s[2]>=0, s[2]<s[1], s[2]<s[0]),
        guard=lambda s: s[1]<s[0],
        outcomes=tuple((HALF, lambda s, a, bit=bit: update(s,bit)) for bit in (0,1)),
        initial_condition=n>=1, initial_state=(n,1,0))
    if piecewise:
        loop = replace(loop, name=loop.name+"_piecewise", regions=(
            Region("2v < n", lambda s: 2*s[1]<s[0]), Region("2v >= n", lambda s: 2*s[1]>=s[0])))
    return loop


def fldr_tree(weights=(4,5)):
    """Exact finite decision tree: internal nodes first, leaf labels descending.

    Label len(weights)+1 rejects and resets. Bits encode leaf multiplicities
    at depth c with denominator 2**c. No floating-point logarithm is used.
    """
    if not weights or any(not isinstance(w,int) or w<=0 for w in weights):
        raise ValueError("Positive integer weights required")
    m, n = sum(weights), len(weights)
    k = (m-1).bit_length()
    rejection = 2**k-m
    if n == 1 and m == 2**k:
        return {"weights": list(weights), "m":m, "k":k, "n":n, "rejection":rejection,
                "active": [], "leaves": {(0,0):1}, "edges": {}}
    all_weights = list(weights)+[rejection]
    active = [(0,0)]
    leaves, edges = {}, {}
    internal_count = 1
    for c in range(1,k+1):
        labels = [i+1 for i in reversed(range(n+1)) if (all_weights[i] >> (k-c)) & 1]
        next_count = 2*internal_count-len(labels)
        if next_count < 0:
            raise ValueError("Invalid binary leaf counts")
        for d in range(next_count):
            active.append((c,d))
        for j,label in enumerate(labels):
            leaves[(c,next_count+j)] = label
        for d in range(internal_count):
            posts=[]
            for bit in (0,1):
                child=(c,2*d+bit)
                posts.append((0,0) if leaves.get(child)==n+1 else child)
            edges[(c-1,d)] = tuple(posts)
        internal_count=next_count
    assert internal_count == 0
    return {"weights":list(weights), "m":m, "k":k, "n":n, "rejection":rejection,
            "active":active, "leaves":leaves, "edges":edges}


def fldr_fixed(weights=(4,5), piecewise=False):
    tree=fldr_tree(weights)
    c,d=z.Ints("c d")
    active, edges=tree["active"],tree["edges"]
    valid=set(active) | set(tree["leaves"])
    # Raw rejecting leaves are intermediate body states; exclude from loop heads.
    valid={s for s in valid if tree["leaves"].get(s)!=tree["n"]+1}
    def member(s,nodes):
        return z.Or(*(z.And(s[0]==a,s[1]==b) for a,b in sorted(nodes)))
    def update(s,bit):
        result=(s[0],s[1])
        for node, posts in sorted(edges.items()):
            test=z.And(s[0]==node[0],s[1]==node[1])
            result=tuple(z.If(test,posts[bit][i],result[i]) for i in (0,1))
        return result
    loop=Loop("fldr_fixed_"+"_".join(map(str,weights)), (c,d),
        support=lambda s: member(s,valid), guard=lambda s: member(s,active),
        outcomes=tuple((HALF,lambda s,a,bit=bit:update(s,bit)) for bit in (0,1)),
        initial_condition=z.BoolVal(True), initial_state=(0,0))
    if piecewise:
        threshold=tree["k"]-1
        loop=replace(loop,name=loop.name+"_piecewise",regions=(
            Region(f"c < {threshold}",lambda s:s[0]<threshold),Region(f"c >= {threshold}",lambda s:s[0]>=threshold)))
    return loop


def fldr_abstract(piecewise=False):
    m,k,n,c,d=z.Ints("m k n c d")
    active=z.Bool("active")
    t0,t1=z.Ints("type0 type1") # 0 continue; 1 reset; 2 accept
    def support(s):
        mm,kk,nn,cc,dd,aa=s
        return z.And(mm>=1,kk>=0,kk<=mm,nn>=1,nn<=mm,cc>=0,cc<=kk,dd>=0,z.Implies(aa,cc<kk))
    def relation(s,a):
        return z.And(*(z.And(t>=0,t<=2,z.Implies(t==0,s[3]+1<s[1])) for t in a),z.Not(z.And(a[0]==1,a[1]==1)))
    def update(s,a,bit):
        mm,kk,nn,cc,dd,aa=s
        t=a[bit]
        return mm,kk,nn,z.If(t==1,0,cc+1),z.If(t==1,0,2*dd+bit),t!=2
    loop=Loop("fldr_abstract",(m,k,n,c,d,active),support=support,guard=lambda s:s[5],
        outcomes=tuple((HALF,lambda s,a,bit=bit:update(s,a,bit)) for bit in (0,1)),
        initial_condition=z.And(m>=1,k>=0,k<=m,n>=1,n<=m,z.Implies(active,k>0)),initial_state=(m,k,n,0,0,active),
        descriptors=(t0,t1),relation=relation,
        semantics="overapproximation: finite height k; at most one rejecting child; concrete coverage argued mathematically")
    if piecewise:
        loop=replace(loop,name=loop.name+"_piecewise",regions=(
            Region("c < k-1",lambda s:s[3]<s[1]-1),Region("c >= k-1",lambda s:s[3]>=s[1]-1)))
    return loop


def base_examples():
    return [random_walk(),fdr(),fldr_fixed(),fldr_abstract()]


def piecewise_examples():
    return [random_walk(two_sided=True,piecewise=True),fdr(piecewise=True),
            fldr_fixed(piecewise=True),fldr_abstract(piecewise=True)]
