import streamlit as st
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4

VERSION_REGLAS = 'ELA-AUD-2.0-prototipo'

def crear_pdf(registro):
    salida = BytesIO()
    doc = SimpleDocTemplate(salida, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=42)
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(name='CuerpoELA', parent=estilos['Normal'], fontSize=8.5, leading=12, spaceAfter=5))
    estilos.add(ParagraphStyle(name='TituloELA', parent=estilos['Heading1'], fontSize=15, leading=19, spaceAfter=12))
    estilos.add(ParagraphStyle(name='CabeceraELA', parent=estilos['Heading2'], fontSize=10, spaceBefore=12, spaceAfter=6))
    cuerpo = estilos['CuerpoELA']
    def par(x):
        return Paragraph(escape(str(x)).replace('\n', '<br/>'), cuerpo)
    contenido = [Paragraph('Informe de evaluación preliminar de edaravona en ELA', estilos['TituloELA']),
                 par('PROTOTIPO — DATOS FICTICIOS. No válido para decisiones asistenciales ni documentación real.'),
                 par('ID: ' + registro['id'] + ' | Fecha UTC: ' + registro['fecha'] + ' | Reglas: ' + VERSION_REGLAS),
                 Paragraph('1. Identificación y solicitud', estilos['CabeceraELA'])]
    for clave in ('Paciente', 'Número de asociado', 'Auditor', 'Presentación solicitada'):
        contenido.append(par(clave + ': ' + str(registro['identificacion'][clave])))
    contenido.append(Paragraph('2. Información clínica registrada', estilos['CabeceraELA']))
    for k,v in registro['clinica'].items(): contenido.append(par(f'{k}: {v}'))
    contenido.append(Paragraph('3. ALSFRS-R actual', estilos['CabeceraELA']))
    for k,v in registro['als'].items(): contenido.append(par(f'{k}: {v}'))
    contenido.append(Paragraph('4. Concordancia parcial con criterios seleccionados del MCI186-19', estilos['CabeceraELA']))
    tabla = [[par('Criterio'),par('Estado')]] + [[par(k), par('Cumple' if v is True else 'No cumple' if v is False else 'Sin dato')] for k,v in registro['criterios'].items()]
    t=Table(tabla, colWidths=[365,135], repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf3')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#cbd5e1')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    contenido.append(t)
    contenido.append(Spacer(1,7))
    contenido.append(par('Interpretación: ' + registro['conclusion']))
    contenido.append(Paragraph('5. Progresión funcional observada (no excluyente)', estilos['CabeceraELA']))
    contenido.append(par(registro['progresion']))
    contenido.append(par('La velocidad media retrospectiva no permite predecir la evolución futura ni determina por sí sola la indicación de edaravona. Tres meses no equivalen exactamente a doce semanas.'))
    contenido.append(Paragraph('6. Seguridad y documentación', estilos['CabeceraELA']))
    for k,v in registro['seguridad'].items(): contenido.append(par(f'{k}: {v}'))
    contenido.append(Paragraph('7. Observaciones e interconsulta', estilos['CabeceraELA']))
    contenido.append(par('Observaciones de auditoría: ' + (registro['observaciones'] or 'No consignadas')))
    contenido.append(par('Preguntas al especialista: pertinencia de edaravona en este caso; beneficio funcional esperable e incertidumbre; riesgos, precauciones y plan de seguimiento.'))
    contenido.append(par('Dictamen del especialista: __________________________________________________________'))
    contenido.append(par('________________________________________________________________________________'))
    contenido.append(par('Especialista / matrícula / fecha / firma: ______________________________________________'))
    contenido.append(Paragraph('8. Fuentes y limitaciones', estilos['CabeceraELA']))
    contenido.append(par('MCI186-19: https://pubmed.ncbi.nlm.nih.gov/28522181/'))
    contenido.append(par('Prospecto de referencia para la presentación: ' + (registro['fuente'] or 'No incorporado: verificar ANMAT y documento vigente.')))
    contenido.append(par('Los criterios de selección de un ensayo no son contraindicaciones farmacológicas. La clasificación es parcial, no equivale a elegibilidad completa ni a autorización/denegatoria. Las alertas de seguridad deben contrastarse con el prospecto vigente.'))
    doc.build(contenido)
    return salida.getvalue()


