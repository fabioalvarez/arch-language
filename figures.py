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
    """Figure: downtime per year of each structure against the 99.9 % threshold, in two panels:
    (a) before the redesign, (b) contribution of each tactic of iteration 4."""
    hours = lambda a: (100 - a) / 100 * 8760
    panels = [
        ('(a) Antes del rediseño: la redundancia de e2 no alcanza por los balanceadores', [
            ('e1 · diseño inicial, sin copias', 99.305, 99.285, 99.325),
            ('e2 · cálculo a mano\n(ignora los balanceadores)', 99.948, 99.943, 99.952),
            ('e2 · con sus balanceadores', 99.549, 99.536, 99.563)]),
        ('(b) Rediseño: cada táctica por separado y las dos juntas', [
            ('e2 (punto de partida)', 99.549, 99.536, 99.563),
            ('e2 + T-R1\n(balanceadores en pareja)', 99.906, 99.900, 99.912),
            ('e2 + T-R2\n(dos zonas, β = 0,05)', 99.563, 99.549, 99.577),
            ('e4 = T-R1 + T-R2', 99.957, 99.953, 99.961)]),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.0), gridspec_kw={'height_ratios': [3, 4], 'hspace': 0.55})
    for ax, (title, data) in zip(axes, panels):
        ys = range(len(data))[::-1]
        for y, (label, a, lo, hi) in zip(ys, data):
            v = hours(a)
            if 'mano' in label:
                color = '#b9b8b3'
            elif lo >= 99.92:
                color = GOOD
            elif hi >= 99.9:
                color = ORANGE
            else:
                color = BAD
            ax.barh(y, v, height=0.55, color=color, zorder=2)
            ax.errorbar(v, y, xerr=[[v - hours(hi)], [hours(lo) - v]], fmt='none', ecolor=INK, elinewidth=0.8,
                        capsize=2, zorder=3)
            ax.text(max(hours(lo) + 0.8, 10.0), y, f'{es(v)} h al año  ({es(a, 3)} %)', va='center', fontsize=8, color=INK)
        ax.set_yticks(list(ys))
        ax.set_yticklabels([d[0] for d in data], fontsize=8)
        ax.axvline(hours(99.9), color=INK, lw=0.9, zorder=4, label='meta 99,9 % (8,8 h/año)')
        ax.axvline(hours(99.92), color=INK2, lw=0.8, ls=':', zorder=4, label='con margen 99,92 % (7,0 h/año)')
        ax.set_xlim(0, 72)
        ax.grid(axis='x', color=GRID, lw=0.5, zorder=0)
        ax.tick_params(axis='y', length=0)
        ax.set_title(title, fontsize=9, loc='left', color=INK, fontweight='bold')
    axes[1].set_xlabel('Horas al año con la cadena de levante caída (menos es mejor)')
    axes[1].legend(loc='upper center', bbox_to_anchor=(0.45, -0.3), ncol=2, frameon=False, fontsize=7.5)
    save(fig, 'f2-disponibilidad.png')


def backlog():
    """Figure: how the custody backlog (14 400 events) drains in CAR, one panel per design."""
    n = 14400
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.7), sharey=True, gridspec_kw={'wspace': 0.12})
    for ax, (title, free, color, xmax, step) in zip(axes, [
            ('(a) Diseño anterior (e2)\n2 × 4,5 − 1,5 = 7,5 ev/s libres', 7.5, BAD, 2100, 500),
            ('(b) Rediseño (e4)\n2 × 40 − 1,5 = 78,5 ev/s libres', 78.5, BLUE, 260, 50)]):
        t = n / free
        ax.plot([0, t], [n, 0], color=color, lw=2.2, solid_capstyle='round')
        ax.plot([t], [0], 'o', color=color, ms=5, zorder=3)
        ax.axvline(230, color=INK, lw=0.9)
        if free < 10:
            ax.text(230 + xmax * 0.015, 5200, 'meta\n230 s', fontsize=7.5, color=INK, va='top')
        else:
            ax.text(230 + xmax * 0.015, 13300, 'meta\n230 s', fontsize=7.5, color=INK, va='top')
        ax.annotate(f'termina en {es(t, 0)} s', (t, 0), xytext=(t * 0.76, 1500), ha='right', va='center',
                    fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.6))
        ax.set_xlim(0, xmax)
        ax.set_xticks(range(0, xmax + 1, step))
        ax.set_ylim(0, 15500)
        ax.set_title(title, fontsize=8.5, loc='left', color=INK)
        ax.set_xlabel('Segundos desde que vuelve Carretera')
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
        ax.grid(color=GRID, lw=0.5, zorder=0)
    axes[0].set_ylabel('Custodias pendientes en CAR')
    axes[0].yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 0)))
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
    """Figure: P1 against the common-cause fraction beta (e4 structure, seed 1000 for every point)."""
    xs = [0.0, 0.05, 0.08, 0.10, 0.11, 0.12, 0.15, 0.20]
    m = [99.999, 99.957, 99.927, 99.906, 99.897, 99.887, 99.862, 99.826]
    lo = [99.998, 99.953, 99.922, 99.900, 99.889, 99.880, 99.853, 99.815]
    hi = [100.0, 99.961, 99.932, 99.912, 99.904, 99.893, 99.871, 99.836]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    sweep(ax, xs, m, lo, hi, BLUE)
    ax.axhline(99.9, color=INK, lw=0.9)
    ax.axhline(99.92, color=INK2, lw=0.7, ls=':')
    ax.text(0.205, 99.903, 'meta 99,9 %', ha='right', fontsize=8, color=INK)
    ax.text(0.205, 99.923, 'con margen ≥ 99,92 %', ha='right', fontsize=8, color=INK2)
    ax.axvline(0.05, color=BLUE, lw=0.7, ls='--')
    ax.text(0.052, 99.99, 'rediseño\nβ = 0,05', fontsize=8, color=INK, va='top')
    ax.axvline(0.10, color=MUTED, lw=0.7, ls='--')
    ax.text(0.102, 99.99, 'diseño e2\nβ = 0,10', fontsize=8, color=INK2, va='top')
    ax.set_xlabel('β: fracción de las fallas que tumban las dos copias de una pareja')
    ax.set_ylabel('Disponibilidad (%)')
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 2)))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: es(v, 2)))
    ax.set_xlim(-0.004, 0.207)
    ax.set_ylim(99.81, 100.005)
    ax.set_xticks([0, 0.05, 0.10, 0.15, 0.20])
    ax.set_yticks([99.82, 99.86, 99.90, 99.94, 99.98])
    ax.grid(color=GRID, lw=0.5, zorder=0)
    save(fig, 'f6-beta.png')


