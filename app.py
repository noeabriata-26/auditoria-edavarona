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
