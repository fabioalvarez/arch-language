# team-D-p3 — Modelado arquitectónico del Sistema de Coordinación Nacional (NCS)

Lenguaje del Laboratorio 4 adaptado por el equipo D, modelo conjunto `sos.arch` (escrito en el lenguaje base, así que corre igual con el lenguaje de cualquier equipo),
modelos del NCS antes (`ncs-e1.arch`) y después (`ncs-e2.arch`) de la Entrega 2,
transformaciones y artefactos generados.

El lenguaje es común a los equipos: el equipo A (Puerto del Caribe, CPMS) le agregó sus adaptaciones, marcadas `[A]`, y el equipo C (Transporte Carretero, RTS) las suyas, marcadas `[C]`, sin cambiar las anteriores. Ver las secciones «Equipo A» y «Equipo C» al final.

## Ejecución

```bash
docker build -t lssa-team-d .
docker run --rm -v "$PWD:/app" lssa-team-d                      # todos los modelos de models/
docker run --rm -v "$PWD:/app" lssa-team-d invalid/c6-layers.arch  # un modelo mal formado
```

Sin argumentos se procesan todos los modelos de `models/`. Los artefactos quedan en
`out/<modelo>/`: `connectors.md`, `view.mmd` (Mermaid), `analysis.md` y `summary.md` (este último, adaptación [A]).

## Estructura

| Archivo | Contenido |
|---------|-----------|
| `arch.tx` | Gramática (M2). Adaptaciones del equipo marcadas `[D]` |
| `metamodel.py` | Restricciones C1–C15 |
| `simulation.py`, `verification.py` | Simulación y verificación (Laboratorio 5, extendido [D4]) |
| `correspondence.py` | Correspondencia entre `sos.arch` y cada modelo de constituyente (C16) |
| `tactics_check.py` | Justificación de las tácticas de la iteración 4: aporte de cada una a D-QS1, sensibilidad a β y alternativa descartada a T-R3 [D4] |
| `transformations.py` | Tabla de conectores, vista C&C y análisis |
| `generation.py` | Lee cada modelo, verifica la conformidad y aplica las transformaciones |
| `models/` | `sos.arch` (conjunto), `ncs-e1.arch`, `ncs-e2.arch`, `ncs-e4.arch` (rediseño de la Entrega 4) |
| `invalid/` | Un modelo mal formado por restricción agregada o adaptada, y los mensajes esperados |
| `out/` | Artefactos generados |
| `tools/gen_models.py` | Ayuda que escribió los modelos a partir de las tablas de la Entrega 2 |
| `team-D-p3.pdf` | Informe de la entrega |

## Adaptaciones del lenguaje

| Adaptación | Dónde | Para qué |
|------------|-------|----------|
| `domain` en componentes | Gramática, C4 | La regla de datos por dominio del NCS (Entrega 1) |
| `event_capacity`, `event_load`, `instances` | Gramática | Calcular la absorción de un rezago (D-QS10) y las réplicas de un servicio escalado (D-QS1) |
| Presupuesto por factor (`= valor`) | Gramática | Un presupuesto es un término del escenario, no una propiedad del elemento: el NCS tiene 230 s en M4 y 15 s en M3 |
| `beta` en un factor simple | Gramática, análisis | Componente con `instances` ≥ 2 y fracción de causa común, sin duplicar el componente |
| Métrica `deadline` | Análisis | Suma de presupuestos; un grupo trabaja en paralelo y cuenta su máximo (M4) |
| Métrica `recovery` con `backlog` | Análisis, C5 | Cada consumidor absorbe solo su parte del rezago (`CAR = 14400`) con su propia capacidad libre; manda el más lento: tiempo = máx(parteᵢ / (capacidadᵢ × instanciasᵢ − cargaᵢ)). Corregido tras la Entrega 3: antes se sumaban capacidades de consumidores distintos |

## Restricciones

