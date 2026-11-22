"""The uniform and fixed-budget baselines use cobra.core.Learner modes.

uniform: designated least-sampled arm, fresh uniform opponent, anytime stopping.
fixed: identical feedback and designation; return an uncertified estimate at cap.
"""
