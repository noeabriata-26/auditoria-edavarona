import streamlit as st

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
st.info('La herramienta compara criterios del ensayo MCI186-19 y presenta alertas según la formulación seleccionada. No indica, autoriza ni deniega tratamientos.')
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
progresion = st.number_input('Descenso de ALSFRS-R durante las 12 semanas previas (puntos)', min_value=0, max_value=48, value=None, step=1)
st.caption('La progresión requiere dos evaluaciones funcionales comparables.')

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
        'Descenso ALSFRS-R de 1–4 puntos en 12 semanas': None if progresion is None else 1 <= progresion <= 4,
        'Clasificación japonesa grado 1–2': None if grado is None else grado in (1, 2),
    }
    st.subheader('6.1. Concordancia con MCI186-19')
    for nombre, resultado in criterios.items():
        mostrar_criterio(nombre, resultado)
    fallidos = [nombre for nombre, valor in criterios.items() if valor is False]
    faltantes = [nombre for nombre, valor in criterios.items() if valor is None]
    if fallidos:
        st.warning('No concordante con todos los criterios seleccionados del ensayo; requiere valoración individual.')
    elif faltantes:
        st.warning('Concordancia indeterminada por información incompleta.')
    else:
        st.success('Concordante con los criterios clínicos seleccionados del ensayo.')
    if faltantes:
        st.write('**Criterios pendientes:**', ', '.join(faltantes))

    st.subheader('6.2. Seguridad por presentación')
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

    st.subheader('6.3. Estado documental')
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

    st.subheader('6.4. Dictamen')
    st.info('Pendiente de evaluación del auditor médico e interconsulta con neurología especializada en ELA. La herramienta no autoriza ni deniega cobertura.')
    if observaciones.strip():
        st.write('**Observaciones del auditor:**', observaciones)
    st.caption('Prototipo de validación con datos ficticios. Revisar versiones vigentes de prospectos y reglas antes de cualquier implementación institucional.')