| ID | Restricción | Origen | Modelo rechazado |
|----|-------------|--------|------------------|
| C1–C2 | Sin cambios (Laboratorio 4) | — | — |
| C3 (corregida) | Todo conector de frontera tiene acuerdo, y cada tramo que cruza la frontera une dos componentes T2: un conector con acuerdo conectado directo a un T3 o T4 se rechaza. Mismo mensaje que C8 [A] | Corrección de la Entrega 3 | `c3-boundary-tier.arch` |
| C4 (adaptada) | Un almacén T4 solo se accede por dependencia desde componentes de su dominio; sin dominio, rige la regla del Laboratorio 4 | Regla de datos por dominio del NCS | `c4-domain.arch`, `c4-lab4-rule.arch` |
| C5 (extendida) | Cada factor tiene la propiedad que su métrica necesita, incluidas `deadline` y `recovery`; en `recovery` con varios consumidores, cada uno lleva su parte del rezago y las partes suman el rezago | U5, Lectura 2, §4.2; corrección de la Entrega 3 | `c5-deadline.arch`, `c5-recovery.arch`, `c5-recovery-shares.arch` |
| C6 (nueva, estilo) | Ningún componente T1 se une directamente a un almacén T4 | Estilo **en capas** del NCS (Entrega 1, §5) | `c6-layers.arch` |
| C7 (nueva, estilo) | Ningún comando de control cruza la frontera de un constituyente | SoS **reconocido**: estilo jerárquico solo donde la autoridad es real (Entrega 1, nivel global) | `c7-command.arch` |

## Convenciones

- Identificadores: `SoS-K5` se escribe `SoS_K5` y `D-K1` se escribe `D_K1`, porque el guion no es válido en un identificador (como `K2a′` → `K2a2` en el Laboratorio 4).
- Los componentes de frontera de los otros constituyentes aparecen en los modelos del NCS como en `sos.arch`. En `ncs-e2.arch`, los conectores globales entrantes pasan por el Balanceador de Entrada (`X -> BEN -> NCG`), como dice la sección 7.3 de la Entrega 2; su ID, naturaleza, acoplamiento y acuerdo son los de `sos.arch`.
- Un par solicitud/respuesta se clasifica como bloqueante en sus dos conectores. D-K1, que en la Entrega 2 es bloqueante para solicitudes y sumidero para eventos, se clasifica como bloqueante (la más restrictiva).
- Disponibilidad de 99,9 % (L17) en cada elemento que entra en una cadena. `event_capacity` = 3 veces la carga normal (L19), repartida entre los consumidores del Bus: Carga 1,5 → 4,5 eventos/s y Tránsito 20 → 60 eventos/s.
- `sos.arch` usa solo el lenguaje base. Los presupuestos de M4 van en ms y cada tramo lo lleva un elemento distinto, como K18 lleva la etapa 4 en el Laboratorio 4: RGW 200 s, SoS-K5 40 s, NCG 230 s, SoS-K32 10 s y CGW 300 s. CGW representa a los cuatro consumidores, que tienen el mismo presupuesto y trabajan en paralelo. M3 no cabe en el lenguaje base (RGW y NCG necesitarían un segundo valor): se analiza en los modelos del NCS con la métrica `deadline`. Los modelos del NCS repiten esas latencias en los elementos de frontera, que se escriben como en `sos.arch`.
- Partes del rezago de D-QS10 (Entrega 2, caída de Carretera de 4 h): 14.400 custodias (1 ev/s), que consume solo CAR, más 288.000 posiciones (20 ev/s) en e1 o 6.000 posiciones compactadas en e2, que consume solo TRS.
- En `ncs-e1.arch`, el tramo del NCS en M4 toma el resultado de `DQS10` en ese mismo modelo (7.200 s). M3 no se puede escribir porque SoS-K36 todavía no existe.

## Resultados

