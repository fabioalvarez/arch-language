"""[D4] Justification of the tactics of iteration 4 (Delivery 4, section 6).

Reads ncs-e2.arch and ncs-e4.arch and runs, with the simulators of simulation.py:
  1. the contribution of each tactic to P1 (D-QS1): e2, e2 + T-R1, e2 + T-R2 and e4,
     40 replications x 20 years, and the Lab 3 formula as known result;
  2. the sensitivity of P1 to the common-cause fraction beta in e4 (section 7.3);
  3. the alternative to T-R3 that was discarded: CAR with 14 and 15 instances of 4.5 events/s.

Usage: python tactics_check.py      (writes out/tactics/tactics.md)
"""
import os
import random

from metamodel import create_metamodel
from simulation import (_downs, _intersect, _union, analytic_availability,
                        availability_factors, interval, outcome_at_least, run_scenario)

THRESHOLD, MARGIN, MTTR, YEARS, REPS = 99.9, 0.02, 4.0, 20, 40


def simulate(factors, seed):
    """Monte Carlo of simulation.simulate_availability, on a list of (A %, n, beta)."""
    horizon, rng, values = YEARS * 8760.0, random.Random(seed), []
    for _ in range(REPS):
        downs = []
        for av, n, b in factors:
            u = 1 - av / 100.0
            lam = u / ((1 - u) * MTTR)
            if n == 1:
                downs += _downs(rng, lam, MTTR, horizon)
                continue
            both = _downs(rng, (1 - b) * lam, MTTR, horizon)
            for _ in range(n - 1):
                both = _intersect(both, _downs(rng, (1 - b) * lam, MTTR, horizon))
            downs += both + _downs(rng, b * lam, MTTR, horizon)
        values.append(100.0 * (1 - _union(downs) / horizon))
    mean, low, high = interval(values)
    return mean, low, high, analytic_availability(factors), outcome_at_least(low, high, THRESHOLD, MARGIN)


def with_beta(factors, beta):
    return [(a, n, beta if n > 1 else b) for a, n, b in factors]


def main():
    mm = create_metamodel()
    e2 = mm.model_from_file('models/ncs-e2.arch')
    e4 = mm.model_from_file('models/ncs-e4.arch')
    a2 = {a.name: a for a in e2.analyses}['DQS1Balancers']     # chain with its 4 balancers
    a4 = {a.name: a for a in e4.analyses}['DQS1']
    f2, f4 = availability_factors(a2), availability_factors(a4)

    lines = ['# Tactics of iteration 4', '',
             f'Monte Carlo: {REPS} replications x {YEARS} years, MTTR {MTTR} h.', '',
             '## 1. Contribution of each tactic to P1 (D-QS1)', '',
             '| Structure | Estimate | 95 % CI | Known (Lab 3) | Outcome |', '|---|---|---|---|---|']
    # seeds 1001 and 1000 reproduce the rows of out/ncs-e2 and out/ncs-e4 (verification.py)
    variants = [('e2: balancers single, beta 0.10', f2, 1001),
                ('e2 + T-R1 (balancers in pairs, beta 0.10)', with_beta(f4, 0.10), 1000),
                ('e2 + T-R2 (beta 0.05, balancers single)', with_beta(f2, 0.05), 1000),
                ('e4: T-R1 + T-R2', f4, 1000)]
    for name, f, seed in variants:
        m, lo, hi, exact, res = simulate(f, seed)
        lines.append(f'| {name} (seed {seed}) | {m:.3f} % | [{lo:.3f}, {hi:.3f}] | {exact:.3f} % | {res} |')

    lines += ['', '## 2. Sensitivity of P1 to beta (e4)', '',
              '| beta | Seed | Estimate | 95 % CI | Known (Lab 3) | Outcome |', '|---|---|---|---|---|---|']
    for i, beta in enumerate([0.0, 0.02, 0.05, 0.08, 0.09, 0.10, 0.11, 0.12, 0.15]):
        m, lo, hi, exact, res = simulate(with_beta(f4, beta), 1200 + i)
        lines.append(f'| {beta:.2f} | {1200 + i} | {m:.3f} % | [{lo:.3f}, {hi:.3f}] | {exact:.3f} % | {res} |')

    lines += ['', '## 3. Discarded alternative to T-R3: more instances of CAR at 4.5 events/s', '',
              '| Instances | Recovery (s) | 95 % CI | Outcome |', '|---|---|---|---|']
    car = next(c for c in e4.elements if getattr(c, 'name', '') == 'CAR')
    qs10 = next(s for s in e4.scenarios if s.name == 'QS_D10')
    qs10.vary.values = [4.5]
    for n in (14, 15):
        car.instances = n
        for value, m, mean, lo, hi, res in run_scenario(qs10):
            if m.metric == 'recovery' and m.workload is None:
                lines.append(f'| {n} | {mean:.1f} | [{lo:.1f}, {hi:.1f}] | {res} |')

    os.makedirs('out/tactics', exist_ok=True)
    with open('out/tactics/tactics.md', 'w') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
