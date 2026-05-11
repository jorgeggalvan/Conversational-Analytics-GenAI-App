# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

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
# 3.2 - EJECUCIÓN DE CÓDIGO DE PYTHON
# =====================================================================================

# Subtítulo
st.subheader('Editor manual de código con Python')
# Resumen de sección
st.markdown('Aquí puedes ejecutar código con Pandas para procesar el DataFrame **`df`**. '
            'El resultado final debe almacenarse en la variable **`result`** para poder mostrarlo o graficarlo.\n\n'
                    
            "**Ejemplo:**\n"
            "```python\n"
            "cond = df['month'] == df['month'].max()\n\n"
            "top_members = df[cond]\\\n"
            "    .groupby('member_id').agg({'visits_this_month':'sum'})\\\n"
            "    .sort_values('visits_this_month', ascending=False)\\\n"
            "    .head(10)\n\n"
            "result = top_members\n"
            "```")

# 1. CÓDIGO DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_py_editor', border=False):  
    code = st.text_area(placeholder='Escribe código con Python para ejecutar sobre el DataFrame', height=125, key='input_py_editor', label='', label_visibility='collapsed')
    btn_py_editor = st.form_submit_button('Ejecutar código')

# 2. EJECUCIÓN DE CÓDIGO DE PYTHON
if btn_py_editor and code:
    
    # Variables locales
    local_vars = {'df': df, 'pd': pd, 'np': np, 'plt': plt, 'sns': sns, 'px': px}

    # Ejecución de todo el código
    exec(code, {'__builtins__': __builtins__}, local_vars)
    # {} es el diccionario para que se no tenga acceso a las variables del script
    # local_vars es el diccionario donde se guardan todas las variables creadas o modificadas durante la ejecución

    # Recuperar variable 'result'
    result = local_vars.get('result', None)
    
    # Mostrar que no se ha encontrado 'result'    
    if result is None:
        st.warning("No se encontró la variable 'result'. Asegúrate de definirla.")

    # 3. RESULTADO DE EJECUCIÓN
    else:
        # Mostrar resultados númericos        
        if isinstance(result, (int, float, np.integer, np.floating)):
            st.success('Código ejecutado correctamente')
            st.write(result)
    
        # Mostrar DataFrame o Series
        elif isinstance(result, (pd.DataFrame, pd.Series)):
            st.success('Código ejecutado correctamente')
            st.dataframe(result)
    
        # Mostrar gráfico de Seaborn o Matplotlib
        elif hasattr(result, 'plot') or isinstance(result, plt.Axes):
            st.success('Gráfico generado correctamente')
            st.pyplot(result.figure if hasattr(result, 'figure') else plt.gcf())
        
        else:
            st.success('Código ejecutado correctamente')
            st.write(result)
        