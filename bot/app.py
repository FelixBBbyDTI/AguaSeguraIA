
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

RUTA_ENV = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=RUTA_ENV)

st.set_page_config(
    page_title="AguaSeguraIA",
    page_icon="💧",
    layout="wide"
)

# ==========================================
# 2. PROMPT DEL SISTEMA
# ==========================================

SYSTEM_PROMPT = """
Eres AguaSeguraIA, asesor técnico de calidad del agua
para operadores, técnicos e ingenieros en Perú.

OBJETIVO:
Interpretar mediciones de cloro residual libre en mg/L
y orientar sobre posibles desviaciones respecto al
D.S. N.º 031-2010-SA (MINSA/DIGESA).

LÍMITES:
- No certifiques la potabilidad del agua.
- No emitas diagnósticos sanitarios.
- No inventes datos, mediciones ni referencias.
- No recomiendes dosificaciones químicas exactas.
- No afirmes cumplimiento de toda una red a partir
  de una sola muestra.
- Cuando menciones normativa, identifica la norma
  y explica las condiciones de aplicación.

ENTRADAS:
1. Concentración de cloro residual libre en mg/L.
2. Tipo de punto: entrada, salida o red de distribución.
3. Zona u hora, opcional.

CRITERIOS:
Para redes de distribución, el D.S. N.º 031-2010-SA
establece como criterio de control que al menos el
90 % de las muestras mensuales tengan cloro residual
libre >= 0.5 mg/L y que las restantes tengan
como mínimo 0.3 mg/L.

Una sola medición no permite verificar el cumplimiento
mensual de toda la red.

Para entrada o salida de planta, no apliques
automáticamente el mismo criterio sin conocer
el contexto y las condiciones del sistema.

FORMATO DE RESPUESTA:
1. Resumen de la medición.
2. Comparación con el criterio normativo aplicable.
3. Posibles desviaciones.
4. Causas generales, sin afirmar diagnósticos.
5. Recomendaciones de monitoreo y verificación.

Responde en español técnico, claro y comprensible.

Finaliza siempre con:
"Esta interpretación es orientativa y no certifica
la potabilidad del agua. Para confirmar su calidad,
consulte con un laboratorio competente o con la
autoridad sanitaria correspondiente."
"""

# ==========================================
# 3. CONFIGURACIÓN DE GROQ
# ==========================================

def configuracion():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    modelo = os.getenv(
        "MODEL", "llama-3.1-8b-instant"
    ).strip()

    # En Streamlit Cloud se pueden usar secretos.
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = str(st.secrets["GROQ_API_KEY"]).strip()

        if "MODEL" in st.secrets:
            modelo = str(st.secrets["MODEL"]).strip()
    except (FileNotFoundError, KeyError):
        pass

    return api_key, modelo


# ==========================================
# 4. VALIDACIÓN DE MEDICIONES
# ==========================================

def validar_medicion(cloro, punto):
    if cloro < 0:
        return "Valor inválido: el cloro no puede ser negativo."

    if punto == "Red de distribución":
        if cloro < 0.3:
            return (
                "Medición inferior a 0.3 mg/L. "
                "Se requiere verificación prioritaria."
            )

        if cloro < 0.5:
            return (
                "Medición inferior a 0.5 mg/L. "
                "Debe revisarse dentro del control mensual."
            )

        return (
            "Medición igual o superior a 0.5 mg/L. "
            "No demuestra por sí sola cumplimiento mensual."
        )

    return (
        "Para este punto se necesita conocer el contexto "
        "operativo antes de aplicar un criterio específico."
    )


# ==========================================
# 5. CONSULTA A GROQ
# ==========================================

def consultar_groq(cliente, modelo, mensajes):
    respuesta_api = cliente.chat.completions.create(
        model=modelo,
        messages=mensajes,
        temperature=0.2,
        max_tokens=1000
    )

    contenido = respuesta_api.choices[0].message.content

    if not contenido:
        raise ValueError("Groq devolvió una respuesta vacía.")

    return contenido


# ==========================================
# 6. INTERFAZ PRINCIPAL
# ==========================================

def main():

    st.title("💧 AguaSeguraIA")

    st.caption(
        "Asistente orientativo de monitoreo "
        "de cloro residual libre · Perú"
    )

    st.info(
        "La evaluación de una muestra individual no permite "
        "certificar la potabilidad ni el cumplimiento "
        "mensual de la red."
    )

    api_key, modelo = configuracion()

    if not api_key or api_key == "TU_CLAVE_AQUI":
        st.error(
            "Configura GROQ_API_KEY en tu archivo .env "
            "local o en los secretos de Streamlit Cloud."
        )
        st.stop()

    # ======================================
    # PANEL LATERAL
    # ======================================

    with st.sidebar:

        st.header("Datos de la muestra")

        cloro = st.number_input(
            "Cloro residual libre (mg/L)",
            min_value=0.0,
            max_value=20.0,
            value=0.50,
            step=0.05,
            format="%.2f"
        )

        punto = st.selectbox(
            "Punto de muestreo",
            [
                "Red de distribución",
                "Entrada de planta",
                "Salida de planta"
            ]
        )

        zona = st.text_input(
            "Zona u hora (opcional)"
        )

        st.divider()

        if st.button("Nueva conversación"):
            st.session_state.mensajes = []
            st.rerun()

    # ======================================
    # HISTORIAL DE CONVERSACIÓN
    # ======================================

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    # ======================================
    # ENTRADA DEL USUARIO
    # ======================================

    pregunta = st.chat_input(
        "Pregunta sobre la medición de cloro residual..."
    )

    if pregunta:

        validacion = validar_medicion(cloro, punto)

        consulta = (
            f"Medición: {cloro:.2f} mg/L de cloro residual "
            f"libre.\n"
            f"Punto: {punto}.\n"
            f"Zona/hora: {zona or 'No informado'}.\n"
            f"Evaluación preliminar: {validacion}\n"
            f"Consulta: {pregunta}"
        )

        st.session_state.mensajes.append(
            {
                "role": "user",
                "content": consulta
            }
        )

        with st.chat_message("user"):
            st.write(consulta)

        # ==================================
        # RESPUESTA DEL ASISTENTE
        # ==================================

        with st.chat_message("assistant"):

            with st.spinner("Analizando medición..."):

                respuesta = None

                try:
                    cliente = Groq(api_key=api_key)

                    historial = (
                        st.session_state.mensajes[-12:]
                    )

                    mensajes_api = [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        }
                    ] + historial

                    respuesta = consultar_groq(
                        cliente,
                        modelo,
                        mensajes_api
                    )

                except Exception as e:
                    print(
                        "Error al consultar Groq:",
                        type(e).__name__,
                        str(e)
                    )

                    st.error(
                        "No se pudo consultar Groq. "
                        "Revisa la terminal de VS Code "
                        "para identificar el error."
                    )

            if respuesta:
                st.markdown(respuesta)

                st.session_state.mensajes.append(
                    {
                        "role": "assistant",
                        "content": respuesta
                    }
                )


# ==========================================
# 7. EJECUCIÓN
# ==========================================

if __name__ == "__main__":
    main()
