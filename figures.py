"""[D4] Figures of the Delivery 4 report (docs/figures/*.png).

The numbers come from out/ncs-e1, out/ncs-e2, out/ncs-e4 (verification.py) and
out/tactics/tactics.md (tactics_check.py). Usage: python figures.py
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = 'docs/figures'
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#8a8984', '#e4e3df'
BLUE, ORANGE, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
BAD, GOOD = '#d03b3b', '#0ca30c'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9, 'text.color': INK,
    'axes.edgecolor': MUTED, 'axes.labelcolor': INK2, 'axes.linewidth': 0.6,
    'xtick.color': INK2, 'ytick.color': INK2, 'axes.spines.top': False,
    'axes.spines.right': False, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
})


def es(x, d=1):
    """Spanish number: decimal comma, dot for thousands."""
    s = f'{x:,.{d}f}'
    return s.replace(',', '_').replace('.', ',').replace('_', '.')


def save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight', pad_inches=0.08)
    plt.close(fig)


def chain():
    """Figure 1: the clearance chain in e1, e2 and e4."""
    rows = [
        ('e1 · diseño inicial', [(n, 1, False) for n in ['NCG', 'TRA', 'ADU', 'RSK', 'CAR', 'RMDB', 'EXDB']], ''),
        ('e2 · con redundancia', [('BEN', 1, True), ('NCG', 2, False), ('BTR', 1, True), ('TRA', 2, False),
                                  ('BAD', 1, True), ('ADU', 2, False), ('BRI', 1, True), ('RSK', 2, False),
                                  ('EXDB', 2, False)], 'β = 0,10 · una zona'),
        ('e4 · rediseño', [('BEN', 2, True), ('NCG', 2, False), ('BTR', 2, True), ('TRA', 2, False),
                           ('BAD', 2, True), ('ADU', 2, False), ('BRI', 2, True), ('RSK', 2, False),
                           ('EXDB', 2, False)], 'β = 0,05 · dos zonas'),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    ax.set_xlim(-0.2, 10.4)
    ax.set_ylim(-1.05, 3.2)
    ax.axis('off')
    w, h = 0.86, 0.42
    for r, (label, items, note) in enumerate(rows):
        y = 2.4 - r * 1.15
        ax.text(-0.15, y + 0.5, label, ha='left', va='bottom', fontsize=9, fontweight='bold', color=INK)
        if note:
            ax.text(10.35, y + 0.5, note, ha='right', va='bottom', fontsize=8, color=INK2)
        for i, (name, n, balancer) in enumerate(items):
            x = i * 1.12
            single = n == 1
            edge = BAD if single else BLUE
            face = '#fbe4e4' if single else '#e3eefb'
            if n == 2:   # second copy drawn behind
                ax.add_patch(FancyBboxPatch((x + 0.07, y - 0.07), w, h, boxstyle='round,pad=0,rounding_size=0.06',
                                            fc=face, ec=edge, lw=0.8))
            ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.06',
                                        fc=face, ec=edge, lw=1.0, ls='--' if balancer else '-'))
            ax.text(x + w / 2, y + h / 2, name, ha='center', va='center', fontsize=8, color=INK)
            if i < len(items) - 1:
                ax.annotate('', xy=(x + 1.12, y + h / 2), xytext=(x + w + 0.07 * (n == 2), y + h / 2),
                            arrowprops=dict(arrowstyle='-|>', color=MUTED, lw=0.7, mutation_scale=7))
    # legend (one row) and reading note (row below)
    ly = -0.45
    def key(x, fc, ec, ls='-', double=False):
        if double:
            ax.add_patch(FancyBboxPatch((x + 0.05, ly - 0.05), 0.3, 0.22, boxstyle='round,pad=0,rounding_size=0.04', fc=fc, ec=ec))
        ax.add_patch(FancyBboxPatch((x, ly), 0.3, 0.22, boxstyle='round,pad=0,rounding_size=0.04', fc=fc, ec=ec, ls=ls))
    key(0, '#fbe4e4', BAD)
    ax.text(0.45, ly + 0.11, 'sin copia (punto único de falla)', va='center', fontsize=8, color=INK2)
    key(4.4, '#e3eefb', BLUE, double=True)
    ax.text(4.9, ly + 0.11, 'dos copias', va='center', fontsize=8, color=INK2)
    key(6.7, 'white', MUTED, ls='--')
    ax.text(7.15, ly + 0.11, 'borde punteado: balanceador', va='center', fontsize=8, color=INK2)
    ax.text(-0.15, ly - 0.42, 'Los elementos están en serie: la cadena funciona solo si todos funcionan.',
            ha='left', va='center', fontsize=8, color=INK2)
    save(fig, 'f1-cadena.png')


def availability():
    """Figure 2: downtime per year of each structure against the 99.9 % threshold."""
    data = [  # label, A %, low, high
        ('e1 · diseño inicial', 99.305, 99.285, 99.325),
        ('e2 · cálculo a mano\n(sin balanceadores)', 99.948, 99.943, 99.952),
        ('e2 · con sus balanceadores', 99.549, 99.536, 99.563),
        ('e2 + T-R1', 99.906, 99.900, 99.912),
        ('e2 + T-R2', 99.563, 99.549, 99.577),
        ('e4 · T-R1 + T-R2', 99.957, 99.953, 99.961),
    ]
    hours = lambda a: (100 - a) / 100 * 8760
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    ys = range(len(data))[::-1]
    for y, (label, a, lo, hi) in zip(ys, data):
        v = hours(a)
        if 'mano' in label:
            color = '#b9b8b3'          # not a real result: ignores the balancers
        elif lo >= 99.92:
            color = GOOD
        elif hi >= 99.9:
            color = ORANGE             # inconclusive or without margin
        else:
            color = BAD
        ax.barh(y, v, height=0.55, color=color, zorder=2)
        ax.errorbar(v, y, xerr=[[v - hours(hi)], [hours(lo) - v]], fmt='none', ecolor=INK, elinewidth=0.8, capsize=2, zorder=3)
        ax.text(max(hours(lo) + 0.8, 10.0), y, f'{es(v)} h  ({es(a, 3)} %)', va='center', fontsize=8, color=INK)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([d[0] for d in data])
    ax.axvline(hours(99.9), color=INK, lw=0.9, ls='-', zorder=4, label='umbral 99,9 % (8,8 h/año)')
    ax.axvline(hours(99.92), color=INK2, lw=0.8, ls=':', zorder=4, label='con margen 99,92 % (7,0 h/año)')
    ax.legend(loc='lower right', frameon=False, fontsize=8)
    ax.set_xlabel('Horas al año con la cadena de levante caída (menos es mejor)')
    ax.set_xlim(0, 72)
    ax.grid(axis='x', color=GRID, lw=0.5, zorder=0)
    ax.tick_params(axis='y', length=0)
    save(fig, 'f2-disponibilidad.png')


def backlog():
    """Figure 3: how the custody backlog drains in e2 and e4 (fluid view, 14 400 events)."""
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    n = 14400
    for label, free, color in [('e2: 2 × 4,5 ev/s − 1,5 de carga = 7,5 ev/s libres', 7.5, BAD),
                               ('e4: 2 × 40 ev/s − 1,5 de carga = 78,5 ev/s libres', 78.5, BLUE)]:
        t = n / free
        ax.plot([0, t], [n, 0], color=color, lw=2, solid_capstyle='round', label=label)
        ax.plot([t], [0], 'o', color=color, ms=5, zorder=3)
        ax.text(t - 35 if free > 10 else t, 600 if free > 10 else 900, f'≈ {es(t, 0)} s', ha='right' if free > 10 else 'center', fontsize=8, color=INK)
    ax.axvline(230, color=INK, lw=0.9)
    ax.text(245, 7500, 'meta: 230 s', fontsize=8, color=INK)
    ax.set_xlim(0, 2050)
    ax.set_ylim(0, 15500)
    ax.set_xlabel('Segundos desde que Carretera vuelve')
    ax.set_ylabel('Custodias pendientes en CAR')
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    ax.grid(color=GRID, lw=0.5, zorder=0)
    ax.legend(frameon=False, fontsize=8, loc='upper right')
    save(fig, 'f3-rezago.png')


def m4():
    """Figure 4: SoS-QS1 (M4) = agreed budgets of the other stages + the verified NCS stage."""
    others = 200 + 40 + 10 + 300
    fig, ax = plt.subplots(figsize=(6.4, 1.7))
    for y, v, color in [(1, 1932.8, BAD), (0, 184.9, BLUE)]:
        ax.barh(y, others, height=0.5, color='#b9b8b3', edgecolor='white', lw=2)
        ax.text(others / 2, y, f'otros tramos\n{es(others, 0)} s', ha='center', va='center', fontsize=7.5, color=INK)
        ax.barh(y, v, left=others, height=0.5, color=color, edgecolor='white', lw=2)
        if v > 400:
            ax.text(others + v / 2, y, f'NCS\n{es(v)} s', ha='center', va='center', fontsize=7.5, color='white')
            ax.text(others + v + 30, y, f'{es(others + v, 0)} s', va='center', fontsize=8.5, fontweight='bold', color=INK)
        else:
            ax.text(930, y, f'{es(others + v, 0)} s  (NCS: {es(v)} s)', va='center', fontsize=8.5, fontweight='bold', color=INK)
    ax.axvline(900, color=INK, lw=1)
    ax.text(910, 1.42, 'meta M4: 900 s', fontsize=8, color=INK)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(['con el NCS de e2', 'con el NCS de e4'])
    ax.set_xlim(0, 2750)
    ax.set_ylim(-0.45, 1.6)
    ax.set_xlabel('Segundos para reconciliar todo el SoS tras 4 h sin Carretera')
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
    ax.tick_params(axis='y', length=0)
    save(fig, 'f4-m4.png')


def sweep(ax, xs, means, lows, highs, color):
    ax.fill_between(xs, lows, highs, color=color, alpha=0.18, lw=0)
    ax.plot(xs, means, color=color, lw=2, marker='o', ms=4)


def capacity():
    """Figure 5: P2 against the capacity of CAR per instance (e4 structure)."""
    xs = [20, 30, 32.1, 35, 40, 60]
    m = [377.3, 248.4, 231.7, 212.2, 184.9, 122.8]
    lo = [375.4, 247.3, 230.5, 211.3, 183.8, 122.0]
    hi = [379.3, 249.5, 233.0, 213.0, 186.1, 123.5]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    sweep(ax, xs, m, lo, hi, BLUE)
    ax.axhline(230, color=INK, lw=0.9)
    ax.axhline(207, color=INK2, lw=0.7, ls=':')
    ax.text(58, 233, 'meta 230 s', ha='right', va='bottom', fontsize=8, color=INK)
    ax.text(58, 210, 'con margen ≤ 207 s', ha='right', va='bottom', fontsize=8, color=INK2)
    for x, v in zip(xs, m):
        if x == 32.1:      # threshold point: callout in the empty lower-left area
            ax.annotate(f'32,1 ev/s → {es(v)} s\n(todavía viola la meta)', (x, v), xytext=(22.5, 165),
                        fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.6))
        else:
            ax.annotate(f'{es(v)} s', (x, v), xytext=(5, 5), textcoords='offset points', fontsize=7.5, color=INK)
    ax.set_xlabel('Capacidad de CAR por instancia (ev/s); el rediseño supone 40')
    ax.set_ylabel('Tiempo de recuperación (s)')
    ax.set_xlim(18, 62)
    ax.grid(color=GRID, lw=0.5, zorder=0)
    save(fig, 'f5-capacidad-car.png')


def beta():
    """Figure 6: P1 against the common-cause fraction beta (e4 structure)."""
    xs = [0.0, 0.02, 0.05, 0.08, 0.09, 0.10, 0.11, 0.12, 0.15]
    m = [99.999, 99.982, 99.955, 99.928, 99.914, 99.908, 99.901, 99.893, 99.863]
    lo = [99.999, 99.980, 99.950, 99.923, 99.908, 99.901, 99.893, 99.886, 99.857]
    hi = [100.0, 99.985, 99.960, 99.933, 99.920, 99.915, 99.908, 99.900, 99.870]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    sweep(ax, xs, m, lo, hi, BLUE)
    ax.axhline(99.9, color=INK, lw=0.9)
    ax.axhline(99.92, color=INK2, lw=0.7, ls=':')
    ax.text(0.152, 99.903, 'umbral 99,9 %', ha='right', fontsize=8, color=INK)
    ax.text(0.152, 99.923, 'con margen ≥ 99,92 %', ha='right', fontsize=8, color=INK2)
    ax.axvline(0.05, color=BLUE, lw=0.7, ls='--')
    ax.text(0.052, 99.99, 'rediseño\nβ = 0,05', fontsize=8, color=INK, va='top')
    ax.axvline(0.10, color=MUTED, lw=0.7, ls='--')
    ax.text(0.102, 99.99, 'diseño e2\nβ = 0,10', fontsize=8, color=INK2, va='top')
    ax.set_xlabel('β: fracción de las fallas que tumban las dos copias de una pareja')
    ax.set_ylabel('Disponibilidad (%)')
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 2)))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 2)))
    ax.set_xlim(-0.003, 0.155)
    ax.set_ylim(99.85, 100.005)
    ax.set_yticks([99.86, 99.88, 99.90, 99.92, 99.94, 99.96, 99.98, 100.0])
    ax.grid(color=GRID, lw=0.5, zorder=0)
    save(fig, 'f6-beta.png')


def sos():
    """Figure: the joint model (sos.arch), its 57 global connectors grouped by pair of constituents."""
    import collections
    import re
    src = open('out/sos/view.mmd').read()
    edges = re.findall(r'(\w+) -->\|\w+\| (\w+)', src)
    pairs = collections.Counter(tuple(sorted(e)) for e in edges)
    pos = {'RGW': (0, 0), 'NCG': (4.2, 0), 'FGW': (2.1, 1.65), 'CGW': (2.1, 0.55),
           'LGW': (2.1, -0.55), 'PGW': (2.1, -1.65)}
    names = {'RGW': 'Carretera (RTS)\nRGW', 'NCG': 'Coordinación\nNacional (NCS)\nNCG',
             'FGW': 'Fluvial (FTS) · FGW', 'CGW': 'Puertos Caribe (CPS) · CGW',
             'LGW': 'Férreo (RLS) · LGW', 'PGW': 'Puertos Pacífico (PPS) · PGW'}
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.axis('off')
    ax.set_xlim(-0.9, 5.1)
    ax.set_ylim(-2.75, 2.5)
    for (a, b), n in sorted(pairs.items(), key=lambda kv: 'NCG' in kv[0]):
        (x1, y1), (x2, y2) = pos[a], pos[b]
        color = BLUE if 'NCG' in (a, b) else '#b9b8b3'
        lw = 0.6 + 0.45 * n
        if {a, b} == {'NCG', 'RGW'}:     # arc over the top, so it does not cross the middle column
            import numpy as np
            t = np.linspace(0, 1, 60)
            cx, cy = 2.1, 4.3              # control point: the curve peaks at y = 2.15, above the top box
            bx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
            by = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
            ax.plot(bx, by, color=color, lw=lw, zorder=1, solid_capstyle='round')
            mx, my = 2.1, 2.15
        else:
            ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=1, solid_capstyle='round')
            if 'NCG' in (a, b):
                o = pos[b] if a == 'NCG' else pos[a]
                mx, my = o[0] + 0.62 * (pos['NCG'][0] - o[0]), o[1] + 0.62 * (pos['NCG'][1] - o[1])
            elif 'RGW' in (a, b):
                o = pos[b] if a == 'RGW' else pos[a]
                mx, my = 0.38 * o[0], 0.38 * o[1]
            else:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, str(n), ha='center', va='center', fontsize=7.5, color=INK, zorder=4,
                bbox=dict(boxstyle='circle,pad=0.18', fc='white', ec=color, lw=0.8))
    for k, (x, y) in pos.items():
        hub = k in ('NCG', 'RGW')
        fc = '#e3eefb' if k == 'NCG' else ('#f2f1ee' if hub else 'white')
        ec = BLUE if k == 'NCG' else MUTED
        w = 1.25 if hub else 1.9
        h = 0.75 if hub else 0.42
        if k == 'NCG':
            h = 0.95
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.08',
                                    fc=fc, ec=ec, lw=1.0, zorder=3))
        ax.text(x, y, names[k], ha='center', va='center', fontsize=7.5, color=INK, zorder=4,
                fontweight='bold' if k == 'NCG' else 'normal')
    ax.text(-0.85, -2.7, 'Cada caja es un sistema con su componente de frontera (T2). El número es cuántos conectores '
            'globales los unen\n(en ambos sentidos); en azul, los del NCS. Total: 57 conectores, 14 acuerdos.',
            fontsize=7.5, color=INK2, va='bottom')
    save(fig, 'f0-sos.png')


if __name__ == '__main__':
    sos(); chain(); availability(); backlog(); m4(); capacity(); beta()
    print('\n'.join(sorted(os.listdir(OUT))))
