"""Verification of a model (Laboratory 5, section 4.4), extended by team D for Delivery 4.

Runs the five steps of the verification process: reads the model (1. abstraction and
2. instantiation), draws its graph by tier and checks the structural properties on it
(3. graphing), runs the scenarios (4. simulation), and writes the report (5. reporting).
Extensions of team D are marked [D4]:

  - S1 is checked on the artifact of each quality scenario verified by an availability
    analysis, closed over the components that its links traverse: an element the
    analysis forgot (a load balancer) is still found on the graph. A component with
    several instances, or replicated by an alternative, is not a single point.
  - availability analyses that a scenario names in 'verified_by' are simulated by Monte
    Carlo, with the closed formula of Laboratory 3 as the case with a known result.
  - the report lists the scenarios declared not verifiable and the tactics.

Usage: python verification.py [model.arch ...]   (default: models/ncs-e*.arch)
"""
import glob
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

from metamodel import create_metamodel
from simulation import run_scenario, simulate_availability, interval, outcome_at_least

TIER_COLOR = {'T1': 'lightblue', 'T2': 'khaki', 'T3': 'lightgreen', 'T4': 'orange', 'T5': 'salmon'}
AVAILABILITY_MARGIN = 0.02      # [D4] percentage points above the threshold for "with margin"
AVAILABILITY_SEED = 1000


