# AguaSeguraIA

Chatbot educativo para interpretar mediciones de cloro residual libre en agua para consumo humano en Perú. Desarrollado con Streamlit y la API de Groq.

## Estructura

- `app.py`: interfaz y lógica del chatbot.
- `requirements.txt`: dependencias.
- `.env`: configuración privada local (no subir a GitHub).
- `.gitignore`: exclusiones de Git.

## Ejecutar en Windows con VS Code

1. Abre la carpeta `bot` en VS Code o entra a ella desde la terminal.
2. Crea el entorno virtual: `py -m venv venv`
3. Actívalo en PowerShell: `./venv/Scripts/Activate.ps1` (si la política de ejecución lo impide, usa `venv\Scripts\python.exe` directamente para los pasos siguientes).
4. Instala las dependencias: `python -m pip install -r requirements.txt`
5. En `.env`, configura `GROQ_API_KEY` con una clave nueva y `MODEL=llama-3.1-8b-instant`. No publiques el archivo ni compartas la clave.
6. Ejecuta: `streamlit run app.py`
7. Abre la dirección local que muestra Streamlit, habitualmente `http://localhost:8501`.

Si no activaste el entorno, puedes usar `venv\Scripts\python.exe -m pip install -r requirements.txt` y `venv\Scripts\python.exe -m streamlit run app.py`.

## Streamlit Cloud

Configura `GROQ_API_KEY` y `MODEL` en los secretos de la aplicación, sin subir `.env` al repositorio. Mantén `requirements.txt` en la misma carpeta que `app.py`.

## Advertencia

Las respuestas son orientativas. Una sola medición no certifica potabilidad ni demuestra cumplimiento mensual. Verifica los criterios aplicables del D.S. N.º 031-2010-SA con un profesional o autoridad competente.
