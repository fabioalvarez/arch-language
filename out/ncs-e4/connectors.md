# Connectors of NCS

| ID | Source → Target | Nature | Coupling | Information carried | Boundary |
|----|-----------------|--------|----------|---------------------|----------|
| D_K1 | National Coordination Gateway → Balanceador del Traductor → Traductor de Mensajes Externos | Data flow | Blocking | Mensajes entrantes validados contra el CDM, con identidad del remitente | No |
| D_K2 | Traductor de Mensajes Externos → National Coordination Gateway | Data flow | Blocking | Respuestas en CDM: certificados de levante y estados consolidados | No |
| D_K3 | Traductor de Mensajes Externos → Búfer de Eventos | Event notification | Sink | Hechos operacionales: arribos, manifiestos, custodias, posiciones | No |
| D_K4a | Traductor de Mensajes Externos → Balanceador de Aduana → Servicio de Aduana | Dependency | Blocking | Solicitud de trámite de levante | No |
| D_K4b | Servicio de Aduana → Traductor de Mensajes Externos | Data flow | Blocking | Resultado y certificado de levante | No |
| D_K5a | Traductor de Mensajes Externos → Balanceador de Carga → Servicio de Carga | Dependency | Blocking | Consulta de estado, con el constituyente solicitante | No |
| D_K5b | Servicio de Carga → Traductor de Mensajes Externos | Data flow | Blocking | Estado de la carga, solo si el solicitante participa en ella | No |
| D_K6 | Bus de Eventos → Balanceador de Carga → Servicio de Carga | Event notification | Sink | Arribos, manifiestos, custodias y decisiones de levante | No |
| D_K7 | Servicio de Carga → Historial de Carga DB | Dependency | Blocking | Escrituras y verificación de duplicados; las lecturas van por D-K37 | No |
| D_K8 | Servicio de Carga → Repositorio de Manifiestos DB | Dependency | Blocking | Lectura y escritura de manifiestos | No |
| D_K9 | Bus de Eventos → Balanceador de Tránsito → Servicio de Tránsito | Event notification | Supply | Posiciones, estado de tránsito y eventos de viaje | No |
| D_K10 | Servicio de Tránsito → Historial de Posiciones DB | Dependency | Blocking | Escrituras y lectura del estado anterior; las lecturas de consultas van por D-K39 | No |
| D_K11 | Servicio de Tránsito → Bus de Eventos | Event notification | Sink | Alertas por desvío, detención prolongada o sello comprometido | No |
| D_K12a | Servicio de Carga → Balanceador de Tránsito → Servicio de Tránsito | Dependency | Blocking | Consulta de la última posición del vehículo que lleva una carga | No |
| D_K12b | Servicio de Tránsito → Servicio de Carga | Data flow | Blocking | Última posición registrada | No |
| D_K13 | National Coordination Gateway → Consola del Centro de Coordinación | Event notification | Sink | Alertas operacionales y de tránsito | No |
| D_K14a | Consola del Centro de Coordinación → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta del historial y estado de una carga | No |
| D_K14b | National Coordination Gateway → Consola del Centro de Coordinación | Data flow | Blocking | Historia completa y estado consolidado | No |
| D_K15a | Servicio de Aduana → Balanceador de Riesgo → Servicio de Riesgo | Dependency | Blocking | Solicitud de evaluación de riesgo | No |
| D_K15b | Servicio de Riesgo → Servicio de Aduana | Data flow | Blocking | Perfil de riesgo calculado y control sugerido | No |
| D_K16a | Servicio de Riesgo → Balanceador de Carga → Servicio de Carga | Dependency | Blocking | Solicitud de manifiesto, solo si a la Copia de Manifiestos DB le falta o no está disponible | No |
| D_K16b | Servicio de Carga → Servicio de Riesgo | Data flow | Blocking | Manifiesto y actores involucrados | No |
| D_K17 | Servicio de Riesgo → Expediente Aduanero DB | Dependency | Blocking | Lectura de antecedentes, sanciones e historial de inspecciones | No |
| D_K18a | Consola Aduanera → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de los casos pendientes de revisión | No |
| D_K18b | National Coordination Gateway → Consola Aduanera | Data flow | Blocking | Casos pendientes, con su evaluación de riesgo y antecedentes | No |
| D_K19 | Consola Aduanera → Balanceador de Entrada → National Coordination Gateway | Control command | Blocking | Decisión del funcionario: levante, escáner o inspección física | No |
| D_K20 | Servicio de Aduana → Expediente Aduanero DB | Dependency | Blocking | Lectura y escritura del expediente | No |
| D_K21 | Servicio de Aduana → Adaptador de Escáneres | Control command | Blocking | Orden de inspección no intrusiva | No |
| D_K22 | National Coordination Gateway → Escáner de Inspección No Intrusiva | Control command | Blocking | Instrucción en el protocolo del fabricante | No |
| D_K23 | Escáner de Inspección No Intrusiva → Balanceador de Entrada → National Coordination Gateway | Data flow | Blocking | Imagen y lectura técnica | No |
| D_K24 | Adaptador de Escáneres → Balanceador de Aduana → Servicio de Aduana | Data flow | Blocking | Resultado estandarizado de la inspección, y aviso de falla o de plazo vencido del escáner | No |
| D_K25a | Aplicación del Inspector → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de las órdenes de inspección física asignadas | No |
| D_K25b | National Coordination Gateway → Aplicación del Inspector | Data flow | Blocking | Órdenes de inspección física asignadas | No |
| D_K26 | Aplicación del Inspector → Balanceador de Entrada → National Coordination Gateway | Data flow | Blocking | Hallazgos y verificación del sello | No |
| D_K27 | Servicio de Aduana → Búfer de Eventos | Event notification | Sink | Decisión de levante emitida | No |
| D_K28 | Bus de Eventos → Balanceador de Riesgo → Servicio de Riesgo | Event notification | Supply | Arribos y manifiestos que publica el Traductor, para la copia de Riesgo | No |
| D_K29 | Servicio de Riesgo → Copia de Manifiestos DB | Dependency | Blocking | Escritura y lectura de los manifiestos en la copia de Riesgo | No |
| D_K30a | Búfer de Eventos → Bus de Eventos | Event notification | Blocking | Entrega de cada hecho guardado al Bus | No |
| D_K30b | Bus de Eventos → Búfer de Eventos | Data flow | Blocking | Confirmación de recepción del Bus | No |
| D_K31a | National Coordination Gateway → Balanceador de Aduana → Servicio de Aduana | Dependency | Blocking | Solicitudes verificadas de la Consola Aduanera y de la Aplicación del Inspector | No |
| D_K31b | Servicio de Aduana → National Coordination Gateway | Data flow | Blocking | Respuestas para las pantallas internas de Aduana | No |
| D_K32a | National Coordination Gateway → Balanceador de Carga → Servicio de Carga | Dependency | Blocking | Solicitudes verificadas de la Consola del Centro de Coordinación | No |
| D_K32b | Servicio de Carga → National Coordination Gateway | Data flow | Blocking | Respuestas para la Consola del Centro de Coordinación | No |
| D_K33a | National Coordination Gateway → Servicio de Identidad | Dependency | Blocking | Validación del token de cada usuario de la ruta interna | No |
| D_K33b | Servicio de Identidad → National Coordination Gateway | Data flow | Blocking | Resultado de la validación del token | No |
| D_K34 | National Coordination Gateway → Registro de Auditoría DB | Dependency | Blocking | Registro de accesos, decisiones e intentos rechazados de la ruta interna | No |
| D_K35 | Expediente Aduanero DB → Expediente Aduanero DB (respaldo) | Data flow | Blocking | Copia síncrona de cada escritura del expediente | No |
| D_K36 | Historial de Carga DB → Historial de Carga DB (réplica de lectura) | Data flow | Supply | Actualización de la réplica de lectura de la historia de carga | No |
| D_K37 | Servicio de Carga → Historial de Carga DB (réplica de lectura) | Dependency | Blocking | Lecturas de las consultas sobre la réplica | No |
| D_K38 | Historial de Posiciones DB → Historial de Posiciones DB (réplica de lectura) | Data flow | Supply | Actualización de la réplica de lectura de posiciones | No |
| D_K39 | Servicio de Tránsito → Historial de Posiciones DB (réplica de lectura) | Dependency | Blocking | Lecturas de las consultas de posición sobre la réplica | No |
| D_K40a | Balanceador del Traductor → Traductor de Mensajes Externos; Balanceador de Aduana → Servicio de Aduana; Balanceador de Riesgo → Servicio de Riesgo; Balanceador de Carga → Servicio de Carga; Balanceador de Tránsito → Servicio de Tránsito | Dependency | Blocking | Solicitudes repartidas entre las instancias y health check | No |
| D_K40b | Traductor de Mensajes Externos → Balanceador del Traductor; Servicio de Aduana → Balanceador de Aduana; Servicio de Riesgo → Balanceador de Riesgo; Servicio de Carga → Balanceador de Carga; Servicio de Tránsito → Balanceador de Tránsito | Data flow | Blocking | Respuestas de cada instancia y estado de salud | No |
| D_K41 | Escáner de Inspección No Intrusiva → Balanceador de Entrada → National Coordination Gateway | Event notification | Supply | Señal de vida del escáner | No |
| D_K42 | Balanceador del Traductor → Controlador de Escalamiento; Balanceador de Aduana → Controlador de Escalamiento; Balanceador de Riesgo → Controlador de Escalamiento; Balanceador de Carga → Controlador de Escalamiento; Balanceador de Tránsito → Controlador de Escalamiento | Data flow | Supply | Carga observada de cada servicio | No |
| D_K43 | Controlador de Escalamiento → National Coordination Gateway; Controlador de Escalamiento → Traductor de Mensajes Externos; Controlador de Escalamiento → Servicio de Aduana; Controlador de Escalamiento → Servicio de Riesgo; Controlador de Escalamiento → Servicio de Carga; Controlador de Escalamiento → Servicio de Tránsito | Control command | Sink | Orden de agregar o quitar instancias | No |
| D_K44a | Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Solicitudes repartidas entre las instancias del Gateway y health check | No |
| D_K44b | National Coordination Gateway → Balanceador de Entrada | Data flow | Blocking | Respuestas y estado de salud del Gateway | No |
| D_K45 | Balanceador de Entrada → Controlador de Escalamiento | Data flow | Supply | Carga observada del Gateway | No |
| D_K46a | Adaptador de Escáneres → National Coordination Gateway | Control command | Blocking | Instrucción hacia el escáner, verificada por el Gateway | No |
| D_K46b | National Coordination Gateway → Adaptador de Escáneres | Data flow | Blocking | Imagen, lectura técnica y señal de vida del escáner | No |
| D_K47 | Bus de Eventos → National Coordination Gateway | Event notification | Supply | Alertas para la Consola del Centro de Coordinación | No |
| SoS_K5 | Road Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Custodia recibida por el transportador; v3: ETA al despachar | Yes |
| SoS_K6 | Road Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Supply | Posición del vehículo, estado del tránsito y eventos en ruta | Yes |
| SoS_K8 | Pacific Port Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Arribo/zarpe de motonave y manifiesto en puertos del Pacífico | Yes |
| SoS_K9a | Pacific Port Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Solicitud de validación de levante previa a la salida por portería | Yes |
| SoS_K9b | National Coordination Gateway → Pacific Port Gateway | Data flow | Blocking | Estado de levante: concedido, inspección requerida o retenido | Yes |
| SoS_K11 | Caribbean Port Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Arribo/zarpe de motonave y manifiesto en puertos del Caribe | Yes |
| SoS_K12a | Caribbean Port Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Solicitud de validación de levante previa a la salida por portería | Yes |
| SoS_K12b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado de levante: concedido, inspección requerida o retenido | Yes |
| SoS_K13 | Rail Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Custodia recibida por el concesionario y composición del tren | Yes |
| SoS_K14 | Rail Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Supply | Posición del convoy, estado del corredor y eventos de vía | Yes |
| SoS_K15 | Fluvial Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Custodia recibida por el operador fluvial | Yes |
| SoS_K16 | Fluvial Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Supply | Posición de barcaza o remolcador y estado de navegación | Yes |
| SoS_K17a | Road Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el transportador | Yes |
| SoS_K17b | National Coordination Gateway → Road Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K18a | Rail Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el concesionario | Yes |
| SoS_K18b | National Coordination Gateway → Rail Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K19a | Fluvial Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador fluvial | Yes |
| SoS_K19b | National Coordination Gateway → Fluvial Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K20a | Pacific Port Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador portuario | Yes |
| SoS_K20b | National Coordination Gateway → Pacific Port Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K21a | Caribbean Port Gateway → Balanceador de Entrada → National Coordination Gateway | Dependency | Blocking | Consulta de estado consolidado de la carga en la que participa el operador portuario | Yes |
| SoS_K21b | National Coordination Gateway → Caribbean Port Gateway | Data flow | Blocking | Estado consolidado limitado a su carga; v3: posición y ETA estimadas | Yes |
| SoS_K29 | Caribbean Port Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Custodia recibida por el puerto del Caribe | Yes |
| SoS_K30 | Pacific Port Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Custodia recibida por el puerto del Pacífico | Yes |
| SoS_K32 | National Coordination Gateway → Caribbean Port Gateway | Event notification | Sink | Cambio de levante en puertos del Caribe; v3: estado de servicio | Yes |
| SoS_K33 | National Coordination Gateway → Pacific Port Gateway | Event notification | Sink | Cambio de levante en puertos del Pacífico; v3: estado de servicio | Yes |
| SoS_K34 | National Coordination Gateway → Rail Gateway | Event notification | Sink | Estado de servicio de un constituyente: degradado o restablecido | Yes |
| SoS_K35 | National Coordination Gateway → Fluvial Gateway | Event notification | Sink | Estado de servicio de un constituyente: degradado o restablecido | Yes |
| SoS_K36 | Road Gateway → Balanceador de Entrada → National Coordination Gateway | Event notification | Sink | Paso por peaje: vehículo, peaje, fecha y hora | Yes |