st.set_page_config(page_title='Auditoría ELA | Edaravona', layout='centered')

ESTUDIO_URL = 'https://pubmed.ncbi.nlm.nih.gov/28522181/'
CLASIFICACION_URL = 'https://www.ncbi.nlm.nih.gov/books/NBK542356/'
PRODUCTOS = {
    'Elavone® — intravenosa': {'renal': 'cualquiera', 'fuente': 'https://elea.com/uploads/PROSPECTOS/ELAVONE-Propecto.pdf'},
    'Edaracut® — intravenosa': {'renal': 'cualquiera', 'fuente': 'https://boletin.anmat.gob.ar/junio_2024/Dispo_5555-24.pdf'},
    'Edaranovag® — intravenosa': {'renal': 'cualquiera', 'fuente': None},
    'Antixan® — intravenosa': {'renal': 'severa', 'fuente': 'https://bioprofarma-bago.com.ar/wp-content/uploads/2025/12/Prospecto-Antixan-21-07-21-1.pdf'},
    'Antixan Oral® — suspensión oral': {'renal': 'precaucion', 'fuente': None},
}
OPCIONES = ['Sin dato', 'Sí', 'No']

def si_no(valor):
    return None if valor == 'Sin dato' else valor == 'Sí'

def mostrar_criterio(nombre, resultado):
    if resultado is None:
        st.write(f'⚪ **{nombre}:** Sin dato')
    elif resultado:
        st.write(f'✅ **{nombre}:** Cumple')
    else:
        st.write(f'❌ **{nombre}:** No cumple')

st.title('Auditoría médica | Edaravona en ELA')
st.caption('Prototipo de apoyo a auditoría. Utilizar exclusivamente datos ficticios; no ingresar información identificatoria ni cargar estudios reales.')
st.info('La herramienta compara criterios clínicos seleccionados del ensayo MCI186-19 (con velocidad media observada descriptiva y no excluyente) y presenta alertas según la formulación. No indica, autoriza ni deniega tratamientos.')
producto = st.selectbox('Presentación solicitada', list(PRODUCTOS))
config = PRODUCTOS[producto]
with st.expander('Fuentes y alcance'):
    st.markdown(f'- [Ensayo MCI186-19]({ESTUDIO_URL})\n- [Referencia sobre ELA]({CLASIFICACION_URL})')
    if config['fuente']:
        st.markdown(f"- [Documento del producto seleccionado]({config['fuente']})")
    else:
        st.write('Prospecto aportado para revisión documental; verificar versión vigente en ANMAT antes de uso asistencial.')
    st.caption('Los criterios del ensayo no son contraindicaciones. Las reglas farmacológicas deben validarse contra los prospectos vigentes antes del uso institucional.')

st.header('1. Diagnóstico y evolución')
diagnostico = st.selectbox('ELA definida o probable según criterios revisados de El Escorial', OPCIONES)
edad = st.number_input('Edad (años)', min_value=0, max_value=120, value=None, step=1)
meses = st.number_input('Meses desde el primer síntoma de ELA', min_value=0, max_value=600, value=None, step=1)
cvf = st.number_input('Capacidad vital forzada (% del valor predicho)', min_value=0.0, max_value=200.0, value=None, step=1.0)

st.header('2. Clasificación japonesa de gravedad')
grados = {
    'Sin dato': None,
    'Grado 1 — Puede trabajar o realizar tareas domésticas': 1,
    'Grado 2 — Vive de forma independiente, pero no puede trabajar': 2,
    'Grado 3 — Requiere ayuda para alimentarse, usar el baño o desplazarse': 3,
    'Grado 4 — Presenta insuficiencia respiratoria, dificultad para eliminar secreciones o disfagia': 4,
    'Grado 5 — Utiliza traqueostomía, alimentación por sonda o ventilación por traqueostomía': 5,
}
grado = grados[st.selectbox('Grado de gravedad de la ELA', list(grados))]
st.caption('Clasificación funcional ordinal; no se calcula sumando puntos.')

