# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
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
# 4.4.1 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A CÓDIGO + EJECUCIÓN
# =====================================================================================

# Subtítulo
st.subheader('Motor de código con lenguaje natural')
# Resumen de sección
st.markdown('Pasa de la pregunta al resultado en un sólo paso. '
            'Escribe lo que quieres analizar, y el sistema se encarga de generar, ejecutar y mostrar/visualizar los resultados automáticamente.')

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

# Variables de resultado iniciales
result_strategic = None
fig_strategic = None

# 3. SOLICITUD DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_py_strategic', border=False):
    # Pregunta de usuario
    question_py_strategic = st.text_input(placeholder='Escribe una pregunta en el motor de código automático', key='input_py_strategic', label='', label_visibility='collapsed')
    btn_py_strategic = st.form_submit_button('Generar y ejecutar código Python')

# Convertir pregunta en código y ejecutarlo
if btn_py_strategic and question_py_strategic:
    
    # 4. DEFINICIÓN DE PROMPT
    prompt_py_strategic = ('Actúa como un experto en Data Science especializado en Python, Pandas y Plotly.\n\n'
    
                      '## OBJETIVO:\n'
                      'Generar código Python ejecutable para resolver la consulta del usuario basada en el contexto proporcionado.\n\n'
                      
                      '## CONTEXTO ANALÍTICO:\n'
                      f'### GLOSARIO DE NEGOCIO:\n{business_glossary}\n\n'
                      f'### ESTRUCTURA DE TABLAS:\n{schema}\n\n'
                      f'### ESTADÍSTICAS DE COLUMNAS CATEGÓRICAS:\n{str_stats}\n\n'
                      f'### ESTADÍSTICAS DE COLUMNAS NUMÉRICAS:\n{num_stats}\n\n'
                      f'### RANGO DE FECHAS:\n{date_ranges}\n\n'

                      f'## SOLICITUD DE USUARIO:\n{question_py_strategic}\n\n'
               
                      '## INSTRUCCIONES OBLIGATORIAS:\n'
                      '1. El DataFrame se llama exactamente \"df\" y ya está cargado en memoria.\n'
                      '2. Usa únicamente Pandas para manipulación y plotly.express (importado como px) para visualización.\n'
                      '3. Aplica filtrado de filas, agregaciones con agg() y groupby() y ordenamiento con sort_values().\n'
                      '4. El DataFrame, Series o valor numérico resultante debe asignarse a la variable \"result\".\n'
                      '5. Genera siempre una visualización que mejor represente los resultados obtenidos.'
                        ' Si el resultado es un valor único, crea un indicador.\n'
                      '6. El objeto Figure o Axes debe asignarse a la variable \"fig\".\n\n'

                      '## FORMATO DE RESPUESTA:\n'
                      '- Devuelve sólo el código Python, sin incluir comentarios ni explicaciones adicionales.'
                     )

    # 5. LLAMADA Y PROCESAMIENTO DEL LLM
    with st.spinner('El LLM está procesando tu consulta...'):

        # Llamada al LLM con Gemini
        response_py_strategic = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_py_strategic)
        py_generated = response_py_strategic.text

        # 6. RESULTADOS DEL CÓDIGO GENERADO POR LLM
        
        # Conversión de consulta en NL a código
        py_generated = py_generated.strip()                                             # Eliminación de espacios en blanco al principio y al final
        py_generated = py_generated.replace('```python', '').replace('```', '').strip() # Eliminación de bloques de código Markdown

        # 7. EJECUCIÓN DE CÓDIGO DE PYTHON

        # Diccionario de variables locales para ejecutar el código
        local_vars = {'df': df, 'pd': pd, 'np': np, 'plt': plt, 'sns': sns, 'px': px}
        
        # Ejecución de código generado
        exec(py_generated, {'__builtins__': __builtins__}, local_vars)

        # Recuperar 'result' y 'fig'
        result_strategic = local_vars.get('result')
        fig_strategic = local_vars.get('fig')

    # 8. RESULTADO DE EJECUCIÓN
    
    # Mostrar visualización si hay
    if fig_strategic is not None:
        st.success('Gráfico generado correctamente')
        st.plotly_chart(fig_strategic, width='stretch')

    # Mostrar visualización DataFrame, Series o valor numérico si no hay visualización
    else:
        if result_strategic is None:
            st.warning("No se encontró la variable 'result'")
        
        elif isinstance(result_strategic, (int, float, np.integer, np.floating)):
            st.success('Código ejecutado correctamente')
            st.write(result_strategic)
            
        elif isinstance(result_strategic, (pd.DataFrame, pd.Series)):
            st.success('Código ejecutado correctamente')
            st.dataframe(result_strategic)

            result_strategic = result_strategic.to_markdown(index=False)
            
        else:
            st.success('Código ejecutado correctamente')
            st.write(result_strategic)

    # Mostrar código
    with st.expander('Código ejecutado', expanded=False):
        st.code(py_generated, language='python')

