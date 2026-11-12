import os; os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
# Helper used once to write the .arch files from tables (kept in the package for traceability).
CONST = [
 ('CPS', 'Sistema de Gestión de Puertos del Caribe', 'Operadores portuarios de la costa Caribe'),
 ('PPS', 'Sistema de Gestión de Puertos del Pacífico', 'Operadores portuarios de la costa Pacífica'),
 ('RTS', 'Sistema de Transporte Carretero', 'Empresas transportadoras y operadores de flotas'),
 ('RLS', 'Sistema de Transporte Férreo', 'Concesionarios férreos'),
 ('FTS', 'Sistema de Transporte Fluvial', 'Operadores de navegación fluvial'),
 ('NCS', 'Sistema de Coordinación Nacional', 'Autoridad nacional (transporte, aduanas y control)'),
]
GW = [('CGW','Caribbean Port Gateway','CPS'),('PGW','Pacific Port Gateway','PPS'),('RGW','Road Gateway','RTS'),
      ('LGW','Rail Gateway','RLS'),('FGW','Fluvial Gateway','FTS'),('NCG','National Coordination Gateway','NCS')]
# Budgets of SoS-QS1 (M4) in ms, carried by one element per stage (base language of Lab 4)
LAT = {'RGW':200000,'NCG':230000,'CGW':300000,'SoS_K5':40000,'SoS_K32':10000}
D,F,E='dependency','data_flow','event_notification'
A={'cita':'Contrato de citas portuarias (v1)','ct':'Contrato de transferencia camión-tren (v1)','cb':'Contrato de transferencia camión-barcaza (v1)',
   'pt':'Contrato de transferencia puerto-tren (v1)','pb':'Contrato de transferencia puerto-barcaza (v1, v2)','ret':'Contrato de retiro por camión (v1)',
   'cus':'Semántica de custodia; clave transferId (P8)','pos':'Reporte de posición; umbral P6 y clave P8','arr':'Aviso de arribo y manifiesto (v1)',
   'lev':'Contrato de levante aduanero (v1)','est':'Contrato de estado consolidado; regla de acceso y tasa P7','avl':'Aviso de levante y de estado de servicio (v2, P2)',
   'avs':'Aviso de estado de servicio (P2)','pea':'Paso por peaje; clave P8 (P3)'}