| Escenario | Antes (e1) | Después (e2) | Entrega 2 | Diferencia |
|-----------|-----------|--------------|-----------|------------|
| D-QS1 | 99,30 %, no cumple | 99,95 %, cumple | 99,30 % → 99,95 % | Ninguna |
| D-QS1 con balanceadores | — | 99,55 %, no cumple | No calculado | La Entrega 2 no contó los 4 balanceadores que la cadena atraviesa, cada uno sin copia |
| D-QS10 (corregido) | 7.200 s (TRS), no cumple | 1.920 s (CAR), no cumple | ≈ 7.030 s → ≈ 190 s | La Entrega 2 y la Entrega 3 sumaban la capacidad libre de CAR y TRS (189,8 s); cada uno solo consume su clase de evento |
| SoS-QS1 (M4), `sos.arch` | — | 780.000 ms, cumple | 780 s | Ninguna; lenguaje base |
| SoS-QS1 (M4), modelos del NCS | 7.740 s, no cumple | 780 s con el presupuesto acordado (NCG = 230 s); con la medida corregida de D-QS10 (1.920 s) serían 2.470 s, no cumple | Sin cifra → 780 s | Pendiente para la P4: la medida del NCS supera su presupuesto |
| SoS-QS1 (M3), modelos del NCS | No aplica (SoS-K36 no existe) | 55 s, cumple | 55 s | Ninguna; no se puede escribir en `sos.arch` con el lenguaje base |

## Entrega 4 — Verificación (equipo D)

El lenguaje se extiende con lo que la verificación necesita, siguiendo el Laboratorio 5. Todo es opcional: los modelos de la Entrega 3 y los de los equipos A y C siguen siendo válidos.

### Ejecución

```bash
docker build -f Dockerfile.verification -t lssa-team-d-verif .
docker run --rm -v "$PWD:/app" lssa-team-d-verif                       # models/ncs-e1, e2 y e4
docker run --rm -v "$PWD:/app" lssa-team-d-verif models/ncs-e4.arch    # un modelo
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-d-verif \
  correspondence.py models/sos.arch models/ncs-e2.arch models/ncs-e4.arch
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-d-verif tactics_check.py   # out/tactics/tactics.md
```

Cada modelo deja en `out/<modelo>/` el grafo (`graph.png`) y el informe (`verification.md`). Cada corrida tarda menos de un minuto.

### Extensiones del lenguaje

| Extensión | Marca | Para qué |
|-----------|-------|----------|
| `capacity` y `store` en componentes | [L5] | Tasa de servicio de una instancia; un `store` retiene los trabajos mientras el siguiente componente está caído |
| `scenario` con `workload`, `fault`, `vary`, `measure` y `run` | [L5] | Simular un escenario sobre la estructura del modelo, con réplicas y semillas |
| Seis partes del escenario: `source`, `stimulus`, `artifact`, `environment`, `response`, más `attribute` | [D4] | El escenario como elemento del modelo; el artefacto refiere elementos del modelo |
| `verified_by` y `not_verifiable` | [D4] | La medida de un escenario se simula, se verifica con un análisis del modelo, o se declara no verificable con lo que falta |
| `tactic ... for ... introduces ... changes ...` | [D4] | Cada táctica ligada a los escenarios que la motivan y a los elementos que introduce o cambia |
| `compact n` en una carga | [D4] | Compactación de la Entrega 2: mientras un store retiene la carga, solo quedan sus últimos n eventos |
| `mttr` en un análisis | [D4] | Tiempo medio de reparación para simular la disponibilidad (4 h por defecto) |

Diferencias con el simulador del Laboratorio 5, todas [D4]: la capacidad de un componente es `capacity` (o `event_capacity`) × `instances`; un store que está caído retiene lo que recibe (la salida de Carretera mientras cae); la recuperación se mide en el último componente de cada carga, y sin carga se toma la más lenta, porque los consumidores de clases de evento distintas no son intercambiables; y la disponibilidad de los análisis que un escenario nombra en `verified_by` se simula por Monte Carlo, con la fórmula del Laboratorio 3 como caso de resultado conocido.

### Restricciones nuevas

C6 y C7 del Laboratorio 5 ya estaban ocupadas (capas y comandos, Entrega 3), así que aquí son C12 y C13.

| ID | Restricción | Origen | Modelo rechazado |
|----|-------------|--------|------------------|
| C12 | Cada tramo de una carga sigue un conector del modelo | Laboratorio 5, C6 | `c12-workload-hop.arch` |
| C13 | Un componente que falla en un escenario tiene capacidad | Laboratorio 5, C7 | `c13-fault-capacity.arch` |
| C14 | Un escenario de calidad tiene sus seis partes, y su medida se simula, se verifica con un análisis o se declara no verificable | Entrega 4, §3.1 | `c14-six-parts.arch` |
| C15 | Una táctica cambia o introduce algún elemento y la motiva un escenario cuya medida se verifica | Entrega 4, §3.1; Laboratorio 5, §6 | `c15-tactic-unverified.arch` |
| C16 (correspondencia) | `correspondence.py`: los componentes de frontera y los conectores globales de un modelo de constituyente coinciden con `sos.arch` (K1 componentes, K2 naturaleza, acoplamiento, información, acuerdo y extremos de frontera; K3 ningún conector global falta) | Entrega 4, §3.1 | `k2-correspondence.arch` |