st.header('3. ALSFRS-R')
st.caption('Asignar 0 a 4 según descriptores validados. Para el ítem 5, utilizar la variante apropiada según la vía de alimentación.')
items = ['Habla', 'Salivación', 'Deglución', 'Escritura', 'Cortar alimentos y manejar utensilios', 'Vestirse e higiene', 'Girarse en la cama y acomodar las sábanas', 'Caminar', 'Subir escaleras', 'Disnea', 'Ortopnea', 'Insuficiencia respiratoria']
puntajes = [st.selectbox(f'{i}. {nombre}', ['Sin dato', 0, 1, 2, 3, 4], key=f'als_{i}') for i, nombre in enumerate(items, 1)]
completa = all(isinstance(p, int) for p in puntajes)
if completa:
    st.metric('ALSFRS-R total', f'{sum(puntajes)}/48')
    st.write('**Puntaje mínimo por ítem:**', min(puntajes))
    respiratorio_concordante = all(p == 4 for p in puntajes[9:12])
    st.info('Tres ítems respiratorios con 4 puntos.' if respiratorio_concordante else 'Al menos un ítem respiratorio tiene menos de 4 puntos.')
else:
    respiratorio_concordante = None
    st.info('Completar los 12 ítems para calcular la puntuación total.')

st.subheader('3.1. Progresión funcional observada (opcional)')
st.caption('Registrar únicamente el descenso de ALSFRS-R y los meses del intervalo. No se utiliza como criterio de exclusión ni como pronóstico.')
col_p, col_m = st.columns(2)
with col_p:
    descenso_puntos = st.number_input('Puntos perdidos en ALSFRS-R', min_value=0, max_value=48, value=None, step=1)
with col_m:
    intervalo_meses = st.number_input('Meses entre evaluaciones', min_value=0.1, max_value=120.0, value=None, step=0.5, format='%.1f')
if descenso_puntos is not None and intervalo_meses is not None:
    velocidad_media = descenso_puntos / intervalo_meses
    progresion_texto = f'Descenso de {descenso_puntos} puntos en {intervalo_meses:g} meses; velocidad media observada: {velocidad_media:.2f} puntos ALSFRS-R/mes.'
    if 2.8 <= intervalo_meses <= 3.2:
        progresion_texto += ' Intervalo aproximadamente trimestral, sin acreditar el período exacto de 12 semanas del MCI186-19.'
    else:
        progresion_texto += ' Intervalo distinto de la preobservación de 12 semanas del MCI186-19.'
    st.info(progresion_texto + ' Es una descripción retrospectiva, no una proyección futura.')
elif descenso_puntos is None and intervalo_meses is None:
    progresion_texto = 'No evaluada: no se aportaron datos de progresión.'
else:
    progresion_texto = 'Información incompleta: se requieren descenso e intervalo para calcular la velocidad.'
    st.warning(progresion_texto)

st.header('4. Evaluación clínica de seguridad')
st.caption('El antecedente conocido de hipersensibilidad a edaravona o excipientes es una contraindicación. No se pregunta de rutina; si consta en la documentación, debe señalarse al auditor.')
renal = st.selectbox('Situación renal documentada', ['Sin dato', 'Sin insuficiencia renal documentada', 'Insuficiencia renal leve o moderada', 'Insuficiencia renal severa'])
st.subheader('Precauciones')
preguntas_precaucion = [
    'Disfunción renal o deshidratación', 'Disfunción hepática',
    'Trastorno cardíaco clínicamente relevante', 'Asma o sensibilidad a sulfitos',
    'Infección activa clínicamente relevante', 'Alteración aguda de la conciencia',
    'Embarazo o sospecha de embarazo', 'Lactancia',
    'Edad avanzada con fragilidad clínica',
    'Tratamiento antibiótico concomitante que requiere evaluación',
]
precauciones = {pregunta: st.selectbox(pregunta, OPCIONES, key=f'prec_{i}') for i, pregunta in enumerate(preguntas_precaucion, 1)}
st.subheader('Documentación de seguridad')
laboratorio = st.selectbox('Evaluación clínica y laboratorios basales adjuntos y suficientes', OPCIONES)
seguimiento = st.selectbox('Plan de monitoreo clínico y de laboratorio documentado', OPCIONES)
st.caption('No se exige ingresar valores de laboratorio en este prototipo; deben revisarse en la documentación por el auditor.')