# (id, nature, coupling, source, target, carries, agreement)
G = [
 ('SoS_K1a',D,'blocking','RGW','CGW','Solicitud de cita portuaria y programación de camión y conductor','cita'),
 ('SoS_K1b',F,'blocking','CGW','RGW','Confirmación de cita, ventana horaria y carril, o rechazo','cita'),
 ('SoS_K2a',D,'blocking','RGW','PGW','Solicitud de cita portuaria y programación de camión y conductor','cita'),
 ('SoS_K2b',F,'blocking','PGW','RGW','Confirmación de cita, ventana horaria y carril, o rechazo','cita'),
 ('SoS_K3a',D,'blocking','RGW','LGW','Solicitud de capacidad y turno de transferencia camión-tren','ct'),
 ('SoS_K3b',F,'blocking','LGW','RGW','Confirmación de programación y plataforma, o rechazo','ct'),
 ('SoS_K4a',D,'blocking','RGW','FGW','Solicitud de capacidad y turno de transferencia camión-barcaza','cb'),
 ('SoS_K4b',F,'blocking','FGW','RGW','Confirmación de muelle fluvial y horario, o rechazo','cb'),
 ('SoS_K5',E,'sink','RGW','NCG','Custodia recibida por el transportador; v3: ETA al despachar','cus'),
 ('SoS_K6',E,'supply','RGW','NCG','Posición del vehículo, estado del tránsito y eventos en ruta','pos'),
 ('SoS_K7a',D,'blocking','PGW','LGW','Unidades listas para transferencia patio-tren y solicitud de vagones','pt'),
 ('SoS_K7b',F,'blocking','LGW','PGW','Confirmación de convoy, capacidad, plataforma y ventana, o rechazo','pt'),
 ('SoS_K8',E,'sink','PGW','NCG','Arribo/zarpe de motonave y manifiesto en puertos del Pacífico','arr'),
 ('SoS_K9a',D,'blocking','PGW','NCG','Solicitud de validación de levante previa a la salida por portería','lev'),
 ('SoS_K9b',F,'blocking','NCG','PGW','Estado de levante: concedido, inspección requerida o retenido','lev'),
 ('SoS_K10a',D,'blocking','FGW','CGW','Arribo de barcaza y solicitud de muelle de transferencia','pb'),
 ('SoS_K10b',F,'blocking','CGW','FGW','Asignación de muelle de transferencia y ventana, o rechazo','pb'),
 ('SoS_K11',E,'sink','CGW','NCG','Arribo/zarpe de motonave y manifiesto en puertos del Caribe','arr'),
 ('SoS_K12a',D,'blocking','CGW','NCG','Solicitud de validación de levante previa a la salida por portería','lev'),
 ('SoS_K12b',F,'blocking','NCG','CGW','Estado de levante: concedido, inspección requerida o retenido','lev'),
 ('SoS_K13',E,'sink','LGW','NCG','Custodia recibida por el concesionario y composición del tren','cus'),
 ('SoS_K14',E,'supply','LGW','NCG','Posición del convoy, estado del corredor y eventos de vía','pos'),
 ('SoS_K15',E,'sink','FGW','NCG','Custodia recibida por el operador fluvial','cus'),
 ('SoS_K16',E,'supply','FGW','NCG','Posición de barcaza o remolcador y estado de navegación','pos'),
]
for n,gw,who in [(17,'RGW','el transportador'),(18,'LGW','el concesionario'),(19,'FGW','el operador fluvial'),(20,'PGW','el operador portuario'),(21,'CGW','el operador portuario')]:
    G.append((f'SoS_K{n}a',D,'blocking',gw,'NCG',f'Consulta de estado consolidado de la carga en la que participa {who}','est'))
    G.append((f'SoS_K{n}b',F,'blocking','NCG',gw,'Estado consolidado limitado a su carga; v3: posición y ETA estimadas','est'))
G += [
 ('SoS_K22a',D,'blocking','LGW','PGW','Aviso de convoy de exportación y solicitud de zona y ventana de descargue','pt'),
 ('SoS_K22b',F,'blocking','PGW','LGW','Zona de patio, punto y ventana de descargue, o rechazo','pt'),
 ('SoS_K23a',D,'blocking','LGW','RGW','Solicitud de camiones para retirar unidades en terminal férrea','ret'),
 ('SoS_K23b',F,'blocking','RGW','LGW','Vehículos asignados y cita de retiro, o rechazo','ret'),
 ('SoS_K24a',D,'blocking','CGW','LGW','Unidades listas para transferencia patio-tren y solicitud de vagones','pt'),
 ('SoS_K24b',F,'blocking','LGW','CGW','Confirmación de convoy, capacidad, plataforma y ventana, o rechazo','pt'),
 ('SoS_K25a',D,'blocking','LGW','CGW','Aviso de convoy de exportación y solicitud de zona y ventana de descargue','pt'),
 ('SoS_K25b',F,'blocking','CGW','LGW','Zona de patio, punto y ventana de descargue, o rechazo','pt'),
 ('SoS_K26a',D,'blocking','CGW','RGW','Solicitud de camiones para retirar unidades liberadas en el Caribe','ret'),
 ('SoS_K26b',F,'blocking','RGW','CGW','Vehículos asignados y cita de retiro, o rechazo','ret'),
 ('SoS_K27a',D,'blocking','PGW','RGW','Solicitud de camiones para retirar unidades liberadas en el Pacífico','ret'),
 ('SoS_K27b',F,'blocking','RGW','PGW','Vehículos asignados y cita de retiro, o rechazo','ret'),
 ('SoS_K28a',D,'blocking','FGW','RGW','Solicitud de camiones para retirar unidades en puerto fluvial','ret'),
 ('SoS_K28b',F,'blocking','RGW','FGW','Vehículos asignados y cita de retiro, o rechazo','ret'),
 ('SoS_K29',E,'sink','CGW','NCG','Custodia recibida por el puerto del Caribe','cus'),
 ('SoS_K30',E,'sink','PGW','NCG','Custodia recibida por el puerto del Pacífico','cus'),
 ('SoS_K31a',D,'blocking','CGW','FGW','Unidades liberadas para transferencia patio-barcaza y solicitud de capacidad','pb'),
 ('SoS_K31b',F,'blocking','FGW','CGW','Barcazas asignadas, muelle y ventana de cargue, o rechazo','pb'),
 ('SoS_K32',E,'sink','NCG','CGW','Cambio de levante en puertos del Caribe; v3: estado de servicio','avl'),
 ('SoS_K33',E,'sink','NCG','PGW','Cambio de levante en puertos del Pacífico; v3: estado de servicio','avl'),
 ('SoS_K34',E,'sink','NCG','LGW','Estado de servicio de un constituyente: degradado o restablecido','avs'),
 ('SoS_K35',E,'sink','NCG','FGW','Estado de servicio de un constituyente: degradado o restablecido','avs'),
 ('SoS_K36',E,'sink','RGW','NCG','Paso por peaje: vehículo, peaje, fecha y hora','pea'),
]
D1_GLOBAL = {'SoS_K5','SoS_K6','SoS_K8','SoS_K9a','SoS_K9b','SoS_K11','SoS_K12a','SoS_K12b','SoS_K13','SoS_K14','SoS_K15','SoS_K16'} | {f'SoS_K{n}{s}' for n in range(17,22) for s in 'ab'}
NCS_V3 = D1_GLOBAL | {'SoS_K29','SoS_K30','SoS_K32','SoS_K33','SoS_K34','SoS_K35','SoS_K36'}
def gconn(g, via=None):
    i,n,c,s,t,info,ag=g
    path = f'{s} -> {t}' if not (via and t=='NCG') else f'{s} -> {via} -> {t}'
    lat = f'  latency {LAT[i]}\n' if i in LAT else ''
    return f'connector {i} nature {n} coupling {c}\n  carries "{info}"\n  agreement "{A[ag]}"\n{lat}  : {path}\n'
