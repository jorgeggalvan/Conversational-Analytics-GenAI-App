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
# 3.4 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A CÓDIGO (CON GLOSARIO DE NEGOCIO)
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

# Valores únicos de variables categóricas
str_stats = df.select_dtypes(exclude='number').drop(columns=['month', 'signup_date']).describe().T.drop(columns='count')
str_stats['values'] = [df[col].unique()[:5].tolist() for col in str_stats.index]
str_stats['nulls'] = df[str_stats.index].isnull().sum()
str_stats = str_stats.reset_index().rename(columns={'index': 'column'}).to_markdown(index=False)

# Estadísticas básicas de variables numéricas
num_cols = df.select_dtypes(include='number').drop(columns=['month_num', 'quarter', 'year'], errors='ignore').columns
num_stats = df[num_cols].describe().T
num_stats['nulls'] = df[num_cols].isnull().sum()
num_stats = num_stats.reset_index().rename(columns={'index': 'column'}).to_markdown(index=False)

# Rangos de fechas
date_ranges = df[['month', 'signup_date']].agg(['min', 'max']).T
date_ranges['nulls'] = df[date_ranges.index].isnull().sum()
date_ranges = date_ranges.reset_index().rename(columns={'index': 'column'}).to_markdown(index=False)

# Ruta del glosario de negocio
GLOSSARY = ROOT_PATH / 'data' / 'fitlife_glossary.csv'
# Glosario de negocio
data_glossary = pd.read_csv(GLOSSARY)
business_glossary = data_glossary.to_markdown(index=False)

# 3. SOLICITUD DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_py_code3', border=False):
    # Pregunta de usuario
    question_py_code3 = st.text_input(placeholder='Escribe una consulta en lenguaje natural para convertirla en código', key='input_py_code3', label='', label_visibility='collapsed')
    btn_py_code3 = st.form_submit_button('Generar código Python')

# Convertir pregunta a código de Python
if btn_py_code3 and question_py_code3:
    
    # 4. DEFINICIÓN DE PROMPT
    prompt_py_code3 = ('Actúa como un experto en Data Science especializado en Python, Pandas y Seaborn.\n\n'
                       
                       '## OBJETIVO:\n'
                       'Generar código Python ejecutable para resolver la petición del usuario basada en el contexto proporcionado.\n\n'
                       
                       '## CONTEXTO ANALÍTICO:\n'
                       f'### GLOSARIO DE NEGOCIO:\n{business_glossary}\n\n'
                       f'### ESTRUCTURA DE TABLAS:\n{schema}\n\n'
                       f'### ESTADÍSTICAS DE COLUMNAS CATEGÓRICAS:\n{str_stats}\n\n'
                       f'### ESTADÍSTICAS DE COLUMNAS NUMÉRICAS:\n{num_stats}\n\n'
                       f'### RANGO DE FECHAS:\n{date_ranges}\n\n'
                        
                       f'## SOLICITUD DE USUARIO:\n{question_py_code3}\n\n'
                        
                       '## INSTRUCCIONES OBLIGATORIAS:\n'
                       '1. El DataFrame se llama exactamente \"df\" y ya está cargado en memoria.\n'
                       '2. Usa únicamente Pandas para manipulación y plotly.express (importado como px) para visualización.\n'
                       '3. Aplica filtrado de filas, agregaciones con agg() y groupby() y ordenamiento con sort_values().\n'
                       '4. El resultado definitivo debe asignarse a la variable \"result\".\n\n'
                        
                       '## FORMATO DE RESPUESTA:\n'
                       '- Devuelve sólo el código Python, sin texto adicional.'
                      )

    # 5. LLAMADA Y PROCESAMIENTO DEL LLM
    with st.spinner('El LLM está procesando tu consulta...'):

        # Llamada al LLM con Gemini
        response_py_code3 = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_py_code3)
        response_py_code3 = response_py_code3.text

    # 6. RESULTADO DEL LLM
    st.success('Código generado')
    st.write(response_py_code3)
