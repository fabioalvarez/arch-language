"""Verification by simulation of the NCS (Delivery 4, team D) — DRAFT.

Two properties, of different attributes, verified by simulation with replications,
fixed seeds and 95 % confidence intervals:

  P1 (D-QS1, availability): Monte Carlo of failures and repairs of the clearance chain.
  P2 (D-QS10, recoverability): discrete-event drain of the backlog, one queue per
      consumer and event class (custody -> CAR, positions -> TRS).

Each simulation is checked against a case with a known result (closed formula of
Laboratory 3 for P1; deterministic fluid drain for P2), and P2 includes a sensitivity
analysis of the uncertain parameter L19 (event capacity of CAR).

Parameters are those of the models (models/ncs-e1.arch, ncs-e2.arch, ncs-e4.arch).
Usage: python verification/simulate.py  -> writes verification/out/*.md and *.png
"""
import json
import math
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
Z95 = 1.959964

# ───────────────────────── common ─────────────────────────


def ci95(x):
    x = np.asarray(x, dtype=float)
    m = x.mean()
    h = Z95 * x.std(ddof=1) / math.sqrt(len(x)) if len(x) > 1 else 0.0
    return m, m - h, m + h


# ───────────────────────── P1: availability (D-QS1) ─────────────────────────
# Each element: availability A (L17: 99.9 %), exponential repair with mean MTTR.
# A pair (instances 2) with common-cause fraction beta: each instance fails
# independently at rate (1 - beta) * lambda, and a common-cause shock at rate
# beta * lambda takes both down (Laboratory 3).

MTTR_H = 4.0          # assumed mean time to repair (h); U depends only on A, not on MTTR
YEARS = 20            # horizon of one replication
REPS = 40             # replications
HOURS = YEARS * 8760.0


def _down_intervals(rng, rate, mttr, horizon):
    """Alternating renewal process: list of (start, end) down intervals."""
    t, out = 0.0, []
    while True:
        t += rng.exponential(1.0 / rate)
        if t >= horizon:
            return out
        d = rng.exponential(mttr)
        out.append((t, min(t + d, horizon)))
        t += d


