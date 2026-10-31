import streamlit as st

st.set_page_config(
    page_title="Auditoría ELA | Elavone",
    layout="centered"
)

PROSPECTO_URL = (
    "https://elea.com/uploads/PROSPECTOS/"
    "ELAVONE-Propecto.pdf"
)

ESTUDIO_URL = (
    "https://pubmed.ncbi.nlm.nih.gov/28522181/"
)

CLASIFICACION_URL = (
    "https://www.ncbi.nlm.nih.gov/books/NBK542356/"
)

OPCIONES = ["Sin dato", "Sí", "No"]


def respuesta_positiva(valor):
    if valor == "Sin dato":
        return None
    return valor == "Sí"


def mostrar_criterio(nombre, resultado):
    if resultado is None:
        st.write(f"⚪ **{nombre}:** Sin dato")
    elif resultado:
        st.write(f"✅ **{nombre}:** Cumple")
    else:
        st.write(f"❌ **{nombre}:** No cumple")


st.title("Auditoría médica | Elavone® en ELA")

st.caption(
    "Edaravona 30 mg/20 ml, solución intravenosa. "
    "Prototipo de apoyo a la auditoría. "
    "Utilizar exclusivamente datos ficticios."
)

st.info(
    "La herramienta compara el perfil clínico con los "
    "criterios del ensayo MCI186-19 y registra alertas "
    "de seguridad. No autoriza ni rechaza tratamientos."
)

with st.expander("Fuentes documentales"):
    st.markdown(
        f"- [Prospecto de Elavone]({PROSPECTO_URL})\n"
        f"- [Ensayo pivotal MCI186-19]({ESTUDIO_URL})\n"
        f"- [Clasificación japonesa de gravedad]"
        f"({CLASIFICACION_URL})"
    )

# --------------------------------------------------
# 1. DIAGNÓSTICO Y EVOLUCIÓN
# --------------------------------------------------

st.header("1. Diagnóstico y evolución")

diagnostico = st.selectbox(
    "Diagnóstico de ELA definido o probable "
    "según criterios revisados de El Escorial",
    OPCIONES
)

edad = st.number_input(
    "Edad del paciente (años)",
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
    "Capacidad vital forzada (% del valor predicho)",
    min_value=0.0,
    max_value=200.0,
    value=None,
    step=1.0
)

progresion = st.number_input(
    "Descenso de ALSFRS-R durante las "
    "12 semanas previas (puntos)",
    min_value=0,
    max_value=48,
    value=None,
    step=1
)

st.caption(
    "La progresión debe documentarse mediante "
    "evaluaciones funcionales comparables."
)

# --------------------------------------------------
# 2. CLASIFICACIÓN JAPONESA
# --------------------------------------------------

st.header("2. Clasificación japonesa de gravedad")

st.write(
    "Seleccionar la categoría que mejor describa "
    "la situación clínica y funcional del paciente."
)

grados_japoneses = {
    "Sin dato": None,

    "Grado 1 — Puede trabajar o realizar "
    "tareas domésticas": 1,

    "Grado 2 — Vive de forma independiente, "
    "pero no puede trabajar": 2,

    "Grado 3 — Requiere ayuda para alimentarse, "
    "usar el baño o desplazarse": 3,

    "Grado 4 — Presenta insuficiencia respiratoria, "
    "dificultad para eliminar secreciones o disfagia": 4,

    "Grado 5 — Utiliza traqueostomía, alimentación "
    "por sonda o ventilación por traqueostomía": 5
}

seleccion_japonesa = st.selectbox(
    "Grado de gravedad de la ELA",
    list(grados_japoneses.keys())
)

gr_japones = grados_japoneses[seleccion_japonesa]

if gr_japones in (1, 2):
    st.success(
        "Gravedad concordante con la población "
        "seleccionada del ensayo pivotal."
    )
elif gr_japones is not None:
    st.warning(
        "Gravedad fuera del perfil seleccionado "
        "del ensayo MCI186-19. Esto no constituye "
        "por sí mismo una contraindicación."
    )

st.caption(
    "La clasificación japonesa es funcional y "
    "ordinal. No se calcula sumando puntos."
)

# --------------------------------------------------
# 3. ALSFRS-R
# --------------------------------------------------

st.header("3. Escala ALSFRS-R")