def constituents(only=None):
    return ''.join(f'constituent {c} "{l}" owner "{o}"\n' for c,l,o in CONST if not only or c in only)
SOS_BASE_HEADER = '''// Model (M1) of the SoS: joint model, agreement v4 (Delivery 2, section 3)
// Written in the base language of Laboratory 4. Budgets of SoS-QS1 (M4) in ms, carried by one
// element per stage (as K18 carries stage 4 in Lab 4):
//   RGW 200 s: Carretera recovers and re-sends   SoS_K5 40 s: boundary during the re-send
//   NCG 230 s: consolidation by the NCS           SoS_K32 10 s: "restablecido" notice
//   CGW 300 s: reconciliation; the four consumers work in parallel with the same budget,
//              so the maximum is any one of them (CGW stands for the four)
'''
SOS_BASE_ANALYSIS = '''
// Analysis of SoS-QS1, measure M4 (section 3.6.6 of Delivery 2)
analysis SoSQS1M4 scenario "SoS-QS1 (M4)" latency target 900000 :
  RGW, SoS_K5, NCG, SoS_K32, CGW
'''
SOS_ANALYSES = '''
// Analyses of SoS-QS1 (section 3.6.6 of Delivery 2): composition of the agreed budgets
analysis SoSQS1M4 scenario "SoS-QS1 (M4)" deadline target 900 :
  RGW = 200, SoS_K5 = 40, NCG = 230, SoS_K32 = 10,
  [CGW = 300 | PGW = 300 | LGW = 300 | FGW = 300]
analysis SoSQS1M3 scenario "SoS-QS1 (M3)" deadline target 60 :
  RGW = 30, SoS_K36 = 10, NCG = 15
'''
# ---------- sos.arch ----------
out = [SOS_BASE_HEADER, 'system SoS\n\n', constituents(), '\n// T2 — Boundary components\n']
out += [f'component {i} "{l}" in {c} tier T2 kind software' + (f' latency {LAT[i]}' if i in LAT else '') + '\n' for i,l,c in GW]
out += ['\n// Global connectors (SoS-K1 to SoS-K36)\n'] + [gconn(g) for g in G] + [SOS_BASE_ANALYSIS]
open('models/sos.arch','w').write(''.join(out))
import json; json.dump({'G':G,'D1':sorted(D1_GLOBAL),'V3':sorted(NCS_V3)}, open('/tmp/glob.json','w'))

