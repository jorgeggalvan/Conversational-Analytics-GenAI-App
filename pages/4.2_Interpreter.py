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
# 4.2.1 - CONVERSIÓN DE CONSULTAS EN LENGUAJE NATURAL A CÓDIGO + EJECUCIÓN
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
result_interpret = None
fig_interpret = None

# 3. SOLICITUD DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_py_interpret', border=False):
    # Pregunta de usuario
    question_py_interpret = st.text_input(placeholder='Escribe una pregunta en el motor de código automático', key='input_py_interpret', label='', label_visibility='collapsed')
    btn_py_interpret = st.form_submit_button('Generar y ejecutar código Python')

# Convertir pregunta en código y ejecutarlo
if btn_py_interpret and question_py_interpret:
    
    # 4. DEFINICIÓN DE PROMPT
    prompt_py_interpret = ('Actúa como un experto en Data Science especializado en Python, Pandas y Plotly.\n\n'
                           
                           '## OBJETIVO:\n'
                           'Generar código Python ejecutable para resolver la consulta del usuario basada en el contexto proporcionado.\n\n'
                           
                           '## CONTEXTO ANALÍTICO:\n'
                           f'### GLOSARIO DE NEGOCIO:\n{business_glossary}\n\n'
                           f'### ESTRUCTURA DE TABLAS:\n{schema}\n\n'
                           f'### ESTADÍSTICAS DE COLUMNAS CATEGÓRICAS:\n{str_stats}\n\n'
                           f'### ESTADÍSTICAS DE COLUMNAS NUMÉRICAS:\n{num_stats}\n\n'
                           f'### RANGO DE FECHAS:\n{date_ranges}\n\n'
                           
                           f'## SOLICITUD DE USUARIO:\n{question_py_interpret}\n\n'
                           
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
        response_py_interpret = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_py_interpret)
        py_generated = response_py_interpret.text

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
        result_interpret = local_vars.get('result')
        fig_interpret = local_vars.get('fig')

    # 8. RESULTADO DE EJECUCIÓN
    
    # Mostrar visualización si hay
    if fig_interpret is not None:
        st.success('Gráfico generado correctamente')
        st.plotly_chart(fig_interpret, width='stretch')

    # Mostrar visualización DataFrame, Series o valor numérico si no hay visualización
    else:
        if result_interpret is None:
            st.warning("No se encontró la variable 'result'")
        
        elif isinstance(result_interpret, (int, float, np.integer, np.floating)):
            st.success('Código ejecutado correctamente')
            st.write(result_interpret)
            
        elif isinstance(result_interpret, (pd.DataFrame, pd.Series)):
            st.success('Código ejecutado correctamente')
            st.dataframe(result_interpret)

            result_interpret = result_interpret.to_markdown(index=False)
            
        else:
            st.success('Código ejecutado correctamente')
            st.write(result_interpret)

    # Mostrar código
    with st.expander('Código ejecutado', expanded=False):
        st.code(py_generated, language='python')

# =====================================================================================
# 4.2.2 - GENERACIÓN DE INTERPRETACIONES/CONCLUSIONES DEL RESULTADO
# =====================================================================================

# Encabezado
st.markdown('##### Interpretador de resultados')

# Interpretar resultados analíticos generados
with st.expander('Interpretación de IA', expanded=True):

    if result_interpret is not None:

        # 9. DEFINICIÓN DE PROMPT
        prompt_interpret = ('Actúa como un Senior Data Storyteller experto en el sector fitness y gestión de gimnasios.\n\n'
                            
                            '## OBJETIVO:\n'
                            'Interpretar los resultados analíticos y detectar hallazgos en lenguaje claro, '
                            'explicando qué significan para la salud del gimnasio (FitLife).\n\n'
                                                                    
                            '## CONTEXTO ANALÍTICO:\n'
                            f'### GLOSARIO DE NEGOCIO:\n{business_glossary}\n\n'
                            f'### ESTADÍSTICAS HISTÓRICAS GENERALES:\n{num_stats}\n\n'
                            
                            f'## RESULTADOS A INTERPRETAR: {result_interpret}\n\n'
                            
                            '## INSTRUCCIONES OBLIGATORIAS:\n'
                            '1. Basa tu análisis exclusivamente en los datos proporcionados y el glosario, sin inventar tendencias ni comparaciones.\n'
                            '2. No menciones ni describas elementos técnicos (código, DataFrame tabla o columnas).\n'
                            '3. El tono debe ser profesional, ejecutivo y orientado a la toma de decisiones.\n'
                            '4. Si los datos son insuficientes para una conclusión sólida, indícalo y sugiere qué métrica adicional deberíamos consultar.\n\n'
                            
                            '## FORMATO DE RESPUESTA:\n'
                            '- Empieza directamente con el contenido, sin introducciones.\n'
                            '- Usa exclusivamente Markdown enriquecido (negritas, listas).\n'
                            '- Respeta la siguiente estructura de tres bloques:\n\n'
                            
                            '1. 🎯 **VISIÓN EJECUTIVA**\n'
                            '   - Crea un titular breve en negrita que resuma el hallazgo principal.\n'
                            '   - Si hay una/s cifra/s clave/s, menciónala aquí.\n\n'
                            '2. 💡 **INSIGHT DE NEGOCIO**\n'
                            '   - Explica el por qué (causas, hallazgos ocultos, cruce de conocimiento datos) de estos datos en base a los datos.\n'
                            '   - Identifica si es una anomalía, una tendencia positiva o un riesgo.\n'
                            '   - Compara los valores si el resultado es una lista o tabla.\n\n'
                            '3. 📈 **IMPACTO Y ACCIÓN**\n'
                            '   - Explica cómo afecta esto a la rentabilidad de FitLife y experiencia de los miembros.\n'
                            '   - Propón una acción concreta e inmediata para el equipo del gimnasio.'
                           )

        # 10. LLAMADA Y PROCESAMIENTO DEL LLM
        with st.spinner('El LLM está interpretando el resultado...'):

            # Llamada al LLM con Gemini
            response_interpret = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_interpret)
            response_interpret = response_interpret.text
    
            # 11. RESULTADO DE INTERPRETACIÓN DE LLM
            st.markdown(response_interpret)

    else:
        st.write('👉 Escribe una pregunta arriba para obtener un interpretración.')
    