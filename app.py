
import streamlit as st

st.set_page_config(
    page_title="Auditoría ELA | Elavone",
    layout="centered"
)

st.title("Auditoría médica | Elavone® en ELA")
st.caption(
    "Edaravona intravenosa 30 mg/20 ml. "
    "Prototipo para pruebas con datos ficticios. "
    "No autoriza ni rechaza tratamientos."
)

PROSPECTO = (
    "https://elea.com/uploads/PROSPECTOS/"
    "ELAVONE-Propecto.pdf"
)
ESTUDIO = "https://pubmed.ncbi.nlm.nih.gov/28522181/"
METODOLOGIA = (
    "https://journals.plos.org/plosone/"
    "article?id=10.1371/journal.pone.0258614"
)
CADTH = (
    "https://www.ncbi.nlm.nih.gov/books/"
    "NBK542364/table/cl4.tab1/"
)

OPCIONES = ["Sin dato", "Sí", "No"]


def pregunta(texto, clave):
    return st.selectbox(texto, OPCIONES, key=clave)


def afirmativo(valor):
    if valor == "Sin dato":
        return None
    return valor == "Sí"


def negativo(valor):
    if valor == "Sin dato":
        return None
    return valor == "No"


def mostrar(nombre, valor):
    if valor is None:
        st.write(f"⚪ **{nombre}:** Sin dato")
    elif valor:
        st.write(f"✅ **{nombre}:** Cumple")
    else:
        st.write(f"❌ **{nombre}:** No cumple")


def mostrar_lista(titulo, elementos):
    if elementos:
        st.write(f"**{titulo}**")
        for elemento in elementos:
            st.write(f"- {elemento}")


with st.expander("Fuentes documentales y alcance"):
    st.markdown(
        f"- [Prospecto argentino de Elavone]({PROSPECTO})\n"
        f"- [Ensayo pivotal MCI186-19]({ESTUDIO})\n"
        f"- [Descripción de los criterios del ensayo]"
        f"({METODOLOGIA})\n"
        f"- [Comparación de estudios CADTH]({CADTH})"
    )
    st.info(
        "Los criterios del ensayo se utilizan para "
        "describir la población estudiada, no como "
        "contraindicaciones absolutas. Las reglas "
        "de seguridad se basan en el prospecto "
        "de Elavone de referencia."
    )

# ==========================================
# 1. DIAGNÓSTICO Y EVOLUCIÓN
# ==========================================

st.header("1. Diagnóstico y evolución")

diagnostico = pregunta(
    "ELA definida o probable según criterios "
    "revisados de El Escorial",
    "diagnostico"
)

edad = st.number_input(
    "Edad (años)",
    min_value=0,
    max_value=120,
    value=None,
    step=1
)

meses = st.number_input(
    "Meses desde el primer síntoma de ELA",
    min_value=0,
    max_value=600,
    value=None,
    step=1
)

cvf = st.number_input(
    "Capacidad vital forzada (% del predicho)",
    min_value=0.0,
    max_value=200.0,
    value=None,
    step=1.0
)

progresion = st.number_input(
    "Descenso de ALSFRS-R durante las "
    "12 semanas de preobservación (puntos)",
    min_value=0,
    max_value=48,
    value=None,
    step=1
)

# ==========================================
# 2. CLASIFICACIÓN JAPONESA
# ==========================================

st.header("2. Clasificación japonesa de gravedad")

grados = {
    "Sin dato": None,
    "Grado 1 - Puede trabajar o realizar "
    "tareas domésticas": 1,
    "Grado 2 - Independiente, con dificultades "
    "para trabajar o realizar tareas domésticas": 2,
    "Grado 3 - Requiere asistencia para alimentarse, "
    "desplazarse o utilizar el baño": 3,
    "Grado 4 - Insuficiencia respiratoria, dificultad "
    "para eliminar secreciones o disfagia": 4,
    "Grado 5 - Traqueostomía, alimentación por sonda "
    "o ventilación mediante traqueostomía": 5
}

seleccion = st.selectbox(
    "Seleccionar el grado clínico",
    list(grados.keys())
)
grado = grados[seleccion]

st.caption(
    "La clasificación debe ser asignada mediante "
    "evaluación clínica. No se obtiene sumando "
    "los puntos de ALSFRS-R."
)

