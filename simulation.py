"""Step 4 of the verification process: simulation (Laboratory 5, section 4.3).

Transforms the static structure of a model into the dynamic structure of Laboratory 5,
section 2.3, runs the replications of each scenario and computes the 95 % confidence
interval and the outcome of each measure. Extensions of team D for Delivery 4 are
marked [D4]:

  - capacity: 'capacity', or 'event_capacity' of Delivery 3, times 'instances'. The
    instances of a component share one FIFO queue.
  - a store that is down holds the jobs it receives and releases them when it
    returns (the outbox of a constituent that recovers, D-QS10).
  - 'compact n' on a workload: while held by a store, only its last n jobs are kept.
  - 'recovery' is measured per workload, at the last component of its path, and the
    measure without a workload takes the slowest one: consumers of different event
    classes are not interchangeable (correction of Delivery 3).
  - simulate_availability: Monte Carlo of the failures and repairs of the factors of
    an availability analysis, read from the model.
"""
import math
import random
import statistics

# Student t quantiles (0.975) by degrees of freedom, for 95 % confidence intervals
T_975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31,
         9: 2.26, 10: 2.23, 15: 2.13, 20: 2.09, 30: 2.04, 40: 2.02, 60: 2.00}


class Job:
    """One request or event that traverses the path of its workload."""
    __slots__ = ('workload', 'path', 'start', 't', 'lost', 'held')

    def __init__(self, workload, path, start):
        self.workload, self.path, self.start = workload, path, start
        self.t, self.lost, self.held = start, False, False


# ─────────────────────────────────────────────
# Transformation: static structure → dynamic structure
# ─────────────────────────────────────────────

def _stations(scenario):
    """Components visited by the workloads, in an order that respects every path."""
    succ, indeg = {}, {}
    for w in scenario.workloads:
        for c in w.path:
            succ.setdefault(c, set())
            indeg.setdefault(c, 0)
        for a, b in zip(w.path, w.path[1:]):
            if b not in succ[a]:
                succ[a].add(b)
                indeg[b] += 1
    order, ready = [], [c for c in succ if indeg[c] == 0]
    while ready:
        c = ready.pop()
        order.append(c)
        for b in succ[c]:
            indeg[b] -= 1
            if indeg[b] == 0:
                ready.append(b)
    return order


def capacity_of(component):
    """[D4] Service rate of the whole component: capacity of one instance × instances."""
    mu = component.capacity or component.event_capacity
    return mu * (component.instances or 1) if mu else None


# ─────────────────────────────────────────────
# Execution of one replication
# ─────────────────────────────────────────────

def simulate(scenario, seed, rates, capacities):
    """
    Every component with a capacity is a FIFO server with exponential service; components
    without capacity take no time. A component that is down loses the jobs that reach it,
    unless the previous component of the path is a store, or [D4] it is a store itself;
    then the jobs are held until the fault ends.
    """
    rng = random.Random(seed)
    jobs = []
    for w in scenario.workloads:
        rate = rates[w.name]
        t = rng.expovariate(rate) if rate > 0 else scenario.duration
        while t < scenario.duration:
            jobs.append(Job(w.name, w.path, t))
            t += rng.expovariate(rate)
    compact = {w.name: w.compact for w in scenario.workloads if w.compact}
    down = {f.target.name: (f.start, f.start + f.length) for f in scenario.faults}
    end_of_fault = max((d1 for _, d1 in down.values()), default=None)

    recovered = {}                                  # [D4] recovery time per component
    by_workload = {w.name: [j for j in jobs if j.workload == w.name] for w in scenario.workloads}
    for c in _stations(scenario):
        d0, d1 = down.get(c.name, (None, None))
        arriving = []
        held = {}
        for w in scenario.workloads:
            if c not in w.path:
                continue
            i = w.path.index(c)
            for j in by_workload[w.name]:
                if j.lost:
                    continue
                if d0 is not None and d0 <= j.t < d1:
                    if c.store or (i > 0 and w.path[i - 1].store):
                        j.t, j.held = d1, True      # held by the store until the fault ends
                        held.setdefault(j.workload, []).append(j)
                    else:
                        j.lost = True               # nothing holds it: the job is lost
                        continue
                arriving.append(j)
        # [D4] compaction: of the jobs held, only the last n of the workload remain
        for name, n in compact.items():
            js = held.get(name, [])
            if len(js) > n:
                js.sort(key=lambda j: j.start)
                for j in js[:-n]:
                    j.lost, j.held = True, 'compacted'
                arriving = [j for j in arriving if not j.lost]
        mu = capacities.get(c.name)
        if not mu:
            continue
        arriving.sort(key=lambda j: j.t)
        free = 0.0
        for j in arriving:
            start = max(j.t, free)
            if d0 is not None and d0 <= start < d1:
                start = d1                          # the server does not work while down
            if (end_of_fault is not None and c.name not in recovered and j.held is False
                    and j.t > end_of_fault and j.t >= free):
                recovered[c.name] = j.t - end_of_fault  # first new arrival that finds no backlog
            free = start + rng.expovariate(mu)
            j.t = free
    if end_of_fault is not None:
        for c in _stations(scenario):
            if capacities.get(c.name):
                recovered.setdefault(c.name, scenario.duration - end_of_fault)
    return jobs, recovered


def _recovery(scenario, recovered, workload=None):
    """Laboratory 5: the time from the end of the fault until the first new arrival finds
    no backlog. [D4] Measured at the last component with capacity of each workload that
    the fault held (its consumer), and for the slowest one when no workload is given:
    consumers of different event classes recover separately."""
    if not recovered:
        return 0.0
    workloads = [workload] if workload else scenario.workloads
    times = []
    for w in workloads:
        last = [c.name for c in w.path if c.name in recovered]
        if last:
            times.append(recovered[last[-1]])
    return max(times, default=0.0)