`ncs-e2.arch` y `ncs-e4.arch` corresponden con `sos.arch`. `ncs-e1.arch` no: le faltan SoS-K29 a SoS-K36, que el acuerdo v4 agregó en la Entrega 2 después de la estructura de partida.

### Resultados

| Propiedad | e1 | e2 | e4 (rediseño) |
|-----------|----|----|---------------|
| S1 en el artefacto de D-QS1 | Violada: 7 elementos únicos | Violada: BEN, BTR, BAD, BRI | Satisfecha |
| D-QS1, Monte Carlo (40 × 20 años) | 99,305 % [99,285; 99,325], violada | 99,549 % [99,536; 99,563] con balanceadores, violada | 99,957 % [99,953; 99,961], con margen |
| D-QS10, recuperación (10 réplicas, semillas 1–10) | 7.211,2 s (TRS) [7.194,8; 7.227,6], violada | 1.932,8 s (CAR) [1.921,5; 1.944,1], violada | 184,9 s [183,8; 186,1], con margen |
| Custodias perdidas | 0 | 0 | 0 |

La simulación es determinista: con las mismas semillas da las mismas cifras en cada corrida (antes, `_stations` recorría un `set` de componentes y el orden de las estaciones, y con él las cifras de recuperación, cambiaba entre procesos).

Valores conocidos. Disponibilidad: la fórmula del Laboratorio 3 cae dentro de los tres intervalos. Recuperación: el vaciado exacto de una cola M/M/1 que empieza con n trabajos es n / (μ − λ), y la medida agrega la espera hasta la primera llegada nueva, 1/λ (0,67 s para CAR, 0,05 s para TRS). Con eso, e1 da 7.200,1 s y e4 184,1 s, dentro de sus intervalos; e2 da 1.920,7 s, 0,8 s por debajo del suyo. El reenvío de RGW no agrega tiempo: con capacidad ilimitada en RGW la medida no cambia.

En e4, la sensibilidad a la capacidad de CAR por instancia da violada hasta 32,1 ev/s (231,7 s [230,5; 233,0]), satisfecha sin margen en 35 ev/s (212,2 s [211,3; 213,0]) y con margen desde 40 ev/s.

### Tácticas de la iteración 4

`tactics_check.py` lee `ncs-e2.arch` y `ncs-e4.arch` y deja en `out/tactics/tactics.md` tres tablas que justifican el rediseño:

| Pregunta | Resultado |
|----------|-----------|
| ¿Hacen falta T-R1 y T-R2 a la vez? | e2 99,549 % (violada); e2 + T-R1 99,906 % [99,900; 99,912] (inconclusa); e2 + T-R2 99,563 % (violada); e4 99,957 % (con margen). Las dos son necesarias |
| ¿Hasta qué β aguanta e4? | Con margen hasta β = 0,08; sin margen hasta 0,10; inconclusa en 0,11–0,12; violada en 0,15. Límite analítico del margen: β ≈ 0,088 |
| ¿Por qué lotes y no más instancias de CAR? | Con 4,5 ev/s por instancia hacen falta 15 instancias (220,0 s, sin margen); con 14, violada |

## Equipo A — Sistema de Gestión de Puertos del Caribe (CPMS)

El equipo A modela el constituyente `CPS` con el mismo lenguaje de este repositorio. Sus adaptaciones están marcadas `[A]` en `arch.tx`, `metamodel.py` y `transformations.py`. Todas son adiciones, así que los modelos del equipo D y `sos.arch` siguen dando exactamente los mismos artefactos y sus modelos mal formados se rechazan con los mismos mensajes.

### Archivos

