import streamlit as st

st.set_page_config(page_title="Auditoría ELA - Edaravona", layout="centered")
st.title("Auditoría médica | Edaravona en ELA")
st.caption("Prototipo local para pruebas con datos ficticios. No emite autorizaciones automáticas.")

OPCIONES = ["Sin dato", "Sí", "No"]

st.header("1. Diagnóstico y evolución")
diagnostico = st.selectbox("ELA confirmada por neurología", OPCIONES)
meses = st.number_input("Meses desde el primer síntoma", min_value=0, max_value=600, value=None, step=1)
cvf = st.number_input("CVF (% del valor predicho)", min_value=0.0, max_value=200.0, value=None, step=1.0)
progresion = st.number_input("Descenso de ALSFRS-R en las 12 semanas previas (puntos)", min_value=0, max_value=48, value=None, step=1)
grados = ["Sin dato", "1", "2", "3", "4", "5"]
gr_japones = st.selectbox("Grado de severidad según clasificación japonesa", grados)

st.header("2. Escala ALSFRS-R")
st.caption("Puntuar cada función de 0 a 4 según los descriptores oficiales. En el ítem 5, aplicar la variante pertinente según la vía de alimentación.")
items = ["Habla", "Salivación", "Deglución", "Escritura", "Cortar alimentos y manejar utensilios", "Vestirse e higiene", "Girarse en la cama y acomodar las sábanas", "Caminar", "Subir escaleras", "Disnea", "Ortopnea", "Insuficiencia respiratoria"]
puntajes = []
for indice, nombre in enumerate(items, 1):
    valor = st.selectbox(f"{indice}. {nombre}", ["Sin dato", 0, 1, 2, 3, 4], key=f"als_{indice}")
    puntajes.append(valor)
completa = all(isinstance(p, int) for p in puntajes)
if completa:
    st.metric("ALSFRS-R total", f"{sum(puntajes)}/48")
    st.write("Puntaje mínimo entre los ítems:", min(puntajes))
else:
    st.info("Completá los 12 ítems para calcular la escala.")

st.header("3. Seguridad y documentación")
seguridad = st.selectbox("Evaluación de seguridad favorable según prospecto aplicable", OPCIONES)
documentacion = st.selectbox("Informe neurológico y documentación clínica completos", OPCIONES)
observaciones = st.text_area("Observaciones del médico auditor")

st.header("4. Resultado orientativo")
if st.button("Evaluar elegibilidad"):
    criterios = {
        "Diagnóstico confirmado": None if diagnostico == "Sin dato" else diagnostico == "Sí",
        "Evolución ≤24 meses": None if meses is None else meses <= 24,
        "CVF ≥80%": None if cvf is None else cvf >= 80,
        "ALSFRS-R ≥2 en todos los ítems": None if not completa else min(puntajes) >= 2,
        "Descenso ALSFRS-R de 1–4 puntos en 12 semanas": None if progresion is None else 1 <= progresion <= 4,
        "Severidad japonesa grado 1–2": None if gr_japones == "Sin dato" else gr_japones in ("1", "2"),
        "Seguridad favorable": None if seguridad == "Sin dato" else seguridad == "Sí",
        "Documentación completa": None if documentacion == "Sin dato" else documentacion == "Sí",
    }
    for nombre, resultado in criterios.items():
        simbolo = "⚪" if resultado is None else ("✅" if resultado else "❌")
        estado = "Sin dato" if resultado is None else ("Cumple" if resultado else "No cumple")
        st.write(f"{simbolo} **{nombre}:** {estado}")
    if any(valor is None for valor in criterios.values()):
        st.warning("Evaluación incompleta: faltan datos.")
    elif seguridad == "No":
        st.error("Requiere revisión individual de seguridad antes de considerar el tratamiento.")
    elif all(criterios.values()):
        st.success("Perfil concordante con los criterios seleccionados del ensayo pivotal.")
    else:
        st.warning("No cumple todos los criterios seleccionados: requiere evaluación individual.")
    st.caption("Los criterios del ensayo no son contraindicaciones absolutas. Esta herramienta no sustituye el juicio clínico ni las obligaciones regulatorias y de cobertura.")
    if observaciones:
        st.write("**Observaciones:**", observaciones)