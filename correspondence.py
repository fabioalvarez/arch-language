"""C16 [D4]. Correspondence between the joint model and the model of a constituent.

The core of the language (constituents, boundary components and global connectors) is
shared and changed only by agreement (Delivery 4, section 3.1). A constituent model
repeats the part of sos.arch in which its constituent participates, and the two must
not diverge. For a constituent model M of constituent X and the joint model S:

  K1. Every component of M that belongs to another constituent, and every boundary
      component of X, is in S with the same constituent and tier.
  K2. Every global connector of M (a connector with a link that crosses a boundary) is
      in S with the same nature, coupling, information and agreement, and with the
      same boundary ends: internal hops of M (X -> BEN -> NCG) are ignored, because S
      does not show the inside of a constituent.
  K3. Every global connector of S that reaches a boundary component of X is in M.

Usage: python correspondence.py models/sos.arch models/ncs-e1.arch [...]
Exit status 1 if any model does not correspond.
"""
import sys

from metamodel import create_metamodel


def _components(model):
    return {e.name: e for e in model.elements if e.__class__.__name__ == 'Component'}


def _connectors(model):
    return {e.name: e for e in model.elements if e.__class__.__name__ == 'Connector'}


def _global(k):
    return any(len({c.system.name for c in link.path}) > 1 for link in k.links)


def _ends(k, keep):
    """Links of a connector reduced to the components that the joint model shows."""
    return sorted(tuple(c.name for c in link.path if c.name in keep) for link in k.links)


def check(joint, model):
    problems = []
    own = model.name
    jc, mc = _components(joint), _components(model)
    jk, mk = _connectors(joint), _connectors(model)
    boundary = {n for n, c in jc.items() if c.system.name == own}

    # K1
    for name, c in mc.items():
        if c.system.name == own and name not in boundary:
            continue
        j = jc.get(name)
        if j is None:
            problems.append(f'K1: {name} ({c.system.name}) is not in the joint model')
        elif (j.system.name, j.tier) != (c.system.name, c.tier):
            problems.append(f'K1: {name} is {c.system.name}/{c.tier} here and '
                            f'{j.system.name}/{j.tier} in the joint model')
    for name in boundary - set(mc):
        problems.append(f'K1: boundary component {name} of {own} is missing')

    # K2
    shown = set(jc)
    for name, k in mk.items():
        if not _global(k):
            continue
        j = jk.get(name)
        if j is None:
            problems.append(f'K2: global connector {name} is not in the joint model')
            continue
        for attr in ('natures', 'coupling', 'info', 'agreement'):
            a, b = getattr(k, attr), getattr(j, attr)
            if list(a or []) != list(b or []) if attr == 'natures' else a != b:
                problems.append(f'K2: {name} differs in {attr}: {a!r} here, {b!r} in the joint model')
        if _ends(k, shown) != _ends(j, shown):
            problems.append(f'K2: {name} joins {_ends(k, shown)} here and {_ends(j, shown)} '
                            f'in the joint model')

    # K3
    for name, j in jk.items():
        if name not in mk and any(c.name in boundary for link in j.links for c in link.path):
            problems.append(f'K3: global connector {name} of the joint model is missing')
    return problems


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    mm = create_metamodel()
    joint = mm.model_from_file(sys.argv[1])
    failed = False
    for source in sys.argv[2:]:
        problems = check(joint, mm.model_from_file(source))
        if problems:
            failed = True
            print(f'{source}: does NOT correspond to {sys.argv[1]}')
            for p in problems:
                print(f'  {p}')
        else:
            print(f'{source}: corresponds to {sys.argv[1]}')
    sys.exit(1 if failed else 0)