def _components(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Component']


def _connectors(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Connector']


# ─────────────────────────────────────────────
# Step 3. Graphing
# ─────────────────────────────────────────────

def draw_graph(model, out):
    graph = nx.DiGraph()
    order = {s.name: i for i, s in enumerate(model.constituents)}
    for c in sorted(_components(model), key=lambda c: order[c.system.name]):
        graph.add_node(c.name, tier=c.tier, layer=-int(c.tier[1]))
    for k in _connectors(model):
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                graph.add_edge(a.name, b.name, label=k.name)
    plt.figure(figsize=(16, 11))
    pos = nx.multipartite_layout(graph, subset_key='layer', align='horizontal')
    arc = 'arc3,rad=0.2'
    nx.draw(graph, pos, with_labels=True, node_size=1600, font_size=7, arrows=True,
            connectionstyle=arc, edge_color='gray',
            node_color=[TIER_COLOR[graph.nodes[n]['tier']] for n in graph.nodes])
    plt.title(f'{model.name} — C&C graph')
    plt.savefig(os.path.join(out, 'graph.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return graph


# ─────────────────────────────────────────────
# Structural properties, checked on the graph of the model
# ─────────────────────────────────────────────

def _chain(analysis):
    """Components of a chain: the components it names and those that its connectors traverse."""
    nodes = set()
    for f in analysis.factors:
        refs = [m.ref for m in f.members] if f.__class__.__name__ == 'Group' else [f.ref]
        for r in refs:
            if r.__class__.__name__ == 'Component':
                nodes.add(r.name)
            else:
                nodes |= {c.name for link in r.links for c in link.path}
    return nodes


def artifact_closure(model, scenario):
    """[D4] The components of the artifact, plus every component that a link traverses
    between two of them, or on the way in from another constituent."""
    names = {e.name for e in scenario.artifact if e.__class__.__name__ == 'Component'}
    own = {e.system.name for e in scenario.artifact if e.__class__.__name__ == 'Component'}
    closure = set(names)
    for k in _connectors(model):
        for link in k.links:
            p = link.path
            if len(p) < 3 or p[-1].name not in names:
                continue
            if p[0].name in names or p[0].system.name not in own:
                closure |= {c.name for c in p[1:-1]}
    return closure


def _replicated(model, scenario):
    """[D4] Components replicated by instances, or by an alternative in a group."""
    names = {c.name for c in _components(model) if (c.instances or 1) > 1}
    for a in scenario.checks:
        for f in a.factors:
            if f.__class__.__name__ == 'Group' and len(f.members) > 1:
                names |= {m.ref.name for m in f.members}
            elif f.__class__.__name__ == 'Single' and (f.replicas or 1) > 1:
                names.add(f.ref.name)
    return names


def check_structure(model):
    rows = []
    for s in model.scenarios:
        if s.artifact and any(a.metric == 'availability' for a in s.checks):
            chain = artifact_closure(model, s)
            single = sorted(chain - _replicated(model, s))
            rows.append((f'S1. No single point of failure in the artifact of {s.label}',
                         ', '.join(single) or 'None', 'Violated' if single else 'Satisfied'))
    for a in model.analyses:
        if a.metric == 'latency':
            chain = _chain(a)
            blocking = sorted(k.name for k in _connectors(model) if k.coupling == 'blocking'
                              for link in k.links if {c.name for c in link.path} <= chain)
            rows.append((f'S2. No blocking connector in the chain of Scenario {a.scenario}',
                         ', '.join(blocking) or 'None', 'Violated' if blocking else 'Satisfied'))
    return rows


# ─────────────────────────────────────────────
# Step 4 [D4]. Availability by simulation
# ─────────────────────────────────────────────

def check_availability(model):
    rows = []
    for s in model.scenarios:
        for i, a in enumerate(x for x in s.checks if x.metric == 'availability'):
            seed = AVAILABILITY_SEED + i
            values, exact = simulate_availability(a, seed)
            mean, low, high = interval(values)
            rows.append((s, a, seed, len(values), mean, low, high, exact,
                         outcome_at_least(low, high, a.target, AVAILABILITY_MARGIN)))
    return rows


# ─────────────────────────────────────────────
# Step 5. Reporting
# ─────────────────────────────────────────────

def report(model, source, structure, availability, simulations, out):
    lines = [f'# Verification of {model.name}', '', f'Model: `{source}`', '',
             '## Structural properties', '',
             '| Property | Elements found | Outcome |', '|----------|----------------|---------|']
    lines += [f'| {p} | {e} | {o} |' for p, e, o in structure] or ['| — | — | — |']
    if availability:
        lines += ['', '## Availability (Monte Carlo of failures and repairs)', '',
                  '| Scenario | Analysis | Seed | Replications | Estimate | 95 % CI | Known result '
                  '(Lab 3 formula) | Threshold | Outcome |',
                  '|----------|----------|------|--------------|----------|---------|------------------'
                  '-------------|-----------|---------|']
        for s, a, seed, n, mean, low, high, exact, result in availability:
            lines.append(f'| {s.label} | {a.name} | {seed} | {n} × 20 years | {mean:.3f} % | '
                         f'[{low:.3f}, {high:.3f}] | {exact:.3f} % | ≥ {a.target:g} % | {result} |')
    for s, results in simulations:
        varied = s.vary.target.name if s.vary else '—'
        lines += ['', f'## Scenario {s.label} ({s.name})', '',
                  f'Run {s.duration:g} s, warm-up {s.warmup:g} s, '
                  f'{s.replications} replications (seeds 1–{s.replications}); varied: {varied}', '',
                  '| Value | Measure | Estimate | 95 % CI | Threshold | Outcome |',
                  '|-------|---------|----------|---------|-----------|---------|']
        for value, m, mean, low, high, result in results:
            v = '—' if value is None else f'{value:g}'
            name = f'{m.metric} {m.workload.name}' if m.workload else m.metric
            lines.append(f'| {v} | {name} | {mean:.1f} | [{low:.1f}, {high:.1f}] '
                         f'| ≤ {m.threshold:g} {m.unit} | {result} |')
    declared = [s for s in model.scenarios if s.missing]
    if declared:
        lines += ['', '## Scenarios not verifiable with this language', '',
                  '| Scenario | Attribute | What is missing |', '|----------|-----------|-----------------|']
        lines += [f'| {s.label} | {s.attribute or "—"} | {s.missing} |' for s in declared]
    if model.tactics:
        lines += ['', '## Tactics', '', '| Tactic | For | Introduces | Changes |',
                  '|--------|-----|------------|---------|']
        for t in model.tactics:
            lines.append(f'| {t.label} ({t.name}) | {", ".join(s.label for s in t.scenarios)} | '
                         f'{", ".join(e.name for e in t.introduces) or "—"} | '
                         f'{", ".join(e.name for e in t.changes) or "—"} |')
    with open(os.path.join(out, 'verification.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def verify(model, source):
    out = os.path.join('out', os.path.splitext(os.path.basename(source))[0])
    os.makedirs(out, exist_ok=True)
    draw_graph(model, out)                                                  # Step 3
    structure = check_structure(model)
    availability = check_availability(model)                                # Step 4
    simulations = [(s, run_scenario(s)) for s in model.scenarios if s.workloads]
    report(model, source, structure, availability, simulations, out)       # Step 5
    return out


if __name__ == '__main__':
    sources = sys.argv[1:] or sorted(glob.glob('models/ncs-e*.arch'))
    mm = create_metamodel()
    for source in sources:
        model = mm.model_from_file(source)                                  # Steps 1 and 2
        out = verify(model, source)
        print(f'{source}: verification report written to {out}/verification.md')
