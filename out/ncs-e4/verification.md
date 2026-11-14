# Verification of NCS

Model: `models/ncs-e4.arch`

## Structural properties

| Property | Elements found | Outcome |
|----------|----------------|---------|
| S1. No single point of failure in the artifact of D-QS1 | None | Satisfied |

## Availability (Monte Carlo of failures and repairs)

| Scenario | Analysis | Seed | Replications | Estimate | 95 % CI | Known result (Lab 3 formula) | Threshold | Outcome |
|----------|----------|------|--------------|----------|---------|-------------------------------|-----------|---------|
| D-QS1 | DQS1 | 1000 | 40 × 20 years | 99.957 % | [99.953, 99.961] | 99.954 % | ≥ 99.9 % | Satisfied with margin |

## Scenario D-QS10 (QS_D10)

Run 17000 s, warm-up 0 s, 10 replications (seeds 1–10); varied: CAR

| Value | Measure | Estimate | 95 % CI | Threshold | Outcome |
|-------|---------|----------|---------|-----------|---------|
| 4.5 | recovery Custody | 1932.8 | [1921.5, 1944.1] | ≤ 230 s | Violated |
| 4.5 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 4.5 | recovery | 1932.8 | [1921.5, 1944.1] | ≤ 230 s | Violated |
| 4.5 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 20 | recovery Custody | 377.3 | [375.4, 379.3] | ≤ 230 s | Violated |
| 20 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 20 | recovery | 377.3 | [375.4, 379.3] | ≤ 230 s | Violated |
| 20 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 30 | recovery Custody | 248.4 | [247.3, 249.5] | ≤ 230 s | Violated |
| 30 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 30 | recovery | 248.4 | [247.3, 249.5] | ≤ 230 s | Violated |
| 30 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 32.1 | recovery Custody | 231.7 | [230.5, 233.0] | ≤ 230 s | Violated |
| 32.1 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 32.1 | recovery | 231.7 | [230.5, 233.0] | ≤ 230 s | Violated |
| 32.1 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 35 | recovery Custody | 212.2 | [211.3, 213.0] | ≤ 230 s | Satisfied without margin |
| 35 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 35 | recovery | 212.2 | [211.3, 213.0] | ≤ 230 s | Satisfied without margin |
| 35 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 40 | recovery Custody | 184.9 | [183.8, 186.1] | ≤ 230 s | Satisfied with margin |
| 40 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 40 | recovery | 184.9 | [183.8, 186.1] | ≤ 230 s | Satisfied with margin |
| 40 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |
| 60 | recovery Custody | 122.8 | [122.0, 123.5] | ≤ 230 s | Satisfied with margin |
| 60 | recovery Positions | 61.3 | [60.6, 61.9] | ≤ 230 s | Satisfied with margin |
| 60 | recovery | 122.8 | [122.0, 123.5] | ≤ 230 s | Satisfied with margin |
| 60 | lost Custody | 0.0 | [0.0, 0.0] | ≤ 0 events | Satisfied with margin |

## Scenarios not verifiable with this language

| Scenario | Attribute | What is missing |
|----------|-----------|-----------------|
| D-QS2 | disponibilidad | Clases de evento con prioridad y una regla de descarte (compactación) en el Bus |
| D-QS3 | seguridad | Identidad, credenciales y límites de confianza por conector |
| D-QS4 | desempeño | Tasas de llegada y capacidad en consultas por componente (p99_latency ya existe desde el Laboratorio 5) |
| D-QS5 | escalabilidad | Capacidad y carga de consultas por instancia frente al crecimiento |
| D-QS6 | elasticidad | Perfiles de carga en el tiempo y costo por instancia-hora |
| D-QS7 | integridad | Atributos del modelo canónico por conector; model checking de la regla de descarte de duplicados |
| D-QS8 | interoperabilidad | Versión de cada conector y período de convivencia de versiones |
| D-QS9 | disponibilidad | Plazos (timeouts), período de latido y reintentos |
| SoS-QS1 (M1) | desempeño | Reglas de comportamiento; model checking sobre una máquina de estados de despacho |
| SoS-QS1 (M2) | desempeño | Distribuciones del error de estimación y su simulación |

## Tactics

| Tactic | For | Introduces | Changes |
|--------|-----|------------|---------|
| Redundancia activa (TE2_Redundancy) | D-QS1, D-QS10 | — | NCG, TRA, ADU, RSK, CAR, TRS |
| Respaldo del Expediente Aduanero (TE2_Backup) | D-QS1 | EXDB2 | — |
| Balanceo de carga entre réplicas (TE2_Balancing) | D-QS1 | BEN, BTR, BAD, BRI, BCA, BTS | — |
| Compactación de posiciones en el rezago (TE2_Compaction) | D-QS10 | BUF | — |
| Balanceadores en pareja (TR1_BalancerPairs) | D-QS1 | — | BEN, BTR, BAD, BRI |
| Réplicas en dos zonas de falla (beta 0,05) (TR2_FailureZones) | D-QS1 | — | NCG, TRA, ADU, RSK, EXDB, EXDB2, BEN, BTR, BAD, BRI |
| Consumo por lotes de custodias (TR3_BatchCustody) | D-QS10 | — | CAR |
