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
# 2.2 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A SQL
# =====================================================================================

# Subtítulo
st.subheader('Generador de consultas SQL')
# Resumen de sección
st.markdown('Convierte descripciones en lenguaje natural en consultas SQL listas para ejecutar. '
            'Escribe en palabras simples lo que necesitas y obtendrás la consulta preparada para copiar y ejecutar.')

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
with st.form(key='form_sql_code', border=False):
    # Pregunta de usuario
    question_sql_code = st.text_input(placeholder='Escribe una consulta en lenguaje natural para convertirla en SQL', key='input_sql_code', label='', label_visibility='collapsed')
    btn_sql_code = st.form_submit_button('Generar consulta SQL')

# Convertir pregunta en consulta SQL
if btn_sql_code and question_sql_code:

    # 4. DEFINICIÓN DE PROMPT
    prompt_sql_code = ('Actúa como un experto en consultas SQL.\n\n'

                       '## OBJETIVO:\n'
                       'Convertir la solicitud del usuario en una consulta SQL válida.\n\n'

                       f'## ESTRUCTURA DE TABLA (COLUMNAS Y TIPOS DE DATOS):\n{schema}\n\n'

                       f'## SOLICITUD DE USUARIO:\n{question_sql_code}\n\n'
                                                          
                       '## INSTRUCCIONES OBLIGATORIAS:\n'
                       '1. La tabla se llama exactamente members y no debe ir entre comillas.\n'
                       '2. Todas las variables (columnas) deben ir entre comillas dobles "".\n'
                       '3. Usa comillas simples para valores de texto.\n'
                       '4. Usa únicamente las columnas proporcionadas.\n\n'
                       
                       '## FORMATO DE RESPUESTA:\n'
                       '- Devuelve sólo el código SQL, sin texto adicional.'
                      ) 

    # 5. LLAMADA Y PROCESAMIENTO DEL LLM
    with st.spinner('El LLM está procesando tu consulta...'):

        # Llamada al LLM con Gemini
        response_sql_code = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_sql_code)
        response_sql_code = response_sql_code.text

    # 6. RESULTADO DEL LLM 
    st.success('Consulta generada')
    st.write(response_sql_code)
    