# ==========================================
# 3. ALSFRS-R
# ==========================================

st.header("3. Escala ALSFRS-R")

st.caption(
    "Puntuar cada ítem de 0 a 4 utilizando "
    "los descriptores validados de la escala. "
    "En el ítem 5, aplicar la variante pertinente."
)

items = [
    "Habla",
    "Salivación",
    "Deglución",
    "Escritura",
    "Cortar alimentos y manejar utensilios",
    "Vestirse e higiene",
    "Girarse en la cama y acomodar las sábanas",
    "Caminar",
    "Subir escaleras",
    "Disnea",
    "Ortopnea",
    "Insuficiencia respiratoria"
]

puntajes = []

for i, item in enumerate(items, 1):
    valor = st.selectbox(
        f"{i}. {item}",
        ["Sin dato", 0, 1, 2, 3, 4],
        key=f"als_{i}"
    )
    puntajes.append(valor)

completa = all(
    isinstance(p, int) for p in puntajes
)

if completa:
    st.metric(
        "ALSFRS-R total",
        f"{sum(puntajes)}/48"
    )
    st.write(
        "Puntaje mínimo por ítem:",
        min(puntajes)
    )
    respiratorio = all(
        p == 4 for p in puntajes[9:12]
    )
else:
    respiratorio = None
    st.info(
        "Completá los 12 ítems para calcular "
        "la escala y evaluar los criterios."
    )

# ==========================================
# 4. EXCLUSIONES DEL ENSAYO MCI186-19
# ==========================================

st.header("4. Antecedentes relevantes del ensayo")

st.caption(
    "Estas preguntas identifican situaciones "
    "excluidas del ensayo pivotal. No constituyen "
    "por sí mismas contraindicaciones de Elavone."
)

cirugia = pregunta(
    "¿Cirugía de columna después del inicio "
    "de los síntomas de ELA?",
    "cirugia"
)

cirugia_prevista = pregunta(
    "¿Cirugía de columna prevista durante "
    "el período de evaluación?",
    "cirugia_prevista"
)

diagnostico_alternativo = pregunta(
    "¿Existe otra enfermedad que podría explicar "
    "los síntomas neurológicos actuales?",
    "diagnostico_alternativo"
)

cancer = pregunta(
    "¿Tratamiento activo por enfermedad maligna?",
    "cancer"
)

edaravona_previa = pregunta(
    "¿Recibió edaravona anteriormente?",
    "edaravona_previa"
)

complicacion = pregunta(
    "¿Presenta una complicación clínicamente "
    "significativa que compromete la evaluación?",
    "complicacion"
)

experimental = pregunta(
    "¿Recibió un producto en investigación "
    "durante las últimas 12 semanas?",
    "experimental"
)

st.subheader("4.1. Función renal según el ensayo")

clearance = st.number_input(
    "Depuración de creatinina documentada "
    "(ml/min)",
    min_value=0.0,
    max_value=250.0,
    value=None,
    step=1.0
)

st.caption(
    "El ensayo MCI186-19 excluyó a pacientes "
    "con depuración de creatinina ≤50 ml/min. "
    "Este umbral NO define la contraindicación "
    "renal del prospecto de Elavone."
)

# ==========================================
# 5. SEGURIDAD SEGÚN PROSPECTO ELAVONE
# ==========================================

st.header("5. Seguridad según prospecto de Elavone")

st.subheader("5.1. Contraindicaciones")

hipersensibilidad = pregunta(
    "¿Hipersensibilidad conocida a edaravona "
    "o a alguno de sus excipientes?",
    "hipersensibilidad"
)

insuficiencia_renal = pregunta(
    "¿Presenta insuficiencia renal "
    "clínicamente documentada?",
    "insuficiencia_renal"
)

st.warning(
    "El apartado de contraindicaciones del "
    "prospecto consultado indica insuficiencia "
    "renal sin establecer allí un umbral numérico. "
    "No se debe utilizar automáticamente "
    "la depuración de 50 ml/min del ensayo "
    "para interpretar esta contraindicación."
)

st.subheader("5.2. Documentación renal")

evaluacion_renal = pregunta(
    "¿Se dispone de una evaluación renal "
    "actual suficiente para descartar "
    "insuficiencia renal?",
    "evaluacion_renal"
)