| Archivo | Contenido |
|---------|-----------|
| `models/cpms-l1.arch` | Estructura de partida: la de la Entrega 1 (44 componentes, 88 conectores internos) con las propiedades de la Entrega 2 (L1 a L24) |
| `models/cpms-l3.arch` | Estructura resultante de la Entrega 2: T2.8, T2.9, A-K85' y A-K89 a A-K98 (numeración de la corrección 2.1, §4.1), e `instances 2` en T2.1, T2.5, T3.6 y T3.9 |
| `invalid/cpms-*.arch` | Un modelo mal formado por restricción del equipo (C8, C9, C10) y el caso de C4 del feedback de la Entrega 1; los mensajes están en `invalid/expected-rejections.txt` |
| `tools/make_invalid_cpms.py` | Escribe `invalid/cpms-*.arch` a partir de `models/cpms-l1.arch`, con un solo cambio en cada uno |
| `out/cpms-l1/`, `out/cpms-l3/` | Artefactos generados, incluido `summary.md` |

Se generan con el mismo comando del repositorio (`docker run --rm -v "$PWD:/app" lssa-team-d`, o `python generation.py`). Los modelos mal formados se regeneran con `python tools/make_invalid_cpms.py`.

### Adaptaciones del lenguaje [A]

| Adaptación | Dónde | Para qué |
|------------|-------|----------|
| Identificadores de las entregas (`T2.1`, `A-K70`, `A-K85'`) | Gramática (`Ident`), vista | Trazabilidad directa con las Entregas 1 y 2. Todo identificador del lenguaje base sigue siendo válido; la vista Mermaid convierte `.`, `-` y `'` en `_` |
| `event_capacity` y `event_load` también en conectores | Gramática | La tasa de consultas de SoS-K21a frente al tope de 2 por segundo de P7 (A-QS6) |
| Métrica `utilization` | Gramática, C5, análisis | Carga / (capacidad × instancias) del elemento más cargado: T2.5 a 20 eventos/s con 10 por instancia (A-QS4) |
| `replicas n` en un factor | Gramática, C5, análisis | Evaluar como par un elemento que en la estructura tiene una sola instancia, sin cambiar la estructura: el «antes» de la Entrega 2 ya suponía pares |
| `summary.md` | Transformaciones | Conteos por tier, por acoplamiento y por naturaleza, que reproducen las tablas de las Entregas 1 y 2 |
| Artefactos en UTF-8 y LF | Transformaciones | Los mismos bytes en Docker y en Windows |

Lo demás ya estaba en el lenguaje y se usa tal cual: el presupuesto por factor (`= valor`), `beta` sobre un componente con `instances` y la métrica `deadline`.

### Restricciones [A]

| ID | Restricción | Origen (Entrega 1 del CPMS) | Alcance | Modelo rechazado |
|----|-------------|-----------------------------|---------|------------------|
| C8 | Todo enlace que cruza una frontera empieza y termina en un componente T2 | Patrón gateway (§3.2 y §3.5) | Global | `cpms-c8-boundary-not-at-gateway.arch` |
| C9 | Un equipo físico (T5) recibe comandos de control de un solo componente | Estilo jerárquico y lazo de control (§5.2) | Constituyente `CPS` | `cpms-c9-equipment-with-two-authorities.arch` |
| C10 | Una notificación de evento nunca es bloqueante | Estilo orientado a eventos | Constituyente `CPS` | `cpms-c10-event-with-blocking-coupling.arch` |

C9 y C10 se revisan solo dentro de `CPS`, porque un estilo se atribuye a una parte delimitada de la estructura y no a todo el SoS (el NCS, por ejemplo, tiene un outbox bloqueante en `D_K30a`). La regla de C7 del equipo D (ningún comando cruza la frontera) ya cubre la del CPMS y no se repite.

`cpms-c4-store-shared.arch` reproduce la observación del feedback de la Entrega 1: T3.12 lee T4.2 sin pasar por T3.1. C4 lo rechaza con `T4.2: data store shared by ['T3.1', 'T3.12']`. Los dos modelos del CPMS ya traen esa corrección.

### Convenciones

