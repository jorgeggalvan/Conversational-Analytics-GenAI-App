# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
from google import genai
import ollama

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
# 2.1 - CÁLCULO DIRECTO
# =====================================================================================

# Subtítulo
st.subheader('🔢 LLM directo')
# Resumen de sección
st.markdown('Utiliza este chat para realizar preguntas sobre FitLife. '
            'El modelo responderá basándose directa y únicamente en la información contenida en el dataset.')

# 1. INICIALIZACIÓN DE LLM

# API Key
GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
# Selección de modelo
GEMINI_MODEL = 'gemini-2.5-flash'

# Client Gemini
gemini = genai.Client(api_key=GEMINI_API_KEY)

# 2. VARIABLES CONTEXTUALES

# Datos
data = df.to_string()
# Muestra de datos
data_sample = df[df['month'] >= '2024-01'].head(20).to_string()
# Estructura de DataFrame
schema = df.dtypes.to_string()

# 3. SOLICITUD DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_llm', border=False):
    # Pregunta de usuario
    question_llm = st.text_input(placeholder='Escribe una pregunta sobre los datos', key='input_llm', label='', label_visibility='collapsed')
    btn_llm = st.form_submit_button('Preguntar sobre los datos')

# Responder pregunta sobre los datos
if btn_llm and question_llm:
        
    # 4. DEFINICIÓN DE PROMPT
    prompt_llm = ('Actúa como un Senior Data Analyst experto en el sector de fitness y gestión de gimnasios.\n\n'

                  '## OBJETIVO:\n'
                  'Responder de forma precisa, técnica y analítica a la solicitud del usuario sobre los datos.\n\n'
                  
                  f'## DATOS DISPONIBLES:\n{data_sample}\n\n'
                  
                  f'## SOLICITUD DE USUARIO:\n{question_llm}\n\n'
           
                  '## INSTRUCCIONES OBLIGATORIAS:\n'
                  '1. Basa tu respuesta únicamente en los datos proporcionados.\n'
                  '2. Evita suposiciones o datos inventados.\n\n'
                  
                  '## FORMATO DE RESPUESTA:\n'
                  '- Sé conciso y claro; máximo una línea de explicación intermedia si es necesaria.\n'
                  '- Devuelve sólo la información solicitada. Si es cálculo o resumen, muestra sólo el resultado principal.'
                 ) 

    # 5. LLAMADA Y PROCESAMIENTO DEL LLM
    with st.spinner('El LLM está procesando tu pregunta...'):

        # Llamada al LLM con Gemini
        #response_llm = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_llm)
        #response_llm = response_llm.text

        # Llamada al LLM con OpenAI
        #response_llm = openai.responses.create(model=GPT_MODEL, input=prompt_llm)
        #response_llm = response_llm.output_text

        # Llamada al LLM con Ollama
        response_llm = ollama.generate(model='llama3', prompt=prompt_llm, options={'temperature': 0.1})
        response_llm = response_llm['response']

    # 6. RESULTADO DEL LLM
    st.success('Análisis completado')
    st.write(response_llm)