def _measure(m, scenario, jobs, recovered):
    if m.metric == 'recovery':
        return _recovery(scenario, recovered, m.workload)
    own = [j for j in jobs if j.workload == m.workload.name and j.start >= scenario.warmup]
    if m.metric == 'lost':
        return sum(1 for j in own if j.lost and j.held != 'compacted')
    times = sorted((j.t - j.start) * 1000 for j in own if not j.lost)
    return times[max(0, math.ceil(0.99 * len(times)) - 1)]


# ─────────────────────────────────────────────
# Replications, confidence intervals, and outcome
# ─────────────────────────────────────────────

def interval(values):
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, mean, mean
    df = len(values) - 1
    t = T_975[max(k for k in T_975 if k <= df)]
    half = t * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


def outcome(low, high, threshold):
    """Classification of Unit 6, Reading 2, §4.1, with a margin of 10 % of the threshold."""
    if high <= 0.9 * threshold:
        return 'Satisfied with margin'
    if high <= threshold:
        return 'Satisfied without margin'
    if low > threshold:
        return 'Violated'
    return 'Inconclusive'


def outcome_at_least(low, high, threshold, margin):
    """[D4] The same classification for a measure that must be at least the threshold
    (availability); the margin is absolute, in the unit of the threshold."""
    if low >= threshold + margin:
        return 'Satisfied with margin'
    if low >= threshold:
        return 'Satisfied without margin'
    if high < threshold:
        return 'Violated'
    return 'Inconclusive'


def run_scenario(scenario):
    """Runs every value of the varied parameter, with independent replications."""
    rates = {w.name: w.rate for w in scenario.workloads}
    capacities = {c.name: capacity_of(c) for w in scenario.workloads for c in w.path if capacity_of(c)}
    if scenario.vary:
        target = scenario.vary.target
        points = [(v, target.name) for v in scenario.vary.values]
    else:
        target, points = None, [(None, None)]
    results = []
    for value, name in points:
        r, k = dict(rates), dict(capacities)
        if target is not None:
            if target.__class__.__name__ == 'Workload':
                r[name] = value
            else:                                   # [D4] the value is per instance
                k[name] = value * (target.instances or 1)
        samples = {m: [] for m in scenario.measures}
        for seed in range(1, scenario.replications + 1):
            jobs, recovered = simulate(scenario, seed, r, k)
            for m in scenario.measures:
                samples[m].append(_measure(m, scenario, jobs, recovered))
        for m in scenario.measures:
            mean, low, high = interval(samples[m])
            results.append((value, m, mean, low, high, outcome(low, high, m.threshold)))
    return results


# ─────────────────────────────────────────────
# [D4] Availability: Monte Carlo of failures and repairs
# ─────────────────────────────────────────────
# Each factor of an availability analysis fails and is repaired as an alternating
# renewal process with availability A and mean time to repair MTTR. A factor with n
# instances (or a group of alternatives) is down when all its replicas are down: each
# replica fails independently at rate (1 - beta)·λ, and a common-cause shock at rate
# beta·λ takes all of them down (Laboratory 3).

def _downs(rng, rate, mttr, horizon):
    t, out = 0.0, []
    while rate > 0:
        t += rng.expovariate(rate)
        if t >= horizon:
            break
        d = rng.expovariate(1.0 / mttr)
        out.append((t, min(t + d, horizon)))
        t += d
    return out


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


def _union(intervals):
    total, cs, ce = 0.0, None, None
    for s, e in sorted(intervals):
        if ce is None or s > ce:
            if ce is not None:
                total += ce - cs
            cs, ce = s, e
        else:
            ce = max(ce, e)
    return total + (ce - cs if ce is not None else 0.0)


def availability_factors(analysis):
    """(availability %, replicas, beta) of each factor, read from the model."""
    out = []
    for f in analysis.factors:
        if f.__class__.__name__ == 'Group':
            a = min(m.ref.availability for m in f.members)
            out.append((a, len(f.members), f.beta or 0.0))
        else:
            n = f.replicas or getattr(f.ref, 'instances', None) or 1
            out.append((f.ref.availability, n, f.beta or 0.0))
    return out


def analytic_availability(factors):
    a = 1.0
    for av, n, b in factors:
        u = 1 - av / 100.0
        a *= 1 - (b * u + ((1 - b) * u) ** n if n > 1 else u)
    return 100 * a


def simulate_availability(analysis, seed, years=20, replications=40, beta=None):
    factors = availability_factors(analysis)
    if beta is not None:
        factors = [(a, n, beta if n > 1 else b) for a, n, b in factors]
    mttr = analysis.mttr or 4.0
    horizon = years * 8760.0
    rng = random.Random(seed)
    values = []
    for _ in range(replications):
        downs = []
        for av, n, b in factors:
            u = 1 - av / 100.0
            lam = u / ((1 - u) * mttr)
            if n == 1:
                downs += _downs(rng, lam, mttr, horizon)
                continue
            both = _downs(rng, (1 - b) * lam, mttr, horizon)
            for _ in range(n - 1):
                both = _intersect(both, _downs(rng, (1 - b) * lam, mttr, horizon))
            downs += both + _downs(rng, b * lam, mttr, horizon)
        values.append(100.0 * (1 - _union(downs) / horizon))
    return values, analytic_availability(factors)
