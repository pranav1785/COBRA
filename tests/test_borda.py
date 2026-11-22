import unittest,inspect
import numpy as np
from cobra.core import Learner,validate,scores,radius,certificate
from cobra.simulation import simulate,regret

class BordaTests(unittest.TestCase):
    def setUp(self):self.p=np.array([[.5,.51,.51],[.49,.5,.9],[.49,.1,.5]])
    def test_reciprocity_and_diagonal(self):
        validate(self.p)
        for bad in (np.eye(3),np.ones((3,2)),np.array([[.5,np.nan],[.5,.5]])):
            with self.assertRaises(ValueError):validate(bad)
    def test_scores_and_target(self):np.testing.assert_allclose(scores(self.p),[.51,.695,.295]);self.assertEqual(scores(self.p).argmax(),1)
    def test_updates_not_double_counted(self):
        l=Learner(3);l.update(0,1,10,7,True)
        self.assertEqual(l.n.sum(),20);self.assertEqual(l.w.sum(),10);self.assertEqual(l.c.sum(),10)
        self.assertEqual(l.w[1,0],3);self.assertEqual(l.dn[1,0],0)
    def test_radius(self):self.assertAlmostEqual(float(radius(10,3,.05)),np.sqrt(np.log(24000)/(20)))
    def test_pair_symmetry_unseen(self):
        l=Learner(3);l.update(0,1,1000,700);lo,hi=l.pair_bounds()
        np.testing.assert_allclose(lo,1-hi.T);self.assertEqual(lo[0,2],0);self.assertEqual(hi[0,2],1)
    def test_row_coverage(self):
        l=Learner(3)
        for i,j in ((0,1),(0,2),(1,2)):l.update(i,j,10000,int(10000*self.p[i,j]))
        lo,hi=l.score_bounds();b=scores(self.p);self.assertTrue(np.all(lo<=b)&np.all(b<=hi))
    def test_certificate(self):self.assertEqual(certificate(np.array([.7,.2]),np.array([.8,.3])),0);self.assertIsNone(certificate(np.array([.3,.3]),np.array([.8,.8])))
    def test_no_oracle_argument(self):
        self.assertNotIn('p',inspect.signature(Learner).parameters)
        self.assertNotIn('gap',inspect.signature(Learner).parameters)
        self.assertNotIn('scores(',inspect.getsource(Learner))
    def test_regret_and_self(self):self.assertAlmostEqual(regret(self.p,1,1),0);self.assertAlmostEqual(regret(self.p,0,2),.2925)
    def test_uniform_opponents(self):
        p=np.full((5,5),.5);r=simulate(p,'uniform',12,100000,batch=1000)
        n=np.array(r['counts']);self.assertLess(np.max(np.abs(n[np.triu_indices(5,1)]-10000)),700)
    def test_adaptive_no_self(self):
        l=Learner(3);l.block=3;_,i,j=l.select(np.random.default_rng(2));self.assertNotEqual(i,j)
    def test_reproducibility(self):
        a=simulate(self.p,'cobra',1,1000);b=simulate(self.p,'cobra',1,1000)
        for key in ('counts','trace','duels','estimate'):self.assertEqual(a[key],b[key])
    def test_tie_exhaustion(self):
        r=simulate(np.full((3,3),.5),'cobra',7,500);self.assertFalse(r['certified']);self.assertEqual(r['duels'],500)
    def test_matched_ablation(self):
        a=simulate(self.p,'cobra',2,256);b=simulate(self.p,'no_reuse',2,256);self.assertEqual(a['counts'],b['counts'])
    def test_two_arm_and_all_modes(self):
        for mode in ('fixed','uniform','cobra','random_pair','no_reuse','directional','pair_only'):
            r=simulate(np.array([[.5,.9],[.1,.5]]),mode,2,10000)
            self.assertTrue(r['correct'])
    def test_confidence_monotonicity(self):self.assertGreater(float(radius(1,3,.05)),float(radius(100,3,.05)))
    def test_invalid_feedback(self):
        l=Learner(2)
        with self.assertRaises(ValueError):l.update(0,0,1,1)
        with self.assertRaises(ValueError):l.update(0,1,1,2)

if __name__=='__main__':unittest.main()
