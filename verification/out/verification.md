# Verificación por simulación — equipo D (borrador)

P1 (D-QS1): 40 réplicas × 20 años, MTTR = 4 h. P2 (D-QS10): 30 réplicas. IC 95 % normal.

## P1 — Disponibilidad de la cadena de levante (meta ≥ 99,9 %)

| Caso | Semilla | Simulada | IC 95 % | Fórmula (caso conocido) | Resultado |
|------|---------|----------|---------|--------------------------|-----------|
| it1_e1 | 1000 | 99.285 % | [99.265; 99.305] | 99.302 % | violada |
| it2_e2_sin_balanceadores | 1001 | 99.952 % | [99.946; 99.958] | 99.950 % | satisfecha con margen |
| it2_e2_con_balanceadores | 1002 | 99.548 % | [99.536; 99.561] | 99.550 % | violada |
| it4_e4 | 1003 | 99.955 % | [99.951; 99.959] | 99.954 % | satisfecha con margen |

### Sensibilidad de P1 a β (estructura rediseñada, fórmula)

| β | Disponibilidad |
|---|----------------|
| 0.02 | 99.981 % |
| 0.05 | 99.954 % |
| 0.1 | 99.909 % |
| 0.15 | 99.864 % |
| 0.2 | 99.820 % |

## P2 — Absorción del rezago (meta ≤ 230 s)

| Caso | Semilla | Simulado | IC 95 % | Vaciado fluido (caso conocido) | Consumidor más lento | Resultado |
|------|---------|----------|---------|--------------------------------|----------------------|-----------|
| it1_e1 | 2000 | 7201.7 s | [7194.5; 7209.0] | 7200.0 s | TRS | violada |
| it3_e2 | 2001 | 1913.4 s | [1905.8; 1921.1] | 1920.0 s | CAR | violada |
| it4_e4 | 2002 | 183.8 s | [183.3; 184.3] | 183.4 s | CAR | satisfecha con margen |

### Sensibilidad de P2 a la capacidad de CAR por instancia (L19)

| Capacidad (ev/s) | Simulado | IC 95 % | Fluido | ≤ 230 s |
|---|---|---|---|---|
| 4.5 | 1916.2 s | [1910.1; 1922.3] | 1920.0 s | no |
| 10 | 777.4 s | [775.0; 779.8] | 778.4 s | no |
| 20 | 373.4 s | [372.2; 374.5] | 374.0 s | no |
| 30 | 246.7 s | [246.2; 247.3] | 246.2 s | no |
| 32.1 | 230.0 s | [229.3; 230.7] | 229.7 s | no |
| 35 | 209.8 s | [209.2; 210.4] | 210.2 s | sí |
| 40 | 183.1 s | [182.5; 183.7] | 183.4 s | sí |
| 60 | 121.4 s | [121.1; 121.8] | 121.5 s | sí |