- Los componentes internos conservan el identificador de la Entrega 1 (`T1.1` … `T5.10`). Los conectores internos van de `A-K1` a `A-K98`, con `'` para los modificados (`A-K85'`).
- Los componentes de frontera y los 19 conectores globales del CPMS se copian de `sos.arch` con su texto, acuerdo, acoplamiento y latencia. Solo se añaden las propiedades que `sos.arch` no trae y que piden los análisis del equipo: la disponibilidad de CGW, de NCG y de los enlaces (L9 a L11), y la capacidad y la carga de SoS_K21a (P7).
- `SoS_K5` entra en los modelos del CPMS porque es una etapa de SoS-QS1 (M4), aunque no toca al puerto. Por eso `summary.md` cuenta 20 conectores de frontera.
- Acoplamiento de los conectores globales: se sigue la convención de `sos.arch` (un par solicitud/respuesta es bloqueante en sus dos conectores). La Entrega 2 (§4.1) había clasificado como suministro las respuestas K1b, K10b, K12b, K21b, K24b, K25b, K26b y K31b, y también K32.
- Disponibilidad en %, tasas por segundo, `latency` en ms y `deadline` en s. Las metas de disponibilidad de A-QS2 (99,9 %) y del par de T2.5 (99,99 %) son supuestas: la Entrega 2 no las fija.

### Resultados

| Escenario | Antes (l1) | Después (l3) | Entrega 2 | Diferencia |
|-----------|-----------|--------------|-----------|------------|
| A-QS2: disponibilidad de la salida (C1) | 99,70 % (26,2 h/año), no cumple | 99,99 % (0,7 h/año), cumple | 99,84 % → 99,992 % | Antes: la Entrega 2 ya suponía pares de T2.1, T3.6 y T3.9. Con esos pares (`replicas 2`), l1 da 99,84 % (13,8 h/año), igual que la Entrega 2 |
| A-QS4: utilización de T2.5 a 20 eventos/s | 200 %, no cumple | 100 %, cumple | 2 instancias de 10 eventos/s | Ninguna |
| A-QS4: disponibilidad del par de T2.5 | — | 99,99 % (0,4 h/año; 0,0051 % de indisponibilidad), cumple | 99,9949 % | Ninguna |
| A-QS4: latencia lectura → T3.6 (3 saltos de 50 ms, L14) | 150 ms | 150 ms, cumple | Meta ≤ 200 ms | La suma solo vale sin saturación: en l1, T2.5 está al 200 % |
| A-QS6: consultas a SoS-K21a | 75 %, cumple | 75 %, cumple | 1,5 de 2 consultas/s | Ninguna |
| A-QS6: reconciliación de 120 citas | 60 s (120 s con reintento), cumple | 60 s (120 s), cumple | 60 s / 120 s ≤ 300 s | Ninguna |
| SoS-QS1 (M4) | 780.000 ms, cumple | 780.000 ms, cumple | 780 s | Ninguna |

## Adaptaciones del lenguaje [C] — Equipo C (Transporte Carretero, RTS)

Las adaptaciones del metamodelo del equipo C están marcadas `[C]` en `arch.tx`, `metamodel.py` y `transformations.py` (reutilizando `event_load`, `event_capacity`, `= valor` y `Group` del lenguaje común):

| Adaptación | Dónde | Para qué |
|------------|-------|----------|
| Propiedades `period`, `misses`, `buffer` | Gramática | Detección de silencio periódico (RTS-QS4, P6) y capacidad de retención en cola (RTS-QS1, M4) |
| Métricas `detection` y `drain` (con `outage`) | Gramática, C5, análisis | `detection` suma `period × misses` y latencia (`period 0` = silencio no detectable, ∞); `drain` calcula eventos perdidos y tiempo de drenado `kept / (event_capacity - event_load)` |
| Presupuestos (`= valor`) y grupos (`[A \| B]`) también en `latency` | C5, análisis | Evaluar tramos con presupuesto propio y etapas en paralelo en ms |
| `auto_init_attributes=False` | Metamodelo | Distinguir una propiedad no declarada (`None`, error de C5) de una declarada con valor `0` (`period 0`, `buffer 0`) |
| Restricciones C5 (extendida), C7, C8, C10 (`RTS`) y C11 (cliente-servidor `T1 -> T2` en `RTS`) | Metamodelo | Validar estilos arquitectónicos del RTS y consistencia de los grupos de análisis |
