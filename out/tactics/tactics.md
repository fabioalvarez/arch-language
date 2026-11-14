# Tactics of iteration 4

Monte Carlo: 40 replications x 20 years, MTTR 4.0 h.

## 1. Contribution of each tactic to P1 (D-QS1)

| Structure | Estimate | 95 % CI | Known (Lab 3) | Outcome |
|---|---|---|---|---|
| e2: balancers single, beta 0.10 (seed 1001) | 99.549 % | [99.536, 99.563] | 99.550 % | Violated |
| e2 + T-R1 (balancers in pairs, beta 0.10) (seed 1000) | 99.906 % | [99.900, 99.912] | 99.909 % | Inconclusive |
| e2 + T-R2 (beta 0.05, balancers single) (seed 1000) | 99.563 % | [99.549, 99.577] | 99.575 % | Violated |
| e4: T-R1 + T-R2 (seed 1000) | 99.957 % | [99.953, 99.961] | 99.954 % | Satisfied with margin |

## 2. Sensitivity of P1 to beta (e4)

| beta | Seed | Estimate | 95 % CI | Known (Lab 3) | Outcome |
|---|---|---|---|---|---|
| 0.00 | 1200 | 99.999 % | [99.999, 100.000] | 99.999 % | Satisfied with margin |
| 0.02 | 1201 | 99.982 % | [99.980, 99.985] | 99.981 % | Satisfied with margin |
| 0.05 | 1202 | 99.955 % | [99.950, 99.960] | 99.954 % | Satisfied with margin |
| 0.08 | 1203 | 99.928 % | [99.923, 99.933] | 99.927 % | Satisfied with margin |
| 0.09 | 1204 | 99.914 % | [99.908, 99.920] | 99.918 % | Satisfied without margin |
| 0.10 | 1205 | 99.908 % | [99.901, 99.915] | 99.909 % | Satisfied without margin |
| 0.11 | 1206 | 99.901 % | [99.893, 99.908] | 99.900 % | Inconclusive |
| 0.12 | 1207 | 99.893 % | [99.886, 99.900] | 99.891 % | Inconclusive |
| 0.15 | 1208 | 99.863 % | [99.857, 99.870] | 99.864 % | Violated |

## 3. Discarded alternative to T-R3: more instances of CAR at 4.5 events/s

| Instances | Recovery (s) | 95 % CI | Outcome |
|---|---|---|---|
| 14 | 236.1 | [234.8, 237.4] | Violated |
| 15 | 220.0 | [218.6, 221.5] | Satisfied without margin |