st.caption(
    "En ELA, la pérdida de masa muscular puede "
    "dificultar la interpretación de creatinina "
    "sérica. Considerar la documentación de "
    "cistatina C y otras mediciones cuando "
    "corresponda, según el prospecto."
)

st.subheader("5.3. Precauciones")

preguntas_precaucion = [
    "Deshidratación o relación BUN/creatinina elevada",
    "Disfunción hepática",
    "Enfermedad cardíaca clínicamente relevante",
    "Asma o sensibilidad a sulfitos",
    "Infección activa clínicamente relevante",
    "Alteración aguda de la conciencia",
    "Embarazo o sospecha de embarazo",
    "Lactancia",
    "Edad avanzada con fragilidad clínica",
    "Uso concomitante de antibióticos "
    "que requiere vigilancia renal"
]

precauciones = {}

for i, texto in enumerate(preguntas_precaucion):
    precauciones[texto] = pregunta(
        texto, f"precaucion_{i}"
    )

st.subheader("5.4. Seguimiento")

laboratorio = pregunta(
    "¿Se dispone de evaluación clínica y "
    "laboratorio basal suficientes?",
    "laboratorio"
)

seguimiento = pregunta(
    "¿Existe un plan de monitoreo clínico "
    "y de laboratorio?",
    "seguimiento"
)

# ==========================================
# 6. DOCUMENTACIÓN GENERAL
# ==========================================

st.header("6. Documentación")

documentacion = pregunta(
    "¿Informe neurológico y documentación "
    "clínica completos?",
    "documentacion"
)

observaciones = st.text_area(
    "Observaciones del médico auditor"
)

# ==========================================
# 7. EVALUACIÓN
# ==========================================

st.header("7. Resultado orientativo")

