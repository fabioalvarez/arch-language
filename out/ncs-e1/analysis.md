# Analysis of NCS

## DQS1 (Scenario D-QS1)

| Factor | Unavailability | Share |
|--------|----------------|-------|
| NCG | 0.1000 % | 14 % |
| TRA | 0.1000 % | 14 % |
| ADU | 0.1000 % | 14 % |
| RSK | 0.1000 % | 14 % |
| CAR | 0.1000 % | 14 % |
| RMDB | 0.1000 % | 14 % |
| EXDB | 0.1000 % | 14 % |

Chain availability: **99.30 %** (61.1 h/year); target 99.9: **NOT met**

## DQS10 (Scenario D-QS10)

| Consumer | Share of the backlog (events) | Capacity (events/s × instances) | Load (events/s) | Spare (events/s) | Time |
|----------|-------------------------------|----------------------------------|-----------------|------------------|------|
| CAR | 14400 | 4.5 × 1 | 1.5 | 3 | 4800.0 s |
| TRS | 288000 | 60 × 1 | 20 | 40 | 7200.0 s |

Recovery time: **7200.0 s** (slowest consumer: TRS; backlog 302400 events); target 230: **NOT met**

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200 s |
| SoS_K5 | 40 s |
| NCG | 7200 s |
| CGW (300 s) ‖ PGW (300 s) ‖ LGW (300 s) ‖ FGW (300 s) | 300 s (maximum, in parallel) |

Composed deadline: **7740 s**; target 900: **NOT met**