st.header('5. Documentación clínica')
st.caption('Para el prototipo utilizar exclusivamente identificadores y nombres ficticios.')
paciente_ficticio = st.text_input('Nombre y apellido ficticios (para el PDF)')
asociado_ficticio = st.text_input('Número de asociado ficticio (para el PDF)')
auditor_ficticio = st.text_input('Identificación ficticia del auditor (para el PDF)')
documentacion = st.selectbox('Informe neurológico y documentación clínica completos', OPCIONES)
observaciones = st.text_area('Observaciones del auditor (sin datos identificatorios)')

st.header('6. Evaluación orientativa')
if st.button('Evaluar', type='primary', use_container_width=True):
    criterios = {
        'ELA definida o probable': si_no(diagnostico),
        'Edad entre 20 y 75 años': None if edad is None else 20 <= edad <= 75,
        'Evolución ≤24 meses': None if meses is None else meses <= 24,
        'CVF ≥80 % del predicho': None if cvf is None else cvf >= 80,
        'ALSFRS-R ≥2 en todos los ítems': None if not completa else min(puntajes) >= 2,
        'ALSFRS-R respiratorio: 4 puntos en los tres ítems': respiratorio_concordante,
        'Clasificación japonesa grado 1–2': None if grado is None else grado in (1, 2),
    }
    st.subheader('6.1. Concordancia parcial con criterios seleccionados de MCI186-19')
    for nombre, resultado in criterios.items():
        mostrar_criterio(nombre, resultado)
    fallidos = [nombre for nombre, valor in criterios.items() if valor is False]
    faltantes = [nombre for nombre, valor in criterios.items() if valor is None]
    if fallidos:
        st.warning('No concordante con todos los criterios clínicos seleccionados del ensayo; requiere valoración individual.')
    elif faltantes:
        st.warning('Concordancia indeterminada por información incompleta.')
    else:
        st.success('Concordante con los criterios clínicos seleccionados que evalúa esta herramienta.')
    if faltantes:
        st.write('**Criterios pendientes:**', ', '.join(faltantes))
    st.caption('La velocidad de progresión se informa separadamente, sin intervenir en la clasificación. La concordancia es parcial y no acredita todos los criterios del ensayo.')

    st.subheader('6.2. Progresión funcional observada')
    st.write(progresion_texto)
    st.subheader('6.3. Seguridad por presentación')
    contra = []
    prec_extra = []
    pendiente_renal = renal == 'Sin dato'
    renal_afectado = renal in ('Insuficiencia renal leve o moderada', 'Insuficiencia renal severa')
    if renal_afectado:
        if config['renal'] == 'cualquiera':
            contra.append('Insuficiencia renal documentada: contraindicación renal indicada en el prospecto de referencia.')
        elif config['renal'] == 'severa':
            if renal == 'Insuficiencia renal severa':
                contra.append('Insuficiencia renal severa: contraindicación según prospecto de referencia.')
            else:
                prec_extra.append('Insuficiencia renal leve/moderada: requiere evaluación individual; no clasificada aquí como contraindicación.')
        else:
            prec_extra.append('Deterioro renal: precaución y revisión de documentación; no figura como contraindicación renal en el prospecto oral aportado.')
    presentes = [nombre for nombre, valor in precauciones.items() if valor == 'Sí'] + prec_extra
    pendientes = [nombre for nombre, valor in precauciones.items() if valor == 'Sin dato']
    if contra:
        st.error('Alerta de contraindicación farmacológica documentada para la presentación seleccionada.')
        for item in contra:
            st.write('- ' + item)
    if presentes:
        st.warning('Precauciones que requieren evaluación clínica:')
        for item in presentes:
            st.write('- ' + item)
    if pendiente_renal or pendientes:
        st.warning('Evaluación de seguridad parcialmente indeterminada por datos faltantes.')
        if pendiente_renal:
            st.write('- Situación renal sin dato')
        for item in pendientes:
            st.write('- ' + item)
    if not contra and not presentes and not pendiente_renal and not pendientes:
        st.success('Sin alertas identificadas en los campos de seguridad relevados; no descarta riesgos no consignados.')

    st.subheader('6.4. Estado documental')
    doc_pendientes = []
    if laboratorio != 'Sí':
        doc_pendientes.append('Laboratorios y evaluación basal')
    if seguimiento != 'Sí':
        doc_pendientes.append('Plan de seguimiento')
    if documentacion != 'Sí':
        doc_pendientes.append('Informe neurológico y documentación clínica')
    if doc_pendientes:
        st.warning('Documentación incompleta o no confirmada: ' + '; '.join(doc_pendientes))
    else:
        st.success('Documentación declarada completa; su suficiencia debe comprobarse manualmente.')

    st.subheader('6.5. Dictamen')
    st.info('Pendiente de evaluación del auditor médico e interconsulta con neurología especializada en ELA. La herramienta no autoriza ni deniega cobertura.')
    if observaciones.strip():
        st.write('**Observaciones del auditor:**', observaciones)
    st.caption('Prototipo de validación con datos ficticios. Revisar versiones vigentes de prospectos y reglas antes de cualquier implementación institucional.')

    # El informe se construye con los mismos valores y resultados de esta evaluación.
    conclusion = ('No concordante con todos los criterios seleccionados; valoración individual requerida.' if fallidos else
                  'Concordancia indeterminada por información incompleta.' if faltantes else
                  'Concordante con los criterios seleccionados; no implica elegibilidad completa.')
    registro = {
        'id': 'ELA-' + uuid4().hex[:12].upper(),
        'fecha': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
        'identificacion': {'Paciente': paciente_ficticio or 'No consignado', 'Número de asociado': asociado_ficticio or 'No consignado', 'Auditor': auditor_ficticio or 'No consignado', 'Presentación solicitada': producto},
        'clinica': {'Diagnóstico': diagnostico, 'Edad': edad if edad is not None else 'Sin dato', 'Meses desde primer síntoma': meses if meses is not None else 'Sin dato', 'CVF (% predicho)': cvf if cvf is not None else 'Sin dato', 'Grado japonés': grado if grado is not None else 'Sin dato'},
        'als': {**{f'{i}. {nombre}': puntajes[i-1] for i,nombre in enumerate(items,1)}, 'Total': f'{sum(puntajes)}/48' if completa else 'No calculable'},
        'criterios': criterios, 'conclusion': conclusion, 'progresion': progresion_texto,
        'seguridad': {'Situación renal': renal, 'Alertas de contraindicación': '; '.join(contra) or 'Ninguna identificada en las reglas evaluadas', 'Precauciones presentes': '; '.join(presentes) or 'Ninguna declarada', 'Precauciones sin dato': '; '.join(pendientes) or 'Ninguna', 'Situación renal pendiente': 'Sí' if pendiente_renal else 'No', 'Laboratorios basales': laboratorio, 'Plan de monitoreo': seguimiento, 'Documentación clínica': documentacion, **precauciones},
        'observaciones': observaciones, 'fuente': config['fuente']
    }
    st.session_state['informe_ela'] = crear_pdf(registro)
    st.session_state['informe_ela_id'] = registro['id']

if 'informe_ela' in st.session_state:
    st.subheader('7. Informe descargable para interconsulta')
    st.warning('Si modificás cualquier dato, presioná «Evaluar» nuevamente antes de descargar. El informe refleja la última evaluación ejecutada.')
    st.download_button('Descargar informe PDF', data=st.session_state['informe_ela'], file_name=st.session_state['informe_ela_id'] + '.pdf', mime='application/pdf', use_container_width=True)
    st.caption('El PDF contiene campos para dictamen manuscrito del especialista. No guarda historial ni valida identidad o firma. Usar solo datos ficticios hasta implementar seguridad institucional.')
