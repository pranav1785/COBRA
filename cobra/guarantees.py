"""Analysis-only safeguard budget. Never used by the sampling policy.

nbar is the proof's sufficient designated-sample threshold, not an algorithm
input. J counts interior checkpoint cuts; terminal cap truncation is separate.
"""
def safeguard_budget(k,nbar,batch=128,shortened=0):
    if k<2 or nbar<1 or batch<1 or shortened<0:raise ValueError('Invalid analysis parameters')
    safe_blocks=(k*(nbar+batch)+batch-1)//batch+shortened
    total_blocks=4*((safe_blocks+2)//3)
    return dict(S0=safe_blocks,blocks=total_blocks,N0=batch*total_blocks)
