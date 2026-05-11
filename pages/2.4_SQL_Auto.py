# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
import pandasql as ps
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
# 2.4 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A SQL + EJECUCIÓN
# =====================================================================================

# Subtítulo
st.subheader('Motor de consultas SQL con lenguaje natural')
# Resumen de sección
st.markdown('Transforma tus preguntas en resultados estructurados al instante. '
            'El motor genera automáticamente la consulta SQL, la ejecuta y muestra la información correspondiente.')

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
with st.form(key='form_sql_auto', border=False):  
    # Pregunta de usuario
    question_sql_auto = st.text_input(placeholder='Escribe una pregunta en el motor SQL automático', key='input_sql_auto', label='', label_visibility='collapsed')
    btn_sql_auto = st.form_submit_button('Generar y ejecutar consulta SQL')

# Convertir pregunta en consulta SQL y ejecutarla
if btn_sql_auto and question_sql_auto:

    # 4. DEFINICIÓN DE PROMPT
    prompt_sql_auto = ('Actúa como un experto en consultas SQL.\n\n'
           
                       '## OBJETIVO:\n'
                       'Convertir la petición del usuario en una consulta SQL válida.\n\n'
                       
                       f'## ESTRUCTURA DE TABLA (COLUMNAS Y TIPOS DE DATOS):\n{schema}\n\n'
    
                       f'## SOLICITUD DE USUARIO:\n{question_sql_auto}\n\n'
                       
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
        response_sql_auto = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_sql_auto)
        sql_generated = response_sql_auto.text
    
        # Conversión de consulta en NL a SQL
        sql_generated = sql_generated.strip()                                          # Eliminación de espacios en blanco al principio y al final
        sql_generated = sql_generated.replace('```sql', '').replace('```', '').strip() # Eliminación de bloques de código Markdown
    
        # 6. EJECUCIÓN DE QUERY
        result_sql_auto = ps.sqldf(sql_generated, {'members': df})

    # 7. RESULTADO DE EJECUCIÓN
    
    # Mostrar resultados
    st.success('Consulta ejecutada correctamente')
    st.dataframe(result_sql_auto)
    
    # Mostrar query
    st.info('Consulta ejecutada:')
    st.code(sql_generated, language='sql') 
