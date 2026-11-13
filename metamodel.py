import os
from textx import metamodel_from_file, get_location, TextXSemanticError


def _error(message, obj):
    raise TextXSemanticError(message, **get_location(obj))


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _boundary(connector):
    """A connector is a boundary connector when one of its links joins two constituents."""
    return any(_crosses(link) for link in connector.links)


def _singles(factor):
    return factor.members if factor.__class__.__name__ == 'Group' else [factor]


def _value(single, prop):
    if single.value is not None:
        return single.value
    return getattr(single.ref, prop, None)


# [A, C] Constituent-specific styles are checked inside their own constituent:
# a style is attributed to a delimited part of the structure, not to the whole SoS.
CPMS = 'CPS'
RTS = 'RTS'


def _inside(connector, constituent):
    return all(c.system.name == constituent for link in connector.links for c in link.path)


def check_model(model):
    components = [e for e in model.elements if e.__class__.__name__ == 'Component']
    connectors = [e for e in model.elements if e.__class__.__name__ == 'Connector']

    for k in connectors:
        # C1. Every link joins at least two components.
        for link in k.links:
            if len(link.path) < 2:
                _error(f'{k.name}: a link must join at least two components', k)
        # C2. A control command has a single source with authority over its targets.
        if 'control_command' in k.natures:
            sources = {link.path[0].name for link in k.links}
            if len(sources) > 1:
                _error(f'{k.name}: control command with several sources {sorted(sources)}', k)
        # C3 [D, corrected after Delivery 3]. Every boundary connector is governed by an
        # agreement among owners, and the agreement binds only boundary components: every
        # hop of the connector that crosses a constituent joins two T2 components. A
        # connector with an agreement attached directly to a T3 or T4 is rejected.
        if _boundary(k):
            if not k.agreement:
                _error(f'{k.name}: boundary connector without agreement', k)
            for link in k.links:
                for a, b in zip(link.path, link.path[1:]):
                    if a.system is not b.system and (a.tier != 'T2' or b.tier != 'T2'):
                        bad = a if a.tier != 'T2' else b
                        # Same message as C8 [A], so the rejections of team A do not change.
                        _error(f'{k.name}: boundary link reaches {bad.name} (tier {bad.tier}); '
                               f'only T2 boundary components may face another constituent', k)
        # C6 [D]. Layers (NCS, Delivery 1 section 5): no component of T1 is
        # joined directly to a data store of T4; every read goes through a T3 service.
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                if {a.tier, b.tier} == {'T1', 'T4'}:
                    _error(f'{k.name}: {a.name} ({a.tier}) joined directly to {b.name} ({b.tier})', k)
        # C7 [D, C]. Acknowledged SoS (global styles, Delivery 1): a control command
        # never crosses a boundary; authority exists only inside one constituent.
        if 'control_command' in k.natures and _boundary(k):
            _error(f'{k.name}: control command crosses the boundary of a constituent', k)
        # C8 [A, C]. Gateway pattern (Delivery 1): every link that crosses a boundary
        # starts and ends at a boundary component of tier T2. Since the correction of C3
        # [D] the same check runs inside C3, with the same message; C8 is kept as the
        # name team A gives to the gateway pattern.
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                if a.system is not b.system and (a.tier != 'T2' or b.tier != 'T2'):
                    bad = a if a.tier != 'T2' else b
                    _error(f'{k.name}: boundary link reaches {bad.name} (tier {bad.tier}); '
                           f'only T2 boundary components may face another constituent', k)
        # C10 [A, C]. Event-based style (CPMS and RTS, Delivery 1): inside the constituent,
        # a notification is published without waiting for the consumer, so it is never blocking.
        if (_inside(k, CPMS) or _inside(k, RTS)) and 'event_notification' in k.natures and k.coupling == 'blocking':
            _error(f'{k.name}: event notification with blocking coupling '
                   f'(the publisher must not wait for the consumer)', k)
        # C11 [C]. Client-server style (RTS, Delivery 1 section 4): T1 clients initiate
        # interactions and the server does not depend on them; a dependency from T1 goes to T2.
        if _inside(k, RTS) and 'dependency' in k.natures:
            for link in k.links:
                for a, b in zip(link.path, link.path[1:]):
                    if b.tier == 'T1':
                        _error(f'{k.name}: dependency on the client {b.name} (T1)', k)
                    if a.tier == 'T1' and b.tier != 'T2':
                        _error(f'{k.name}: client {a.name} (T1) depends on {b.name} ({b.tier}), '
                               f'not on a T2 component', k)

    # C4 [D, adapted]. A data store (T4) is accessed by dependency only from components
    # of its own domain. A store without domain keeps the rule of Laboratory 4:
    # a single component.
    for c in components:
        if c.tier == 'T4':
            users = [link.path[-2]
                     for k in connectors if 'dependency' in k.natures
                     for link in k.links if link.path[-1] is c]
            if c.domain:
                foreign = sorted({u.name for u in users if u.domain != c.domain})
                if foreign:
                    _error(f'{c.name}: data store of domain {c.domain} accessed from {foreign}', c)
            elif len({u.name for u in users}) > 1:
                _error(f'{c.name}: data store shared by {sorted({u.name for u in users})}', c)

    # C9 [A]. Hierarchical style and control loop of the CPMS (Delivery 1 section 5.2): a
    # piece of physical equipment (T5) of the port receives control commands from a single
    # component.
    for c in components:
        if c.tier == 'T5' and c.system.name == CPMS:
            authorities = {link.path[-2].name
                           for k in connectors if 'control_command' in k.natures
                           for link in k.links if link.path[-1] is c}
            if len(authorities) > 1:
                _error(f'{c.name}: equipment commanded by several authorities '
                       f'{sorted(authorities)}', c)

    # C5 [D, A, C, extended]. Every factor of an analysis carries the property
    # the analysis needs, and groups have the shape required by the metric.
    for a in model.analyses:
        for f in a.factors:
            if f.__class__.__name__ == 'Group':
                if a.metric == 'availability' and not f.beta:
                    _error(f'{a.name}: a redundancy group needs beta', a)
                elif a.metric == 'drain':
                    _error(f'{a.name}: drain analyses do not admit groups', a)
                elif a.metric != 'availability' and f.beta is not None:
                    _error(f'{a.name}: beta is only meaningful in availability groups', a)

            for s in _singles(f):
                r = s.ref
                if a.metric == 'availability' and not _value(s, 'availability'):
                    _error(f'{a.name}: {r.name} has no availability property', a)
                if a.metric == 'latency' and _value(s, 'latency') is None:
                    _error(f'{a.name}: {r.name} has no latency property', a)
                n = s.replicas or getattr(r, 'instances', 0) or 1   # [A] replicas
                if a.metric == 'availability' and s.beta and n < 2:
                    _error(f'{a.name}: {r.name} has beta but fewer than 2 instances', a)
                if s.replicas and not s.beta:                       # [A]
                    _error(f'{a.name}: {r.name} has replicas but no beta', a)
                if a.metric == 'utilization' and (not r.event_capacity or not r.event_load):  # [A]
                    _error(f'{a.name}: {r.name} needs event_capacity and event_load', a)
                if a.metric == 'deadline' and not s.value:
                    _error(f'{a.name}: {r.name} has no budget (= value) for the deadline', a)
                if a.metric == 'recovery':
                    if r.__class__.__name__ != 'Component' or not r.event_capacity or not r.event_load:
                        _error(f'{a.name}: {r.name} needs event_capacity and event_load', a)
                if a.metric == 'detection' and r.period is None and _value(s, 'latency') is None:  # [C]
                    _error(f'{a.name}: {r.name} has neither period nor latency', a)

        if a.metric == 'recovery' and not a.backlog:
            _error(f'{a.name}: a recovery analysis needs its backlog', a)

        # C5 [D, corrected after Delivery 3]. The spare capacity of two consumers is not
        # interchangeable: each consumer absorbs only the events of its own class. With more
        # than one consumer, every consumer carries its share of the backlog (= events),
        # and the shares add up to the backlog.
        if a.metric == 'recovery':
            consumers = [s for f in a.factors for s in _singles(f)]
            shares = [s.value for s in consumers]
            if len(consumers) > 1 and any(v is None for v in shares):
                missing = [s.ref.name for s in consumers if s.value is None]
                _error(f'{a.name}: consumers are not interchangeable; {missing} '
                       f'need their share of the backlog (= events)', a)
            if all(v is not None for v in shares) and round(sum(shares), 6) != round(a.backlog, 6):
                _error(f'{a.name}: the shares of the backlog add up to {sum(shares):g}, '
                       f'not to {a.backlog:g}', a)

        if a.metric == 'drain':  # [C]
            steps = [s for f in a.factors for s in _singles(f)]
            if a.outage is None:
                _error(f'{a.name}: a drain analysis needs an outage duration', a)
            if steps[0].ref.event_load is None:
                _error(f'{a.name}: the first factor ({steps[0].ref.name}) must carry event_load', a)
            if len(steps) < 2:
                _error(f'{a.name}: a drain analysis needs at least one retaining element', a)
            for s in steps[1:]:
                if s.ref.buffer is None or s.ref.event_capacity is None:
                    _error(f'{a.name}: {s.ref.name} needs buffer and event_capacity', a)


    check_scenarios(model, connectors)