# ---------- constituent models of the NCS ----------
EXT = [g for g in GW if g[0] != 'NCG']
C_BASE = [
 # id, label, tier, kind, domain, extra
 ('CCC','Consola del Centro de Coordinación','T1','software','',''),
 ('CAD','Consola Aduanera','T1','software','Aduana',''),
 ('APP','Aplicación del Inspector','T1','software','Aduana',''),
 ('NCG','National Coordination Gateway','T2','software','Integracion','availability 99.9 latency 230000'),
 ('TRA','Traductor de Mensajes Externos','T2','software','Integracion','availability 99.9'),
 ('BUS','Bus de Eventos','T2','software','Integracion',''),
 ('ADP','Adaptador de Escáneres','T2','software','Aduana',''),
 ('CAR','Servicio de Carga','T3','software','Carga','availability 99.9 event_capacity 4.5 event_load 1.5'),
 ('TRS','Servicio de Tránsito','T3','software','Transito','event_capacity 60 event_load 20'),
 ('ADU','Servicio de Aduana','T3','software','Aduana','availability 99.9'),
 ('RSK','Servicio de Riesgo','T3','software','Aduana','availability 99.9'),
 ('HCDB','Historial de Carga DB','T4','software','Carga',''),
 ('RMDB','Repositorio de Manifiestos DB','T4','software','Carga','availability 99.9'),
 ('HPDB','Historial de Posiciones DB','T4','software','Transito',''),
 ('EXDB','Expediente Aduanero DB','T4','software','Aduana','availability 99.9'),
 ('SCN','Escáner de Inspección No Intrusiva','T5','physical','Aduana',''),
]
C_ADD = [
 ('BEN','Balanceador de Entrada','T2','software','Integracion','availability 99.9'),
 ('BTR','Balanceador del Traductor','T2','software','Integracion','availability 99.9'),
 ('BAD','Balanceador de Aduana','T2','software','Aduana','availability 99.9'),
 ('BRI','Balanceador de Riesgo','T2','software','Aduana','availability 99.9'),
 ('BCA','Balanceador de Carga','T2','software','Carga',''),
 ('BTS','Balanceador de Tránsito','T2','software','Transito',''),
 ('BUF','Búfer de Eventos','T2','software','Integracion',''),
 ('IDN','Servicio de Identidad','T3','software','Integracion',''),
 ('CES','Controlador de Escalamiento','T3','software','Plataforma',''),
 ('CMDB','Copia de Manifiestos DB','T4','software','Aduana',''),
 ('RADB','Registro de Auditoría DB','T4','software','Integracion',''),
 ('EXDB2','Expediente Aduanero DB (respaldo)','T4','software','Aduana','availability 99.9'),
 ('HCDBR','Historial de Carga DB (réplica de lectura)','T4','software','Carga',''),
 ('HPDBR','Historial de Posiciones DB (réplica de lectura)','T4','software','Transito',''),
]
SCALED = {'NCG','TRA','ADU','RSK','CAR','TRS'}   # 2..N instances in Delivery 2 (minimum 2)
def comp(c, e2):
    i,l,t,k,d,x = c
    extra = x + (' instances 2' if e2 and i in SCALED else '')
    dom = f' domain {d}' if d else ''
    # order of optional properties follows the grammar
    props = dict()
    toks = extra.split()
    for a,b in zip(toks[0::2], toks[1::2]): props[a]=b
    order = ['availability','latency','event_capacity','event_load','instances']
    p = ''.join(f' {o} {props[o]}' for o in order if o in props)
    return f'component {i} "{l}" in NCS tier {t} kind {k}{dom}{p}\n'
def iconn(i,n,c,info,links):
    return f'connector {i} nature {n} coupling {c}\n  carries "{info}"\n  : {links}\n'