def _intersect(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if s < e:
            out.append((s, e))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def _union_length(intervals):
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(intervals):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def element_down(rng, elem, horizon):
    a, n, beta = elem['availability'] / 100.0, elem.get('instances', 1), elem.get('beta', 0.0)
    u = 1.0 - a
    lam = u / (a * MTTR_H)                      # A = MTTF / (MTTF + MTTR)
    if n == 1:
        return _down_intervals(rng, lam, MTTR_H, horizon)
    ind = [_down_intervals(rng, (1 - beta) * lam, MTTR_H, horizon) for _ in range(n)]
    both = ind[0]
    for other in ind[1:]:
        both = _intersect(both, other)
    common = _down_intervals(rng, beta * lam, MTTR_H, horizon) if beta > 0 else []
    return both + common


def analytic_availability(chain):
    """Closed formula of the model (Lab 3): U(pair) = beta*U + ((1-beta)*U)^n, series product."""
    a = 1.0
    for e in chain:
        u = 1 - e['availability'] / 100.0
        n, b = e.get('instances', 1), e.get('beta', 0.0)
        a *= 1 - (b * u + ((1 - b) * u) ** n if n > 1 else u)
    return a * 100


def simulate_availability(chain, seed):
    rng = np.random.default_rng(seed)
    res = []
    for _ in range(REPS):
        downs = []
        for e in chain:
            downs += element_down(rng, e, HOURS)
        res.append(100.0 * (1 - _union_length(downs) / HOURS))
    return res


def E(name, n=1, beta=0.0, a=99.9):
    return {'name': name, 'availability': a, 'instances': n, 'beta': beta}


CHAINS = {
    # Iteration 1: starting structure (ncs-e1), seven single elements in series
    'it1_e1': [E('NCG'), E('TRA'), E('ADU'), E('RSK'), E('CAR'), E('RMDB'), E('EXDB')],
    # Iteration 2: resulting structure (ncs-e2), as computed in Delivery 2 (no balancers)
    'it2_e2_sin_balanceadores': [E('NCG', 2, .1), E('TRA', 2, .1), E('ADU', 2, .1), E('RSK', 2, .1),
                                 E('EXDB|EXDB2', 2, .1)],
    # Iteration 2: the same chain with the four balancers it traverses (single, 99.9 %)
    'it2_e2_con_balanceadores': [E('BEN'), E('NCG', 2, .1), E('BTR'), E('TRA', 2, .1), E('BAD'),
                                 E('ADU', 2, .1), E('BRI'), E('RSK', 2, .1), E('EXDB|EXDB2', 2, .1)],
    # Iteration 4: redesigned (ncs-e4): balancers in pairs, replicas in two failure zones (beta 0.05)
    'it4_e4': [E('BEN', 2, .05), E('NCG', 2, .05), E('BTR', 2, .05), E('TRA', 2, .05), E('BAD', 2, .05),
               E('ADU', 2, .05), E('BRI', 2, .05), E('RSK', 2, .05), E('EXDB|EXDB2', 2, .05)],
}


# ───────────────────────── P2: recoverability (D-QS10) ─────────────────────────
# One queue per consumer (M/M/c with an initial backlog): Poisson arrivals at the normal
# load, exponential service at event_capacity per instance. Drain time = first instant at
# which the queue no longer holds events of the backlog (number in system <= c).
# While all c servers are busy, the process is a birth-death walk with rates lambda and
# c*mu, which is simulated in vectorized chunks.

REPS_Q = 30


def drain_time(rng, backlog, lam, mu, c):
    n, t = backlog + c, 0.0          # c events in service plus the backlog waiting
    rate = lam + c * mu
    p_arr = lam / rate
    while True:
        k = 200_000
        steps = np.where(rng.random(k) < p_arr, 1, -1)
        path = n + np.cumsum(steps)
        hit = np.flatnonzero(path <= c)
        dts = rng.exponential(1.0 / rate, k)
        if hit.size:
            return t + dts[:hit[0] + 1].sum()
        n, t = path[-1], t + dts.sum()


def simulate_recovery(consumers, seed):
    """consumers: list of dicts (name, share, capacity, load, instances). Max over consumers."""
    rng = np.random.default_rng(seed)
    per = {c['name']: [] for c in consumers}
    total = []
    for _ in range(REPS_Q):
        times = [drain_time(rng, c['share'], c['load'], c['capacity'], c['instances']) for c in consumers]
        for c, x in zip(consumers, times):
            per[c['name']].append(x)
        total.append(max(times))
    return total, per


def fluid(consumers):
    return max(c['share'] / (c['capacity'] * c['instances'] - c['load']) for c in consumers)


def C(name, share, cap, load, n):
    return {'name': name, 'share': share, 'capacity': cap, 'load': load, 'instances': n}


QUEUES = {
    'it1_e1': [C('CAR', 14400, 4.5, 1.5, 1), C('TRS', 288000, 60, 20, 1)],
    'it3_e2': [C('CAR', 14400, 4.5, 1.5, 2), C('TRS', 6000, 60, 20, 2)],
    # Iteration 4: CAR consumes custody in batches (40 events/s per instance)
    'it4_e4': [C('CAR', 14400, 40, 1.5, 2), C('TRS', 6000, 60, 20, 2)],
}


def outcome(value, target, higher_is_better, lo, hi, margin_rel):
    """Satisfied with margin / without margin / inconclusive / violated, using the 95 % CI."""
    ok_lo, ok_hi = (lo >= target, hi >= target) if higher_is_better else (hi <= target, lo <= target)
    if ok_lo:
        m = (value - target) / abs(target) if higher_is_better else (target - value) / abs(target)
        return 'satisfecha con margen' if m >= margin_rel else 'satisfecha sin margen'
    if ok_hi:
        return 'inconclusa'
    return 'violada'


def main():
    os.makedirs(OUT, exist_ok=True)
    results = {'P1': {}, 'P2': {}, 'P2_sensitivity': [], 'P1_sensitivity': []}

    # P1
    for i, (key, chain) in enumerate(CHAINS.items()):
        sims = simulate_availability(chain, seed=1000 + i)
        m, lo, hi = ci95(sims)
        an = analytic_availability(chain)
        # margin for availability: unavailability at least 20 % below the allowed 0.1 %
        res = outcome(m, 99.9, True, lo, hi, margin_rel=0.0002)
        results['P1'][key] = dict(mean=m, lo=lo, hi=hi, analytic=an, outcome=res, seed=1000 + i,
                                  reps=REPS, years=YEARS)
    # P1 sensitivity: beta of the redesigned chain
    for b in (0.02, 0.05, 0.10, 0.15, 0.20):
        chain = [dict(e, beta=b) for e in CHAINS['it4_e4']]
        results['P1_sensitivity'].append(dict(beta=b, analytic=analytic_availability(chain)))

    # P2
    for i, (key, cons) in enumerate(QUEUES.items()):
        tot, per = simulate_recovery(cons, seed=2000 + i)
        m, lo, hi = ci95(tot)
        res = outcome(m, 230, False, lo, hi, margin_rel=0.10)
        results['P2'][key] = dict(mean=m, lo=lo, hi=hi, fluid=fluid(cons), outcome=res, seed=2000 + i,
                                  reps=REPS_Q,
                                  per={k: ci95(v) for k, v in per.items()})
    # P2 sensitivity: event capacity per instance of CAR (L19), redesigned structure
    for j, cap in enumerate((4.5, 10, 20, 30, 32.1, 35, 40, 60)):
        cons = [C('CAR', 14400, cap, 1.5, 2), C('TRS', 6000, 60, 20, 2)]
        tot, _ = simulate_recovery(cons, seed=3000 + j)
        m, lo, hi = ci95(tot)
        results['P2_sensitivity'].append(dict(capacity=cap, mean=m, lo=lo, hi=hi, fluid=fluid(cons)))

    with open(os.path.join(OUT, 'results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    _report(results)
    _plots(results)


def _report(r):
    L = ['# Verificación por simulación — equipo D (borrador)', '',
         f'P1 (D-QS1): {REPS} réplicas × {YEARS} años, MTTR = {MTTR_H:g} h. '
         f'P2 (D-QS10): {REPS_Q} réplicas. IC 95 % normal.', '',
         '## P1 — Disponibilidad de la cadena de levante (meta ≥ 99,9 %)', '',
         '| Caso | Semilla | Simulada | IC 95 % | Fórmula (caso conocido) | Resultado |',
         '|------|---------|----------|---------|--------------------------|-----------|']
    for k, v in r['P1'].items():
        L.append(f"| {k} | {v['seed']} | {v['mean']:.3f} % | [{v['lo']:.3f}; {v['hi']:.3f}] | "
                 f"{v['analytic']:.3f} % | {v['outcome']} |")
    L += ['', '### Sensibilidad de P1 a β (estructura rediseñada, fórmula)', '',
          '| β | Disponibilidad |', '|---|----------------|']
    L += [f"| {s['beta']:g} | {s['analytic']:.3f} % |" for s in r['P1_sensitivity']]
    L += ['', '## P2 — Absorción del rezago (meta ≤ 230 s)', '',
          '| Caso | Semilla | Simulado | IC 95 % | Vaciado fluido (caso conocido) | Consumidor más lento | Resultado |',
          '|------|---------|----------|---------|--------------------------------|----------------------|-----------|']
    for k, v in r['P2'].items():
        slow = max(v['per'], key=lambda n: v['per'][n][0])
        L.append(f"| {k} | {v['seed']} | {v['mean']:.1f} s | [{v['lo']:.1f}; {v['hi']:.1f}] | "
                 f"{v['fluid']:.1f} s | {slow} | {v['outcome']} |")
    L += ['', '### Sensibilidad de P2 a la capacidad de CAR por instancia (L19)', '',
          '| Capacidad (ev/s) | Simulado | IC 95 % | Fluido | ≤ 230 s |', '|---|---|---|---|---|']
    for s in r['P2_sensitivity']:
        L.append(f"| {s['capacity']:g} | {s['mean']:.1f} s | [{s['lo']:.1f}; {s['hi']:.1f}] | "
                 f"{s['fluid']:.1f} s | {'sí' if s['hi'] <= 230 else 'no'} |")
    with open(os.path.join(OUT, 'verification.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


def _plots(r):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return
    s = r['P2_sensitivity']
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot([x['capacity'] for x in s], [x['mean'] for x in s], marker='o', color='#2a6f97', label='Simulado (media)')
    ax.axhline(230, color='#c44536', ls='--', lw=1, label='Meta 230 s')
    ax.set_yscale('log'); ax.set_xlabel('Capacidad de CAR por instancia (eventos/s)')
    ax.set_ylabel('Tiempo de absorción (s)'); ax.legend(frameon=False)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'p2_sensibilidad.png'), dpi=150); plt.close(fig)


if __name__ == '__main__':
    main()