# ─────────────────────────────────────────────────────────────────────────────
# Delivery 4. Constraints C6 and C7 of Laboratory 5 are C12 and C13 here, because C6
# (layers) and C7 (no command crosses a boundary) were already taken in Delivery 3.
# ─────────────────────────────────────────────────────────────────────────────

SIX_PARTS = ('source', 'stimulus', 'artifact', 'environment', 'response')


def _capacity(component):
    return component.capacity or component.event_capacity


def check_scenarios(model, connectors):
    hops = {(a, b) for k in connectors for link in k.links for a, b in zip(link.path, link.path[1:])}
    for s in getattr(model, 'scenarios', None) or []:
        # C12 [L5 C6]. Every hop of a workload follows a connector of the model, in
        # either direction: the stimulus travels only along the declared structure.
        for w in s.workloads or []:
            for a, b in zip(w.path, w.path[1:]):
                if (a, b) not in hops and (b, a) not in hops:
                    _error(f'{s.name}: {w.name} goes from {a.name} to {b.name} without a connector', w)

        # C13 [L5 C7]. A component that fails in a scenario has a capacity.
        for f in s.faults or []:
            if not _capacity(f.target):
                _error(f'{s.name}: fault on {f.target.name}, which has no capacity', f)

        # C14 [D4]. A quality scenario has its six parts: if it declares one of source,
        # stimulus, artifact, environment and response, it declares all of them, and its
        # response measure is verified in one of three ways: simulated (workloads,
        # measures and run), verified by an analysis of the model, or declared not
        # verifiable with the concept that is missing.
        declared = [p for p in SIX_PARTS if getattr(s, p, None)]
        if declared:
            missing = [p for p in SIX_PARTS if not getattr(s, p, None)]
            if missing:
                _error(f'{s.name}: quality scenario without {", ".join(missing)}', s)
        simulated = bool(s.workloads)
        if simulated and (not s.measures or s.duration is None):
            _error(f'{s.name}: a simulated scenario needs at least one measure and its run', s)
        if s.measures and not simulated:
            _error(f'{s.name}: a measure needs a workload to measure', s)
        if declared and not (simulated or s.checks or s.missing):
            _error(f'{s.name}: the response measure is neither simulated, verified by an '
                   f'analysis, nor declared not verifiable', s)
        if s.missing and (simulated or s.checks):
            _error(f'{s.name}: declared not verifiable, but it is also verified', s)
        for m in s.measures or []:
            if m.workload is not None and m.workload not in s.workloads:
                _error(f'{s.name}: measure on {m.workload.name}, a workload of another scenario', m)

    # C15 [D4]. A tactic is linked to what it changes and to a scenario whose measure is
    # verified, so its effect is verified, not assumed (Laboratory 5, section 6).
    for t in getattr(model, 'tactics', None) or []:
        if not (t.introduces or t.changes):
            _error(f'{t.name}: tactic that introduces or changes no element', t)
        for s in t.scenarios:
            if s.missing or not (s.workloads or s.checks):
                _error(f'{t.name}: motivated by {s.name}, whose measure is not verified', t)


def create_metamodel():
    grammar = os.path.join(os.path.dirname(__file__), 'arch.tx')
    # auto_init_attributes=False distinguishes unwritten attributes (None) from 0.
    mm = metamodel_from_file(grammar, auto_init_attributes=False)
    mm.register_model_processor(lambda model, metamodel: check_model(model))
    return mm
