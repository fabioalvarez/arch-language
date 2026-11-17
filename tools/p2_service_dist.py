"""Run e4 P2 (QS_D10) under SERVICE_DIST variants and write a comparison table.

Usage: python tools/p2_service_dist.py
Writes: out/ncs-e4/p2-service-dist.md
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metamodel import create_metamodel
import simulation as sim

LOGNORMAL_SIGMA = 0.5
POINTS = [40.0, 32.1]
DISTS = ['exponential', 'deterministic', 'lognormal']


def run_point(scenario, value, dist):
    sim.SERVICE_DIST = dist
    sim.SERVICE_DIST_SIGMA = LOGNORMAL_SIGMA
    rates = {w.name: w.rate for w in scenario.workloads}
    caps = {c.name: sim.capacity_of(c)
            for w in scenario.workloads for c in w.path if sim.capacity_of(c)}
    caps[scenario.vary.target.name] = value * (scenario.vary.target.instances or 1)
    measure = next(m for m in scenario.measures
                   if m.metric == 'recovery' and m.workload is None)
    samples = []
    for seed in range(1, scenario.replications + 1):
        jobs, recovered = sim.simulate(scenario, seed, rates, caps)
        samples.append(sim._measure(measure, scenario, jobs, recovered))
    mean, low, high = sim.interval(samples)
    return mean, low, high, sim.outcome(low, high, measure.threshold)


def fmt(x):
    return f'{x:.1f}'


def main():
    mm = create_metamodel()
    model = mm.model_from_file('models/ncs-e4.arch')
    scenario = next(s for s in model.scenarios if s.name == 'QS_D10')
    rows = {(dist, value): run_point(scenario, value, dist)
            for dist in DISTS for value in POINTS}

    lines = [
        '# P2 — sensibilidad a la distribución de servicio (e4)',
        '',
        'Model: `models/ncs-e4.arch`, scenario `QS_D10`, seeds 1–10.',
        'Service mean fixed at `1/mu`. Lognormal: σ = 0.5,',
        '`mu_ln = ln(1/mu) - σ²/2`.',
        '',
        '## CAR = 40 ev/s/instancia (punto de diseño / T-R3)',
        '',
        '| Distribución | Estimación (recovery) | IC 95 % | Umbral | Outcome |',
        '|--------------|-----------------------|---------|--------|---------|',
    ]
    labels = {
        'exponential': 'exponential',
        'deterministic': 'deterministic',
        'lognormal': 'lognormal (σ=0.5)',
    }
    for dist in DISTS:
        mean, low, high, out = rows[(dist, 40.0)]
        lines.append(
            f'| {labels[dist]} | {fmt(mean)} s | [{fmt(low)}, {fmt(high)}] | '
            f'≤ 230 s | {out} |'
        )
    lines += [
        '',
        '## CAR = 32.1 (punto crítico, opcional)',
        '',
        '| Distribución | Estimación | IC 95 % | Umbral | Outcome |',
        '|--------------|------------|---------|--------|---------|',
    ]
    for dist in DISTS:
        mean, low, high, out = rows[(dist, 32.1)]
        lines.append(
            f'| {labels[dist]} | {fmt(mean)} s | [{fmt(low)}, {fmt(high)}] | '
            f'≤ 230 s | {out} |'
        )
    lines += [
        '',
        'Reproduce:',
        '',
        '```bash',
        'SERVICE_DIST=exponential python verification.py models/ncs-e4.arch',
        'SERVICE_DIST=deterministic python verification.py models/ncs-e4.arch',
        'SERVICE_DIST=lognormal SERVICE_DIST_SIGMA=0.5 python verification.py models/ncs-e4.arch',
        '# or: python tools/p2_service_dist.py',
        '```',
        '',
    ]
    out_dir = os.path.join('out', 'ncs-e4')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'p2-service-dist.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'wrote {path}')
    for dist in DISTS:
        for value in POINTS:
            mean, low, high, out = rows[(dist, value)]
            print(f'{dist:13} CAR={value:4g}  {fmt(mean)} [{fmt(low)}, {fmt(high)}]  {out}')


if __name__ == '__main__':
    main()