# =====================================================================================
# 4.4.2 - GENERACIÓN DE INTERPRETACIONES/CONCLUSIONES DEL RESULTADO
# =====================================================================================

# Encabezado
st.markdown('##### Panel de alertas y estrategia prescriptiva')

# Definir plan estratégico tras resultados analíticos
with st.expander('Ruta estratégica de IA', expanded=True):

    if result_strategic is not None:
        
        # 9. DEFINICIÓN DE PROMPT
        prompt_strategic = ('Actúa como el Director de Operaciones (COO) de la cadena de gimnasios FitLife.\n\n'
                            
                            '## OBJETIVO:\n'
                            'Generar un plan de acción claro, directo y ejecutable basado en los resultados actuales y el contexto proporcionado.\n\n'
                            
                            '## CONTEXTO ANALÍTICO:\n'
                            f'### GLOSARIO DE NEGOCIO:\n{business_glossary}\n\n'
                            f'### ESTADÍSTICAS CATEGÓRICAS:\n{str_stats}\n\n'
                            f'### ESTADÍSTICAS HISTÓRICAS GENERALES:\n{num_stats}\n\n'
                            f'### RANGO DE FECHAS:\n{date_ranges}\n\n'

                            f'## SOLICITUD DE USUARIO:\n{question_py_strategic}\n\n'
                            f'## RESULTADOS A ANALIZAR:\n{result_strategic}\n\n'
                            
                            '## INSTRUCCIONES OBLIGATORIAS:\n'
                            '1. No expliques los datos, prescribe soluciones. El análisis ya se hizo, ahora toca ejecutar.\n'
                            '2. Usa verbos de acción imperativos.\n'
                            '3. No menciones ni describas elementos técnicos (código, DataFrame tabla o columnas).\n'
                            '4. El tono debe ser profesional, ejecutivo y orientado a la toma de decisiones.\n'
                            '5. Si los datos son insuficientes para una clara, sugiere qué métrica adicional deberíamos analizar.\n\n'

                            '## FORMATO DE RESPUESTA:\n'
                            '- Empieza directamente con el contenido, sin introducciones.\n'
                            '- Usa exclusivamente Markdown enriquecido (negritas, listas).\n'
                            '- Respeta la siguiente estructura de tres bloques:\n\n'

                            '🚨 **ALERTAS DE RIESGO**: Identifica desviaciones críticas o peligros en los datos actuales.\n'
                            '⚡ **ACCIONES PRIORITARIAS**: Enumera 2-4 pasos exactos que el staff debe ejecutar HOY.\n'
                            '🚀 **ESTRATEGIA A LARGO PLAZO**: Indica una recomendación para prevenir este problema en el futuro o para escalar el éxito detectado.'
                            )

        # 10. LLAMADA Y PROCESAMIENTO DEL LLM
        with st.spinner('El LLM está interpretando el resultado...'):

            # Llamada al LLM con Gemini
            response_strategic = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_strategic)
            response_strategic = response_strategic.text
    
            # 11. RESULTADO DEL LLM
            st.markdown(response_strategic)

    else:
        st.write('👉 Escribe una pregunta arriba para activar el plan estratégico.')
