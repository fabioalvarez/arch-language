# Analysis of NCS

## DQS1 (Scenario D-QS1)

| Factor | Unavailability | Share |
|--------|----------------|-------|
| BEN × 2 (β = 0.05) | 0.0051 % | 11 % |
| NCG × 2 (β = 0.05) | 0.0051 % | 11 % |
| BTR × 2 (β = 0.05) | 0.0051 % | 11 % |
| TRA × 2 (β = 0.05) | 0.0051 % | 11 % |
| BAD × 2 (β = 0.05) | 0.0051 % | 11 % |
| ADU × 2 (β = 0.05) | 0.0051 % | 11 % |
| BRI × 2 (β = 0.05) | 0.0051 % | 11 % |
| RSK × 2 (β = 0.05) | 0.0051 % | 11 % |
| EXDB, EXDB2 (β = 0.05) | 0.0051 % | 11 % |

Chain availability: **99.95 %** (4.0 h/year); target 99.9: **met**

## DQS10 (Scenario D-QS10)

| Consumer | Share of the backlog (events) | Capacity (events/s × instances) | Load (events/s) | Spare (events/s) | Time |
|----------|-------------------------------|----------------------------------|-----------------|------------------|------|
| CAR | 14400 | 40 × 2 | 1.5 | 78.5 | 183.4 s |
| TRS | 6000 | 60 × 2 | 20 | 100 | 60.0 s |

Recovery time: **183.4 s** (slowest consumer: CAR; backlog 20400 events); target 230: **met**

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200 s |
| SoS_K5 | 40 s |
| NCG | 230 s |
| SoS_K32 | 10 s |
| CGW (300 s) ‖ PGW (300 s) ‖ LGW (300 s) ‖ FGW (300 s) | 300 s (maximum, in parallel) |

Composed deadline: **780 s**; target 900: **met**

## SoSQS1M3 (Scenario SoS-QS1 (M3))

| Stage | Budget |
|-------|--------|
| RGW | 30 s |
| SoS_K36 | 10 s |
| NCG | 15 s |

Composed deadline: **55 s**; target 60: **met**
