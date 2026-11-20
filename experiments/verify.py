"""Semantic checks, independent of any plotted result."""
import itertools
import numpy as np
from run_study import cw,matrix,scores,paired

checks=0
for bits in itertools.product([False,True],repeat=6):
    p=np.full((4,4),.5)
    for (i,j),v in zip(itertools.combinations(range(4),2),bits):p[i,j]=.8 if v else .2;p[j,i]=1-p[i,j]
    q=0
    for j in range(1,4):
        if p[q,j]<.5:q=j
    out=q if all(p[q,j]>.5 for j in range(4) if j!=q) else None
    assert out==cw(p);checks+=1
assert cw(matrix()) is None
assert int(scores(matrix()).argmax())==1
for s in range(5):
    a=paired(matrix(),s,batch=512)
    by={r['method']:r for r in a}
    assert by['Reuse']['additional_duels']<=by['Restart']['additional_duels']
    assert all(r['complete'] and r['correct'] for r in a)
    checks+=1
print(f'Passed {checks} semantic checks: all 64 four-arm tournaments and 5 paired stochastic runs.')