st.caption(
    "Asignar 0 a 4 puntos por ítem conforme a "
    "los descriptores validados de ALSFRS-R. "
    "En el ítem 5, utilizar la variante pertinente "
    "según la vía de alimentación."
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

for indice, nombre in enumerate(items, start=1):
    valor = st.selectbox(
        f"{indice}. {nombre}",
        ["Sin dato", 0, 1, 2, 3, 4],
        key=f"als_{indice}"
    )
    puntajes.append(valor)

completa = all(
    isinstance(p, int) for p in puntajes
)

if completa:
    total_alsfrs = sum(puntajes)

    st.metric(
        "ALSFRS-R total",
        f"{total_alsfrs}/48"
    )

    st.write(
        "**Puntaje mínimo por ítem:**",
        min(puntajes)
    )

    respiratorios = puntajes[9:12]

    respiratorio_concordante = all(
        p == 4 for p in respiratorios
    )

    if respiratorio_concordante:
        st.success(
            "Los tres ítems respiratorios tienen "
            "4 puntos: concordante con el ensayo."
        )
    else:
        st.warning(
            "Al menos un ítem respiratorio tiene "
            "menos de 4 puntos. No concuerda con "
            "el criterio respiratorio del ensayo."
        )

else:
    total_alsfrs = None
    respiratorio_concordante = None

    st.info(
        "Completá los 12 ítems para calcular "
        "el puntaje y evaluar el criterio respiratorio."
    )

# --------------------------------------------------
# 4. SEGURIDAD DE ELAVONE
# --------------------------------------------------

st.header("4. Evaluación de seguridad de Elavone")

st.caption(
    "Registrar contraindicaciones y condiciones "
    "que requieren precaución según el prospecto "
    "del producto. La evaluación definitiva "
    "corresponde al médico tratante y al auditor."
)

st.subheader("4.1. Contraindicaciones")

hipersensibilidad = st.selectbox(
    "Antecedente de hipersensibilidad a "
    "edaravona o componentes del producto",
    OPCIONES
)

renal_severa = st.selectbox(
    "Deterioro renal severo documentado",
    OPCIONES
)

st.subheader("4.2. Precauciones")

preguntas_precaucion = [
    "Disfunción renal o deshidratación",
    "Disfunción hepática",
    "Trastorno cardíaco clínicamente relevante",
    "Asma o sensibilidad a sulfitos",
    "Infección activa clínicamente relevante",
    "Alteración aguda de la conciencia",
    "Embarazo o sospecha de embarazo",
    "Lactancia",
    "Edad avanzada con fragilidad clínica",
    "Tratamiento antibiótico concomitante "
    "que requiere evaluación"
]

precauciones = {}

for indice, pregunta in enumerate(
    preguntas_precaucion, start=1
):
    precauciones[pregunta] = st.selectbox(
        pregunta,
        OPCIONES,
        key=f"precaucion_{indice}"
    )

st.subheader("4.3. Documentación de seguridad")

laboratorio = st.selectbox(
    "Evaluación clínica y laboratorio basal "
    "suficientes para valorar la seguridad",
    OPCIONES
)

seguimiento = st.selectbox(
    "Plan de monitoreo clínico y de "
    "laboratorio documentado",
    OPCIONES
)

st.caption(
    "La selección de Sí/No no sustituye "
    "la revisión del prospecto ni la "
    "interpretación clínica de los hallazgos."
)

# --------------------------------------------------
# 5. DOCUMENTACIÓN
# --------------------------------------------------

st.header("5. Documentación clínica")

documentacion = st.selectbox(
    "Informe neurológico y documentación "
    "clínica completos",
    OPCIONES
)

observaciones = st.text_area(
    "Observaciones del médico auditor",
    placeholder=(
        "Registrar fundamentos, documentación "
        "pendiente o aspectos que requieren "
        "valoración individual."
    )
)

# --------------------------------------------------
# 6. RESULTADOS
# --------------------------------------------------

st.header("6. Resultado orientativo")

if st.button(
    "Evaluar elegibilidad",
    type="primary",
    use_container_width=True
):

    criterios = {
        "ELA definida o probable":
            respuesta_positiva(diagnostico),

        "Edad entre 20 y 75 años":
            None if edad is None
            else 20 <= edad <= 75,

        "Evolución ≤24 meses":
            None if meses is None
            else meses <= 24,

        "CVF ≥80% del valor predicho":
            None if cvf is None
            else cvf >= 80,

        "ALSFRS-R ≥2 en todos los ítems":
            None if not completa
            else min(puntajes) >= 2,

        "ALSFRS-R respiratorio: "
        "4 puntos en cada uno de los tres ítems":
            respiratorio_concordante,

        "Descenso ALSFRS-R de 1–4 puntos "
        "en 12 semanas":
            None if progresion is None
            else 1 <= progresion <= 4,

        "Clasificación japonesa grado 1–2":
            None if gr_japones is None
            else gr_japones in (1, 2)
    }

    st.subheader("6.1. Perfil del ensayo MCI186-19")

    for nombre, resultado in criterios.items():
        mostrar_criterio(nombre, resultado)

    perfil_incompleto = any(
        valor is None
        for valor in criterios.values()
    )

    perfil_concordante = all(
        valor is True
        for valor in criterios.values()
    )

    if perfil_incompleto:
        st.warning(
            "No se puede determinar la concordancia "
            "con el ensayo por falta de datos."
        )
    elif perfil_concordante:
        st.success(
            "Perfil concordante con los criterios "
            "clínicos seleccionados del ensayo."
        )
    else:
        st.warning(
            "Perfil no completamente concordante "
            "con la población del ensayo pivotal. "
            "Requiere valoración individual."
        )

    # Evaluación de seguridad

    contraindicaciones = {
        "Hipersensibilidad a edaravona "
        "o componentes": hipersensibilidad,
        "Deterioro renal severo": renal_severa
    }

    contra_presentes = [
        nombre
        for nombre, valor
        in contraindicaciones.items()
        if valor == "Sí"
    ]

    contra_pendientes = [
        nombre
        for nombre, valor
        in contraindicaciones.items()
        if valor == "Sin dato"
    ]

    prec_presentes = [
        nombre
        for nombre, valor
        in precauciones.items()
        if valor == "Sí"
    ]

    prec_pendientes = [
        nombre
        for nombre, valor
        in precauciones.items()
        if valor == "Sin dato"
    ]

    seguridad_incompleta = (
        bool(contra_pendientes)
        or bool(prec_pendientes)
        or laboratorio != "Sí"
        or seguimiento != "Sí"
    )

    st.subheader("6.2. Seguridad farmacológica")

    if contra_presentes:
        st.error(
            "Se identificaron condiciones registradas "
            "como contraindicaciones en el prospecto "
            "de referencia."
        )

        for nombre in contra_presentes:
            st.write(f"- {nombre}")

    elif contra_pendientes:
        st.warning(
            "No es posible descartar todas las "
            "contraindicaciones por falta de datos."
        )

    elif prec_presentes:
        st.warning(
            "Existen precauciones que requieren "
            "valoración individual del riesgo-beneficio."
        )

    elif seguridad_incompleta:
        st.warning(
            "Evaluación de seguridad incompleta."
        )

    else:
        st.success(
            "No se identificaron contraindicaciones "
            "ni precauciones en los campos relevados."
        )

    if prec_presentes:
        st.write("**Precauciones identificadas:**")
        for nombre in prec_presentes:
            st.write(f"- {nombre}")

    if prec_pendientes:
        st.write(
            "**Precauciones sin información suficiente:**"
        )
        for nombre in prec_pendientes:
            st.write(f"- {nombre}")

    st.subheader("6.3. Conclusión orientativa")

    if contra_presentes:
        st.error(
            "Contraindicación registrada. "
            "Revisar el prospecto y la documentación "
            "clínica antes de cualquier decisión."
        )

    elif (
        perfil_incompleto
        or seguridad_incompleta
        or documentacion != "Sí"
    ):
        st.warning(
            "Evaluación incompleta: se requiere "
            "documentación o valoración adicional."
        )

    elif prec_presentes:
        st.warning(
            "Requiere evaluación individual de "
            "riesgo-beneficio por las precauciones "
            "identificadas."
        )

    elif perfil_concordante:
        st.success(
            "Perfil concordante con los criterios "
            "seleccionados del ensayo pivotal, "
            "sin alertas de seguridad registradas."
        )

    else:
        st.warning(
            "No cumple todos los criterios "
            "seleccionados del ensayo pivotal. "
            "La indicación y la cobertura requieren "
            "una evaluación clínica individual."
        )

    if observaciones.strip():
        st.write(
            "**Observaciones del auditor:**"
        )
        st.write(observaciones)

    st.divider()

    st.caption(
        "Herramienta de apoyo a la auditoría. "
        "No constituye una indicación médica, "
        "autorización ni denegación automática. "
        "Los criterios de selección del ensayo "
        "no equivalen a contraindicaciones."
    )