def sos():
    """Figure 1: what the joint model (sos.arch) says each system exchanges.
    (a) the 29 global connectors of the NCS, by kind of information and direction;
    (b) the 28 connectors among the other five systems, by purpose."""
    import re
    src = open('out/sos/connectors.md').read()
    ids = set(re.findall(r'\| (SoS_K\d+[ab]?) \|', src))
    assert len(ids) == 57, len(ids)
    rows = [('Carretera', 'RTS · RGW'), ('Puertos Caribe', 'CPS · CGW'), ('Puertos Pacífico', 'PPS · PGW'),
            ('Férreo', 'RLS · LGW'), ('Fluvial', 'FTS · FGW')]
    cols = [('Custodia\nrecibida', 'in'), ('Posición y\nestado del viaje', 'in'), ('Arribo y\nmanifiesto', 'in'),
            ('Levante\naduanero', 'both'), ('Estado de\nla carga', 'both'), ('Estado de\nservicio', 'out'),
            ('Paso por\npeaje', 'in')]
    cell = {  # (row, col): connector ids of sos.arch
        (0, 0): 'K5', (0, 1): 'K6', (0, 4): 'K17', (0, 6): 'K36',
        (1, 0): 'K29', (1, 2): 'K11', (1, 3): 'K12, K32', (1, 4): 'K21', (1, 5): 'K32',
        (2, 0): 'K30', (2, 2): 'K8', (2, 3): 'K9, K33', (2, 4): 'K20', (2, 5): 'K33',
        (3, 0): 'K13', (3, 1): 'K14', (3, 4): 'K18', (3, 5): 'K34',
        (4, 0): 'K15', (4, 1): 'K16', (4, 4): 'K19', (4, 5): 'K35'}
    qs1 = {(0, 0), (0, 1), (1, 5), (2, 5), (3, 5), (4, 5), (0, 6)}   # used by SoS-QS1
    face = {'in': '#e3eefb', 'out': '#fde9df', 'both': '#e7f6ef'}
    edge = {'in': BLUE, 'out': ORANGE, 'both': AQUA}
    arrow = {'in': '→ NCS', 'out': 'NCS →', 'both': '⇄ NCS'}

    fig = plt.figure(figsize=(6.6, 6.9))
    ax = fig.add_axes([0, 0.5, 1, 0.5])
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.45, 6.3)
    ax.text(0.05, 6.15, '(a) Los 29 conectores del NCS: qué recibe y qué entrega a cada sistema', fontsize=9,
            fontweight='bold', color=INK, va='top')
    x0, cw, rh = 2.1, 1.12, 0.78
    for j, (name, d) in enumerate(cols):
        cx = x0 + j * cw + cw / 2
        ax.text(cx, 5.45, name, ha='center', va='center', fontsize=7.2, color=INK)
        ax.text(cx, 4.95, arrow[d], ha='center', va='center', fontsize=7, color=edge[d], fontweight='bold')
    for i, (name, gw) in enumerate(rows):
        cy = 4.3 - i * rh
        ax.text(0.05, cy + 0.1, name, va='center', fontsize=8, color=INK, fontweight='bold')
        ax.text(0.05, cy - 0.18, gw, va='center', fontsize=7, color=INK2)
        for j, (_, d) in enumerate(cols):
            x = x0 + j * cw
            v = cell.get((i, j))
            if v is None:
                ax.add_patch(FancyBboxPatch((x + 0.05, cy - rh / 2 + 0.06), cw - 0.1, rh - 0.12,
                                            boxstyle='round,pad=0,rounding_size=0.05', fc='#f7f7f5', ec='#e4e3df', lw=0.6))
                continue
            hot = (i, j) in qs1
            ax.add_patch(FancyBboxPatch((x + 0.05, cy - rh / 2 + 0.06), cw - 0.1, rh - 0.12,
                                        boxstyle='round,pad=0,rounding_size=0.05', fc=face[d], ec=INK if hot else edge[d],
                                        lw=1.8 if hot else 0.8))
            ax.text(x + cw / 2, cy, v, ha='center', va='center', fontsize=7.5, color=INK)
    ly = 0.25
    for k, (lab, d) in enumerate([('el sistema informa al NCS', 'in'), ('el NCS informa al sistema', 'out'),
                                  ('pregunta y respuesta', 'both')]):
        x = 0.1 + k * 2.75
        ax.add_patch(FancyBboxPatch((x, ly - 0.13), 0.35, 0.26, boxstyle='round,pad=0,rounding_size=0.04',
                                    fc=face[d], ec=edge[d], lw=0.8))
        ax.text(x + 0.45, ly, lab, va='center', fontsize=7.5, color=INK2)
    ax.add_patch(FancyBboxPatch((8.35, ly - 0.13), 0.35, 0.26, boxstyle='round,pad=0,rounding_size=0.04',
                                fc='white', ec=INK, lw=1.8))
    ax.text(8.8, ly, 'usado en SoS-QS1', va='center', fontsize=7.5, color=INK2)
    ax.text(0.05, -0.25, 'Kn = conector SoS-Kn del modelo conjunto; «K9» incluye la pregunta (K9a) y la respuesta (K9b).',
            fontsize=7, color=INK2)

    bx = fig.add_axes([0, 0, 1, 0.47])
    bx.axis('off')
    bx.set_xlim(0, 10)
    bx.set_ylim(-0.2, 5.4)
    bx.text(0.05, 5.3, '(b) Los 28 conectores entre los otros cinco sistemas: coordinan la operación', fontsize=9,
            fontweight='bold', color=INK, va='top')
    pos = {'RTS': (0.85, 2.35), 'FTS': (7.0, 4.3), 'CPS': (7.0, 3.0), 'RLS': (7.0, 1.7), 'PPS': (7.0, 0.4)}
    label = {'RTS': 'Carretera\n(RTS)', 'FTS': 'Fluvial (FTS)', 'CPS': 'Puertos Caribe (CPS)', 'RLS': 'Férreo (RLS)',
             'PPS': 'Puertos Pacífico (PPS)'}
    links = [('FTS', 'turno camión-barcaza y retiro de carga (K4, K28)', 0.2),
             ('CPS', 'cita portuaria y retiro de carga (K1, K26)', 0.2),
             ('RLS', 'turno camión-tren y retiro de carga (K3, K23)', -0.2),
             ('PPS', 'cita portuaria y retiro de carga (K2, K27)', -0.2)]
    trunk = 2.0                        # Carretera reaches the four systems through one trunk line
    (x1, y1) = pos['RTS']
    bx.plot([x1 + 0.75, trunk], [y1, y1], color='#b9b8b3', lw=1.6, zorder=1)
    bx.plot([trunk, trunk], [pos['PPS'][1], pos['FTS'][1]], color='#b9b8b3', lw=1.6, zorder=1)
    for b, text, dy in links:
        x2, y2 = pos[b]
        bx.plot([trunk, x2 - 0.95], [y2, y2], color='#b9b8b3', lw=1.6, zorder=1)
        bx.text(trunk + 0.15, y2 + 0.2, text, ha='left', va='center', fontsize=7, color=INK, zorder=3)
    side = [('FTS', 'CPS', 'muelle de transferencia y\ncargue de barcazas (K10, K31)'),
            ('CPS', 'RLS', 'vagones y descargue de\nconvoyes (K24, K25)'),
            ('RLS', 'PPS', 'vagones y descargue de\nconvoyes (K7, K22)')]
    for a, b, text in side:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        bx.plot([x1 + 1.05, x2 + 1.05], [y1, y2], color='#b9b8b3', lw=1.6, zorder=1)
        bx.plot([x1 + 0.95, x1 + 1.05], [y1, y1], color='#b9b8b3', lw=1.6)
        bx.plot([x2 + 0.95, x2 + 1.05], [y2, y2], color='#b9b8b3', lw=1.6)
        bx.text(x1 + 1.15, (y1 + y2) / 2, text, ha='left', va='center', fontsize=7, color=INK)
    for k, (x, y) in pos.items():
        w, h = (1.5, 0.75) if k == 'RTS' else (1.9, 0.42)
        bx.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle='round,pad=0,rounding_size=0.06',
                                    fc='#f2f1ee' if k == 'RTS' else 'white', ec=MUTED, lw=1.0, zorder=2))
        bx.text(x, y, label[k], ha='center', va='center', fontsize=7.5, color=INK, zorder=3)
    save(fig, 'f0-sos.png')

if __name__ == '__main__':
    sos(); chain(); availability(); backlog(); m4(); capacity(); beta()
    print('\n'.join(sorted(os.listdir(OUT))))
