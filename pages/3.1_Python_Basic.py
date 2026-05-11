# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
from google import genai

# Configuración inicial de la app de Streamlit
st.set_page_config(page_title = 'Gen-AI App', layout='wide', page_icon='https://www.isdi.education/es/wp-content/uploads/2024/02/cropped-Favicon.png')

# Título principal de la app
st.title('Analítica Conversacional con IA Generativa')
# Línea separadora
st.divider()

# Ruta del dataset
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / 'data' / 'fitlife_members.csv'

# Lectura del dataset
df = pd.read_csv(DATA_PATH)

# =====================================================================================
# 3.1 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A CÓDIGO
# =====================================================================================

# Subtítulo
st.subheader('Generador de código básico')
# Resumen de sección
st.markdown('Convierte tus instrucciones en lenguaje natural en código Python con Pandas que procesa el dataset. '
            'El código generado aplica filtrado de filas, agregaciones y ordenamiento según tu descripción.')

# 1. INICIALIZACIÓN DE LLM

# API Key
GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
# Selección de modelo
GEMINI_MODEL = 'gemini-2.5-flash'

# Client Gemini
gemini = genai.Client(api_key=GEMINI_API_KEY)

# 2. VARIABLES CONTEXTUALES

# Estructura de DataFrame
schema = df.dtypes.to_string()

# 3. SOLICITUD DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_py_code1', border=False):
    # Pregunta de usuario
    question_py_code1 = st.text_input(placeholder='Escribe una consulta en lenguaje natural para convertirla en código', key='input_py_code1', label='', label_visibility='collapsed')
    btn_py_code1 = st.form_submit_button('Generar código Python')

# Convertir pregunta a código de Python
if btn_py_code1 and question_py_code1:
    
    # 4. DEFINICIÓN DE PROMPT
    prompt_py_code1 = ('Actúa como un experto en Data Analysis especializado en Python y Pandas.\n\n'

                       '## OBJETIVO:\n'
                       'Generar código Python ejecutable para resolver la petición del usuario.\n\n'

                       f'## ESTRUCTURA DE TABLA:\n{schema}\n\n'

                       f'## SOLICITUD DE USUARIO:\n{question_py_code1}\n\n'
                       
                       '## INSTRUCCIONES OBLIGATORIAS:\n'
                       '1. El DataFrame se llama exactamente \"df\" y ya está cargado en memoria.\n'
                       '2. Usa únicamente Pandas para manipulación. No incluyas visualizaciones ni gráficos.\n'
                       '3. Aplica filtrado de filas, agregaciones con agg() y groupby() y ordenamiento con sort_values().\n'
                       '4. El resultado definitivo debe asignarse a la variable \"result\".\n\n'
                       
                       '## FORMATO DE RESPUESTA:\n'
                       '- Devuelve sólo el código Python, sin texto adicional.'
                      )

    # 5. LLAMADA Y PROCESAMIENTO DEL LLM
    with st.spinner('El LLM está procesando tu consulta...'):

        # Llamada al LLM con Gemini
        response_py_code1 = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_py_code1)
        response_py_code1 = response_py_code1.text

    # 6. RESULTADO DEL LLM
    st.success('Código generado')
    st.write(response_py_code1)