CMD='control_command'
K_E1 = [
 ('D_K1',F,'blocking','Mensajes entrantes validados contra el CDM, con identidad del remitente','NCG -> TRA'),
 ('D_K2',F,'blocking','Respuestas en CDM: certificados de levante y estados consolidados','TRA -> NCG'),
 ('D_K3',E,'sink','Hechos operacionales: arribos, manifiestos, custodias, posiciones','TRA -> BUS'),
 ('D_K4a',D,'blocking','Solicitud de trámite de levante','TRA -> ADU'),
 ('D_K4b',F,'blocking','Resultado y certificado de levante','ADU -> TRA'),
 ('D_K5a',D,'blocking','Consulta de estado, con el constituyente solicitante','TRA -> CAR'),
 ('D_K5b',F,'blocking','Estado de la carga, solo si el solicitante participa en ella','CAR -> TRA'),
 ('D_K6',E,'sink','Arribos, manifiestos, custodias y decisiones de levante','BUS -> CAR'),
 ('D_K7',D,'blocking','Lectura y escritura de la historia de cada carga','CAR -> HCDB'),
 ('D_K8',D,'blocking','Lectura y escritura de manifiestos','CAR -> RMDB'),
 ('D_K9',E,'supply','Posiciones, estado de tránsito y eventos de viaje','BUS -> TRS'),
 ('D_K10',D,'blocking','Lectura y escritura de posiciones','TRS -> HPDB'),
 ('D_K11',E,'sink','Alertas por desvío, detención prolongada o sello comprometido','TRS -> BUS'),
 ('D_K12a',D,'blocking','Consulta de la última posición del vehículo que lleva una carga','CAR -> TRS'),
 ('D_K12b',F,'blocking','Última posición registrada','TRS -> CAR'),
 ('D_K13',E,'sink','Alertas operacionales y de tránsito','BUS -> CCC'),
 ('D_K14a',D,'blocking','Consulta del historial y estado de una carga','CCC -> CAR'),
 ('D_K14b',F,'blocking','Historia completa y estado consolidado','CAR -> CCC'),
 ('D_K15a',D,'blocking','Solicitud de evaluación de riesgo','ADU -> RSK'),
 ('D_K15b',F,'blocking','Perfil de riesgo calculado y control sugerido','RSK -> ADU'),
 ('D_K16a',D,'blocking','Solicitud de manifiesto y composición del embarque','RSK -> CAR'),
 ('D_K16b',F,'blocking','Manifiesto y actores involucrados','CAR -> RSK'),
 ('D_K17',D,'blocking','Lectura de antecedentes, sanciones e historial de inspecciones','RSK -> EXDB'),
 ('D_K18a',D,'blocking','Consulta de los casos pendientes de revisión','CAD -> ADU'),
 ('D_K18b',F,'blocking','Casos pendientes, con su evaluación de riesgo y antecedentes','ADU -> CAD'),
 ('D_K19',CMD,'blocking','Decisión del funcionario: levante, escáner o inspección física','CAD -> ADU'),
 ('D_K20',D,'blocking','Lectura y escritura del expediente','ADU -> EXDB'),
 ('D_K21',CMD,'blocking','Orden de inspección no intrusiva','ADU -> ADP'),
 ('D_K22',CMD,'blocking','Instrucción en el protocolo del fabricante','ADP -> SCN'),
 ('D_K23',F,'blocking','Imagen y lectura técnica','SCN -> ADP'),
 ('D_K24',F,'blocking','Resultado estandarizado de la inspección','ADP -> ADU'),
 ('D_K25a',D,'blocking','Consulta de las órdenes de inspección física asignadas','APP -> ADU'),
 ('D_K25b',F,'blocking','Órdenes de inspección física asignadas','ADU -> APP'),
 ('D_K26',F,'blocking','Hallazgos y verificación del sello','APP -> ADU'),
 ('D_K27',E,'sink','Decisión de levante emitida','ADU -> BUS'),
]
CHG = {  # Delivery 2, section 7.3: changed paths and information
 'D_K1':'NCG -> BTR -> TRA','D_K3':'TRA -> BUF','D_K4a':'TRA -> BAD -> ADU','D_K5a':'TRA -> BCA -> CAR','D_K6':'BUS -> BCA -> CAR',
 'D_K9':'BUS -> BTS -> TRS','D_K12a':'CAR -> BTS -> TRS','D_K13':'NCG -> CCC','D_K14a':'CCC -> BEN -> NCG','D_K14b':'NCG -> CCC',
 'D_K15a':'ADU -> BRI -> RSK','D_K16a':'RSK -> BCA -> CAR','D_K18a':'CAD -> BEN -> NCG','D_K18b':'NCG -> CAD','D_K19':'CAD -> BEN -> NCG',
 'D_K22':'NCG -> SCN','D_K23':'SCN -> BEN -> NCG','D_K24':'ADP -> BAD -> ADU','D_K25a':'APP -> BEN -> NCG','D_K25b':'NCG -> APP',
 'D_K26':'APP -> BEN -> NCG','D_K27':'ADU -> BUF',
}
INFO_CHG = {'D_K7':'Escrituras y verificación de duplicados; las lecturas van por D-K37','D_K10':'Escrituras y lectura del estado anterior; las lecturas de consultas van por D-K39',
            'D_K16a':'Solicitud de manifiesto, solo si a la Copia de Manifiestos DB le falta o no está disponible','D_K24':'Resultado estandarizado de la inspección, y aviso de falla o de plazo vencido del escáner'}
