import math
import os
import re
from collections import Counter

NATURE = {
    'data_flow': 'data flow',
    'control_command': 'control command',
    'dependency': 'dependency',
    'event_notification': 'event notification',
}


def _components(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Component']


def _connectors(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Connector']


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _nid(name):
    """[A] Mermaid node identifier: Ident may contain '.', '-' and a prime (T2.1, A-K85').
    Identifiers of the base language are returned unchanged."""
    return re.sub(r'\W', '_', name)


def _boundary(connector):
    crossing = [link for link in connector.links if _crosses(link)]
    if not crossing:
        return 'No'
    if len(crossing) == len(connector.links):
        return 'Yes'
    return 'Yes (' + ', '.join(link.path[0].label for link in crossing) + ')'


# ─────────────────────────────────────────────
# Model-to-text: documentation
# ─────────────────────────────────────────────
def generate_connector_table(model, out):
    lines = [f'# Connectors of {model.name}', '',
             '| ID | Source → Target | Nature | Coupling | Information carried | Boundary |',
             '|----|-----------------|--------|----------|---------------------|----------|']
    for k in _connectors(model):
        paths = '; '.join(' → '.join(c.label for c in link.path) for link in k.links)
        natures = ', '.join(NATURE[n] for n in k.natures).capitalize()
        lines.append(f'| {k.name} | {paths} | {natures} | {k.coupling.capitalize()} '
                     f'| {k.info} | {_boundary(k)} |')
    with open(os.path.join(out, 'connectors.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Model-to-text: graphical representation
# ─────────────────────────────────────────────
def generate_view(model, out):
    lines = ['flowchart LR']
    for s in model.constituents:
        lines.append(f'  subgraph {s.name}["{s.label}"]')
        for c in _components(model):
            if c.system is s:
                shape = f'[("{c.label} ({c.tier})")]' if c.tier == 'T4' else f'["{c.label} ({c.tier})"]'
                lines.append(f'    {_nid(c.name)}{shape}')
        lines.append('  end')
    for k in _connectors(model):
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                lines.append(f'  {_nid(a.name)} -->|{k.name}| {_nid(b.name)}')
    with open(os.path.join(out, 'view.mmd'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Transformation to analysis: scenarios
# ─────────────────────────────────────────────
def _instances(component):
    return getattr(component, 'instances', 0) or 1


def _value(single, prop):
    if single.value is not None:
        return single.value
    return getattr(single.ref, prop, None)


def _label(single):
    return single.ref.name + (' (budget)' if single.value is not None else '')


def _fmt_ms(v):
    if math.isinf(v):
        return '∞ (silence not detectable)'
    return f'{v:g} ms'


def _stage_time(single, metric):
    """[C] Stage time in ms. In detection, a periodic connector adds period * misses
    (period 0 = publishes changes only: silence is ambiguous and not detectable)."""
    t = 0.0
    if metric == 'detection' and single.ref.period is not None:
        if single.ref.period == 0:
            return math.inf
        misses = single.ref.misses if single.ref.misses is not None else 1
        t += single.ref.period * misses
    lat = _value(single, 'latency')
    if lat is not None:
        t += lat
    return t


def _unavailability(factor):
    """Unavailability of a factor. A group of replicas, or a component with several
    instances and a beta, uses the common-cause fraction: beta*U + ((1 - beta)*U)**n."""
    if factor.__class__.__name__ == 'Single':
        u = 1 - _value(factor, 'availability') / 100
        if factor.beta:
            n, b = factor.replicas or _instances(factor.ref), factor.beta   # [A] replicas
            return b * u + ((1 - b) * u) ** n, f'{factor.ref.name} × {n} (β = {b:g})'
        return u, factor.ref.name
    u = 1 - _value(factor.members[0], 'availability') / 100
    b, n = factor.beta, len(factor.members)
    name = ', '.join(m.ref.name for m in factor.members)
    return b * u + ((1 - b) * u) ** n, f'{name} (β = {b:g})'


def analyze(analysis):
    rows = []
    if analysis.metric == 'availability':
        terms = [_unavailability(f) for f in analysis.factors]
        total_u = sum(u for u, _ in terms)
        result = 1.0
        for u, _ in terms:
            result *= 1 - u
        result *= 100
        for u, name in terms:
            rows.append(f'| {name} | {u * 100:.4f} % | {u / total_u * 100:.0f} % |')
        header = ['| Factor | Unavailability | Share |', '|--------|----------------|-------|']
        hours = (100 - result) / 100 * 8760
        summary = f'Chain availability: **{result:.2f} %** ({hours:.1f} h/year)'
        met = round(result, 6) >= analysis.target
    elif analysis.metric in ('latency', 'detection'):
        # [C] Supports both base latency chains and chains with budgets (= value),
        # parallel groups ([A | B]) and silence detection (period * misses).
        result = 0.0
        for f in analysis.factors:
            if f.__class__.__name__ == 'Single':
                t = _stage_time(f, analysis.metric)
                rows.append(f'| {_label(f)} | {_fmt_ms(t)} |')
            else:
                member_times = [_stage_time(m, analysis.metric) for m in f.members]
                t = max(member_times)
                names = ' ‖ '.join(f'{m.ref.name} ({_fmt_ms(mt)})'
                                   for m, mt in zip(f.members, member_times))
                rows.append(f'| {names} | {_fmt_ms(t)} (maximum, in parallel) |')
            result += t
        header = ['| Stage | Budget |', '|-------|--------|']
        label = 'Chain latency' if analysis.metric == 'latency' else 'Detection time'
        summary = f'{label}: **{_fmt_ms(result)}**'
        met = not math.isinf(result) and round(result, 6) <= analysis.target
    elif analysis.metric == 'drain':
        # [C] Retention and drain after an outage of duration 'outage':
        # backlog = event_load * outage; lost = max(0, backlog - buffer);
        # drain time = kept / (event_capacity - event_load).
        source, holders = analysis.factors[0], analysis.factors[1:]
        load = source.ref.event_load
        backlog = float(round(load * analysis.outage))
        rows.append(f'| {source.ref.name} | event_load {load:g} ev/s × outage {analysis.outage:g} s '
                    f'= {backlog:g} events | — | — |')
        worst_time, worst_lost = 0.0, 0.0
        for h in holders:
            r = h.ref
            cap = r.event_capacity
            lost = max(0.0, backlog - r.buffer)
            kept = backlog - lost
            t = kept / (cap - load) if cap > load else (0.0 if kept == 0 else math.inf)
            if lost > 0 and kept == 0:
                t = math.inf
            worst_time, worst_lost = max(worst_time, t), max(worst_lost, lost)
            tt = '∞ (nothing retained)' if math.isinf(t) else f'{t:.1f} s'
            rows.append(f'| {r.name} | buffer {r.buffer:g} events; event_capacity {cap:g} ev/s | '
                        f'{lost:g} | {tt} |')
        header = ['| Element | Capacity | Events lost | Drain time |',
                  '|---------|----------|-------------|------------|']
        tt = '∞' if math.isinf(worst_time) else f'{worst_time:.1f} s'
        summary = f'Events lost: **{worst_lost:g}**; drain time: **{tt}**'
        met = worst_lost == 0 and not math.isinf(worst_time) and round(worst_time, 6) <= analysis.target
    elif analysis.metric == 'deadline':
        # [D] Sum of the budgets of the stages; a group works in parallel and counts its maximum.
        result = 0
        for f in analysis.factors:
            if f.__class__.__name__ == 'Group':
                stage = max(m.value for m in f.members)
                names = ' ‖ '.join(f'{m.ref.name} ({m.value:g} s)' for m in f.members)
                rows.append(f'| {names} | {stage:g} s (maximum, in parallel) |')
            else:
                stage = f.value
                rows.append(f'| {f.ref.name} | {stage:g} s |')
            result += stage
        header = ['| Stage | Budget |', '|-------|--------|']
        summary = f'Composed deadline: **{result:g} s**'
        met = round(result, 6) <= analysis.target
    elif analysis.metric == 'utilization':
        # [A] utilization: load / (capacity x instances) of each element; the worst one counts.
        result = 0.0
        for f in analysis.factors:
            r = f.ref
            n = _instances(r)
            u = r.event_load / (r.event_capacity * n) * 100
            result = max(result, u)
            rows.append(f'| {r.name} | {r.event_load:g} | {r.event_capacity:g} | {n} | '
                        f'{u:.0f} % | {math.ceil(r.event_load / r.event_capacity)} |')
        header = ['| Element | Load (per s) | Capacity per instance (per s) | Instances | '
                  'Utilization | Instances needed |',
                  '|---------|--------------|-------------------------------|-----------|'
                  '-------------|------------------|']
        summary = f'Bottleneck utilization: **{result:.0f} %**'
        met = round(result, 6) <= analysis.target
    else:
        # [D, corrected after Delivery 3] recovery: each consumer absorbs only its share of
        # the backlog with its own spare capacity; consumers work in parallel, so the
        # slowest one sets the recovery time. A single consumer takes the whole backlog.
        result, worst = 0.0, None
        for f in analysis.factors:
            c = f.ref
            n = _instances(c)
            s = c.event_capacity * n - c.event_load
            share = f.value if f.value is not None else analysis.backlog
            t = share / s if s > 0 else float('inf')
            if t >= result:
                result, worst = t, c.name
            tt = '∞' if math.isinf(t) else f'{t:.1f} s'
            rows.append(f'| {c.name} | {share:g} | {c.event_capacity:g} × {n} | {c.event_load:g} | '
                        f'{s:g} | {tt} |')
        header = ['| Consumer | Share of the backlog (events) | Capacity (events/s × instances) | '
                  'Load (events/s) | Spare (events/s) | Time |',
                  '|----------|-------------------------------|----------------------------------|'
                  '-----------------|------------------|------|']
        tt = '∞' if math.isinf(result) else f'{result:.1f} s'
        summary = (f'Recovery time: **{tt}** (slowest consumer: {worst}; '
                   f'backlog {analysis.backlog:g} events)')
        met = result <= analysis.target
    verdict = 'met' if met else 'NOT met'
    return [f'## {analysis.name} (Scenario {analysis.scenario})', ''] + header + rows + \
           ['', f'{summary}; target {analysis.target:g}: **{verdict}**', '']


def generate_analysis(model, out):
    lines = [f'# Analysis of {model.name}', '']
    for a in model.analyses:
        lines += analyze(a)
    with open(os.path.join(out, 'analysis.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))


# ─────────────────────────────────────────────
# [A] Model-to-text: structural summary (reproduces the counts of Deliveries 1 and 2)
# ─────────────────────────────────────────────
def generate_summary(model, out):
    comps, conns = _components(model), _connectors(model)
    boundary = [k for k in conns if _boundary(k) != 'No']
    internal = [k for k in conns if _boundary(k) == 'No']
    lines = [f'# Summary of {model.name}', '',
             f'- Constituents: {len(model.constituents)}',
             f'- Components: {len(comps)}',
             f'- Connectors: {len(conns)} ({len(internal)} internal, {len(boundary)} boundary)', '',
             '## Components by constituent and tier', '',
             '| Constituent | T1 | T2 | T3 | T4 | T5 | Total |',
             '|-------------|----|----|----|----|----|-------|']
    for s in model.constituents:
        mine = [c for c in comps if c.system is s]
        row = [sum(1 for c in mine if c.tier == t) for t in ('T1', 'T2', 'T3', 'T4', 'T5')]
        lines.append(f'| {s.name} | ' + ' | '.join(map(str, row)) + f' | {len(mine)} |')
    lines += ['', '## Connectors by coupling', '',
              '| Class | Blocking | Supply | Sink | Total |',
              '|-------|----------|--------|------|-------|']
    for title, group in (('Internal', internal), ('Boundary (derived)', boundary)):
        c = Counter(k.coupling for k in group)
        lines.append(f'| {title} | {c["blocking"]} | {c["supply"]} | {c["sink"]} | {len(group)} |')
    lines += ['', '## Connectors by nature', '',
              '| Nature | Internal | Boundary |', '|--------|----------|----------|']
    for n in NATURE:
        lines.append(f'| {NATURE[n]} | {sum(1 for k in internal if n in k.natures)} | '
                     f'{sum(1 for k in boundary if n in k.natures)} |')
    degree = Counter(c.name for k in conns for link in k.links for c in link.path)
    labels = {c.name: c.label for c in comps}
    lines += ['', '## Connectors per component (top 8)', '',
              '| Component | Connectors |', '|-----------|------------|']
    lines += [f'| {labels[name]} | {d} |' for name, d in degree.most_common(8)]
    with open(os.path.join(out, 'summary.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def apply_transformations(model, out):
    os.makedirs(out, exist_ok=True)
    generate_connector_table(model, out)
    generate_view(model, out)
    generate_analysis(model, out)
    generate_summary(model, out)   # [A]
