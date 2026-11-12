# Summary of NCS

- Constituents: 6
- Components: 35
- Connectors: 91 (62 internal, 29 boundary)

## Components by constituent and tier

| Constituent | T1 | T2 | T3 | T4 | T5 | Total |
|-------------|----|----|----|----|----|-------|
| CPS | 0 | 1 | 0 | 0 | 0 | 1 |
| PPS | 0 | 1 | 0 | 0 | 0 | 1 |
| RTS | 0 | 1 | 0 | 0 | 0 | 1 |
| RLS | 0 | 1 | 0 | 0 | 0 | 1 |
| FTS | 0 | 1 | 0 | 0 | 0 | 1 |
| NCS | 3 | 11 | 6 | 9 | 1 | 30 |

## Connectors by coupling

| Class | Blocking | Supply | Sink | Total |
|-------|----------|--------|------|-------|
| Internal | 48 | 8 | 6 | 62 |
| Boundary (derived) | 14 | 3 | 12 | 29 |

## Connectors by nature

| Nature | Internal | Boundary |
|--------|----------|----------|
| data flow | 25 | 7 |
| control command | 5 | 0 |
| dependency | 22 | 7 |
| event notification | 10 | 15 |

## Connectors per component (top 8)

| Component | Connectors |
|-----------|------------|
| National Coordination Gateway | 56 |
| Balanceador de Entrada | 28 |
| Servicio de Carga | 15 |
| Servicio de Aduana | 13 |
| Controlador de Escalamiento | 12 |
| Traductor de Mensajes Externos | 10 |
| Servicio de Riesgo | 10 |
| Servicio de Tránsito | 9 |