K_ADD = [
 ('D_K28',E,'supply','Arribos y manifiestos que publica el Traductor, para la copia de Riesgo','BUS -> BRI -> RSK'),
 ('D_K29',D,'blocking','Escritura y lectura de los manifiestos en la copia de Riesgo','RSK -> CMDB'),
 ('D_K30a',E,'blocking','Entrega de cada hecho guardado al Bus','BUF -> BUS'),
 ('D_K30b',F,'blocking','Confirmación de recepción del Bus','BUS -> BUF'),
 ('D_K31a',D,'blocking','Solicitudes verificadas de la Consola Aduanera y de la Aplicación del Inspector','NCG -> BAD -> ADU'),
 ('D_K31b',F,'blocking','Respuestas para las pantallas internas de Aduana','ADU -> NCG'),
 ('D_K32a',D,'blocking','Solicitudes verificadas de la Consola del Centro de Coordinación','NCG -> BCA -> CAR'),
 ('D_K32b',F,'blocking','Respuestas para la Consola del Centro de Coordinación','CAR -> NCG'),
 ('D_K33a',D,'blocking','Validación del token de cada usuario de la ruta interna','NCG -> IDN'),
 ('D_K33b',F,'blocking','Resultado de la validación del token','IDN -> NCG'),
 ('D_K34',D,'blocking','Registro de accesos, decisiones e intentos rechazados de la ruta interna','NCG -> RADB'),
 ('D_K35',F,'blocking','Copia síncrona de cada escritura del expediente','EXDB -> EXDB2'),
 ('D_K36',F,'supply','Actualización de la réplica de lectura de la historia de carga','HCDB -> HCDBR'),
 ('D_K37',D,'blocking','Lecturas de las consultas sobre la réplica','CAR -> HCDBR'),
 ('D_K38',F,'supply','Actualización de la réplica de lectura de posiciones','HPDB -> HPDBR'),
 ('D_K39',D,'blocking','Lecturas de las consultas de posición sobre la réplica','TRS -> HPDBR'),
 ('D_K40a',D,'blocking','Solicitudes repartidas entre las instancias y health check','BTR -> TRA, BAD -> ADU, BRI -> RSK, BCA -> CAR, BTS -> TRS'),
 ('D_K40b',F,'blocking','Respuestas de cada instancia y estado de salud','TRA -> BTR, ADU -> BAD, RSK -> BRI, CAR -> BCA, TRS -> BTS'),
 ('D_K41',E,'supply','Señal de vida del escáner','SCN -> BEN -> NCG'),
 ('D_K42',F,'supply','Carga observada de cada servicio','BTR -> CES, BAD -> CES, BRI -> CES, BCA -> CES, BTS -> CES'),
 ('D_K43',CMD,'sink','Orden de agregar o quitar instancias','CES -> NCG, CES -> TRA, CES -> ADU, CES -> RSK, CES -> CAR, CES -> TRS'),
 ('D_K44a',D,'blocking','Solicitudes repartidas entre las instancias del Gateway y health check','BEN -> NCG'),
 ('D_K44b',F,'blocking','Respuestas y estado de salud del Gateway','NCG -> BEN'),
 ('D_K45',F,'supply','Carga observada del Gateway','BEN -> CES'),
 ('D_K46a',CMD,'blocking','Instrucción hacia el escáner, verificada por el Gateway','ADP -> NCG'),
 ('D_K46b',F,'blocking','Imagen, lectura técnica y señal de vida del escáner','NCG -> ADP'),
 ('D_K47',E,'supply','Alertas para la Consola del Centro de Coordinación','BUS -> NCG'),
]
GBY = {g[0]: g for g in G}
def ncs_model(e2):
    head = ('// Model (M1) of the National Coordination System: resulting structure of Delivery 2\n' if e2 else
            '// Model (M1) of the National Coordination System: structure of Delivery 1, properties of Delivery 2\n')
    out = [head, 'system NCS\n\n', constituents(), '\n']
    comps = C_BASE + (C_ADD if e2 else [])
    for tier in ['T1','T2','T3','T4','T5']:
        out.append(f'// {tier}\n')
        out += [comp(c, e2) for c in comps if c[2] == tier]
        if tier == 'T2':
            out.append('// T2 — boundary components of the other constituents (as in sos.arch)\n')
            out += [f'component {i} "{l}" in {c} tier T2 kind software' + (f' latency {LAT[i]}' if i in LAT else '') + '\n' for i,l,c in EXT]
    out.append('\n// Internal connectors\n')
    for i,n,c,info,links in K_E1:
        if e2:
            links = CHG.get(i, links); info = INFO_CHG.get(i, info)
        out.append(iconn(i,n,c,info,links))
    if e2:
        out.append('\n// Connectors added in Delivery 2\n')
        out += [iconn(*k) for k in K_ADD]
    out.append('\n// Global connectors in which the NCS participates (as in sos.arch)\n')
    ids = sorted(NCS_V3 if e2 else D1_GLOBAL, key=lambda x: [g[0] for g in G].index(x))
    out += [gconn(GBY[i], via='BEN' if e2 else None) for i in ids]
    if not e2:
        out.append('''
// Analyses (Delivery 2, sections 6.1 and 8: structure before the decisions)
analysis DQS1 scenario "D-QS1" availability target 99.9 :
  NCG, TRA, ADU, RSK, CAR, RMDB, EXDB
// Backlog of a 4 h outage of Road (Delivery 2): 14400 custody events (1 ev/s), consumed
// only by CAR, and 288000 position reports (20 ev/s), consumed only by TRS.
analysis DQS10 scenario "D-QS10" recovery backlog 302400 target 230 :
  CAR = 14400, TRS = 288000
// SoS-QS1 on the starting structure: the NCS stage is the result of DQS10 in this model
// (7200 s); SoS-K32 to SoS-K36 do not exist yet, so M3 cannot be written.
analysis SoSQS1M4 scenario "SoS-QS1 (M4)" deadline target 900 :
  RGW = 200, SoS_K5 = 40, NCG = 7200,
  [CGW = 300 | PGW = 300 | LGW = 300 | FGW = 300]
''')
    else:
        out.append('''
// Analyses (Delivery 2, section 8: resulting structure)
analysis DQS1 scenario "D-QS1" availability target 99.9 :
  NCG beta 0.10, TRA beta 0.10, ADU beta 0.10, RSK beta 0.10, [EXDB | EXDB2] beta 0.10
// Same chain with the load balancers it traverses, at the availability of L17 (99.9 %)
analysis DQS1Balancers scenario "D-QS1 (with balancers)" availability target 99.9 :
  BEN, NCG beta 0.10, BTR, TRA beta 0.10, BAD, ADU beta 0.10, BRI, RSK beta 0.10, [EXDB | EXDB2] beta 0.10
// Backlog after compaction (Delivery 2): 14400 custody events, consumed only by CAR,
// and 6000 compacted position reports, consumed only by TRS.
analysis DQS10 scenario "D-QS10" recovery backlog 20400 target 230 :
  CAR = 14400, TRS = 6000
''' + SOS_ANALYSES)
    return ''.join(out)
open('models/ncs-e1.arch','w').write(ncs_model(False))
open('models/ncs-e2.arch','w').write(ncs_model(True))
