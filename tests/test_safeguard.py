import math,unittest
import numpy as np
from cobra.core import Learner,certificate
from cobra.simulation import simulate
from cobra.guarantees import safeguard_budget

class SafeguardTests(unittest.TestCase):
    def test_actual_schedule_with_checkpoint_cuts(self):
        r=simulate(np.full((5,5),.5),'cobra',17,401,1e-12,32,[17,51,100],audit=True)
        self.assertFalse(r['certified']);self.assertEqual(sum(x['length'] for x in r['blocks']),401)
        for q,x in enumerate(r['blocks']):
            self.assertEqual(x['index'],q);self.assertEqual(x['action'],'pair' if q%4==3 else 'safe')
            self.assertLessEqual(max(x['direct_counts'])-min(x['direct_counts']),32)
        interior=[x for x in r['blocks'] if x['length']<32 and x['start']+x['length']<401]
        self.assertEqual(len(interior),3)
        self.assertEqual(sum(x['length'] for x in r['blocks'] if x['action']=='safe'),sum(r['blocks'][-1]['direct_counts']))
    def test_N0_covers_safe_counts_even_with_short_blocks(self):
        rng=np.random.default_rng(901)
        for k in (2,3,5,10):
            for b in (1,7,32):
                for nbar in (1,8,65):
                    for j in (0,1,3):
                        bound=safeguard_budget(k,nbar,b,j);l=Learner(k);total=0
                        cut=set(rng.choice(bound['blocks'],min(j,bound['blocks']),replace=False).tolist())
                        for q in range(bound['blocks']):
                            l.block=q;action,i,v=l.select(rng);n=1 if q in cut else b;total+=n
                            if action=='safe':v=(i+1)%k
                            l.update(i,v,n,n//2,action=='safe')
                        self.assertGreaterEqual(int(l.c.min()),nbar);self.assertLessEqual(total,bound['N0'])
    def test_paper_interval_intersection_exactly_matches_code(self):
        l=Learner(3,delta=.05)
        for i,j,n,w in ((0,1,5000,3500),(0,2,5000,4000),(1,2,5000,3000)):l.update(i,j,n,w,True)
        direct=[]
        for i in range(3):
            if not l.c[i]:direct.append((0.,1.));continue
            r=math.sqrt(math.log(4*3*l.c[i]**2/(.05/2))/(2*l.c[i]));m=l.s[i]/l.c[i];direct.append((max(0,m-r),min(1,m+r)))
        pl=np.full((3,3),.5);pu=pl.copy()
        for i in range(3):
            for j in range(3):
                if i==j:continue
                n=l.n[i,j];r=math.sqrt(math.log(4*3*n**2/(.05/2))/(2*n));m=l.w[i,j]/n;pl[i,j]=max(0,m-r);pu[i,j]=min(1,m+r)
        lo=np.maximum(np.array(direct)[:,0],(pl.sum(1)-.5)/2);hi=np.minimum(np.array(direct)[:,1],(pu.sum(1)-.5)/2)
        a,b=l.score_bounds();np.testing.assert_allclose(a,lo);np.testing.assert_allclose(b,hi)
        self.assertEqual(certificate(a,b),certificate(lo,hi))
    def test_weight_default_and_validation(self):
        p=np.array([[.5,.8,.9],[.2,.5,.6],[.1,.4,.5]])
        a=simulate(p,'cobra',1,5000);b=simulate(p,'cobra',1,5000,leader_weight=2)
        for key in ('counts','duels','trace'):self.assertEqual(a[key],b[key])
        for w in (0,-1,float('nan')):
            with self.assertRaises(ValueError):Learner(3,leader_weight=w)

if __name__=='__main__':unittest.main()