if st.button(
    "Evaluar",
    type="primary",
    use_container_width=True
):

    # CRITERIOS DE INCLUSIÓN DEL ENSAYO

    inclusion = {
        "ELA definida o probable":
            afirmativo(diagnostico),

        "Edad entre 20 y 75 años":
            None if edad is None
            else 20 <= edad <= 75,

        "Evolución ≤24 meses":
            None if meses is None
            else meses <= 24,

        "CVF ≥80%":
            None if cvf is None
            else cvf >= 80,

        "ALSFRS-R ≥2 en todos los ítems":
            None if not completa
            else min(puntajes) >= 2,

        "Tres ítems respiratorios con 4 puntos":
            respiratorio,

        "Descenso ALSFRS-R de 1 a 4 puntos "
        "en 12 semanas":
            None if progresion is None
            else 1 <= progresion <= 4,

        "Gravedad japonesa grado 1 o 2":
            None if grado is None
            else grado in (1, 2)
    }

    st.subheader("7.1. Inclusión en MCI186-19")

    for nombre, valor in inclusion.items():
        mostrar(nombre, valor)

    # EXCLUSIONES DEL ENSAYO

    exclusion = {
        "Cirugía de columna posterior al inicio "
        "de ELA": cirugia,

        "Cirugía de columna prevista":
            cirugia_prevista,

        "Diagnóstico neurológico alternativo "
        "sin resolver": diagnostico_alternativo,

        "Tratamiento activo por malignidad":
            cancer,

        "Tratamiento previo con edaravona":
            edaravona_previa,

        "Complicación clínicamente significativa":
            complicacion,

        "Producto en investigación reciente":
            experimental
    }

    exclusiones_presentes = [
        nombre for nombre, valor
        in exclusion.items()
        if valor == "Sí"
    ]

    exclusiones_pendientes = [
        nombre for nombre, valor
        in exclusion.items()
        if valor == "Sin dato"
    ]

    if clearance is None:
        exclusiones_pendientes.append(
            "Depuración de creatinina"
        )
    elif clearance <= 50:
        exclusiones_presentes.append(
            "Depuración de creatinina ≤50 ml/min"
        )

    st.subheader("7.2. Exclusiones del ensayo")

    if exclusiones_presentes:
        st.warning(
            "Se identificaron antecedentes que "
            "no concuerdan con la selección "
            "del ensayo MCI186-19."
        )
        mostrar_lista(
            "Exclusiones identificadas:",
            exclusiones_presentes
        )

    elif exclusiones_pendientes:
        st.warning(
            "No se completó la evaluación "
            "de exclusiones del ensayo."
        )

    else:
        st.success(
            "No se identificaron las exclusiones "
            "del ensayo relevadas en este formulario."
        )

    mostrar_lista(
        "Exclusiones sin dato:",
        exclusiones_pendientes
    )

    # CONTRAINDICACIONES DEL PROSPECTO

    contra = {
        "Hipersensibilidad a edaravona "
        "o excipientes": hipersensibilidad,

        "Insuficiencia renal documentada":
            insuficiencia_renal
    }

    contra_presentes = [
        nombre for nombre, valor
        in contra.items()
        if valor == "Sí"
    ]

    contra_pendientes = [
        nombre for nombre, valor
        in contra.items()
        if valor == "Sin dato"
    ]

    if evaluacion_renal != "Sí":
        contra_pendientes.append(
            "Evaluación renal suficiente"
        )

    prec_presentes = [
        nombre for nombre, valor
        in precauciones.items()
        if valor == "Sí"
    ]

    prec_pendientes = [
        nombre for nombre, valor
        in precauciones.items()
        if valor == "Sin dato"
    ]

    st.subheader("7.3. Seguridad de Elavone")

    if contra_presentes:
        st.error(
            "Se identificó al menos una "
            "contraindicación del prospecto."
        )
        mostrar_lista(
            "Contraindicaciones:",
            contra_presentes
        )

    elif contra_pendientes:
        st.warning(
            "No es posible completar la evaluación "
            "de contraindicaciones."
        )

    elif prec_presentes:
        st.warning(
            "Existen precauciones que requieren "
            "evaluación individual."
        )

    elif prec_pendientes:
        st.warning(
            "Hay precauciones pendientes "
            "de documentación."
        )

    elif laboratorio != "Sí" or seguimiento != "Sí":
        st.warning(
            "Falta evaluación basal o "
            "plan de seguimiento."
        )

    else:
        st.success(
            "No se identificaron alertas "
            "de seguridad en los campos relevados."
        )

    mostrar_lista(
        "Contraindicaciones sin dato:",
        contra_pendientes
    )

    mostrar_lista(
        "Precauciones identificadas:",
        prec_presentes
    )

    mostrar_lista(
        "Precauciones sin dato:",
        prec_pendientes
    )

    # CONCLUSIÓN

    st.subheader("7.4. Conclusión")

    inclusion_incompleta = any(
        valor is None
        for valor in inclusion.values()
    )

    inclusion_concordante = all(
        valor is True
        for valor in inclusion.values()
    )

    ensayo_incompleto = (
        inclusion_incompleta
        or bool(exclusiones_pendientes)
    )

    ensayo_concordante = (
        inclusion_concordante
        and not exclusiones_presentes
        and not ensayo_incompleto
    )

    seguridad_incompleta = (
        bool(contra_pendientes)
        or bool(prec_pendientes)
        or laboratorio != "Sí"
        or seguimiento != "Sí"
    )

    if contra_presentes:
        st.error(
            "Contraindicación identificada "
            "según prospecto de Elavone. "
            "Requiere revisión médica."
        )

    elif (
        ensayo_incompleto
        or seguridad_incompleta
        or documentacion != "Sí"
    ):
        st.warning(
            "Evaluación incompleta. "
            "Se requiere documentación adicional."
        )

    elif prec_presentes:
        st.warning(
            "Requiere evaluación individual "
            "del riesgo-beneficio."
        )

    elif ensayo_concordante:
        st.success(
            "Perfil concordante con los criterios "
            "relevados del ensayo MCI186-19, "
            "sin alertas de seguridad registradas."
        )

    else:
        st.warning(
            "El paciente no concuerda plenamente "
            "con la población seleccionada del "
            "ensayo pivotal. Esto no equivale "
            "a contraindicación ni determina "
            "automáticamente la cobertura."
        )

    if observaciones.strip():
        st.write(
            "**Observaciones del auditor:**"
        )
        st.write(observaciones)

    st.divider()
    st.caption(
        "Resultado orientativo. No sustituye "
        "el juicio clínico, la revisión del "
        "prospecto vigente ni las decisiones "
        "institucionales de cobertura."
    )

