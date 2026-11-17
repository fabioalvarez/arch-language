# P2 — sensibilidad a la distribución de servicio (e4)

Model: `models/ncs-e4.arch`, scenario `QS_D10`, seeds 1–10.
Service mean fixed at `1/mu`. Lognormal: σ = 0.5,
`mu_ln = ln(1/mu) - σ²/2`.

## CAR = 40 ev/s/instancia (punto de diseño / T-R3)

| Distribución | Estimación (recovery) | IC 95 % | Umbral | Outcome |
|--------------|-----------------------|---------|--------|---------|
| exponential | 184.9 s | [183.8, 186.1] | ≤ 230 s | Satisfied with margin |
| deterministic | 184.3 s | [183.2, 185.4] | ≤ 230 s | Satisfied with margin |
| lognormal (σ=0.5) | 184.1 s | [182.9, 185.4] | ≤ 230 s | Satisfied with margin |

## CAR = 32.1 (punto crítico, opcional)

| Distribución | Estimación | IC 95 % | Umbral | Outcome |
|--------------|------------|---------|--------|---------|
| exponential | 231.7 s | [230.5, 233.0] | ≤ 230 s | Violated |
| deterministic | 231.1 s | [229.7, 232.6] | ≤ 230 s | Inconclusive |
| lognormal (σ=0.5) | 230.6 s | [229.1, 232.1] | ≤ 230 s | Inconclusive |

Reproduce:

```bash
SERVICE_DIST=exponential python verification.py models/ncs-e4.arch
SERVICE_DIST=deterministic python verification.py models/ncs-e4.arch
SERVICE_DIST=lognormal SERVICE_DIST_SIGMA=0.5 python verification.py models/ncs-e4.arch
# or: python tools/p2_service_dist.py
```
