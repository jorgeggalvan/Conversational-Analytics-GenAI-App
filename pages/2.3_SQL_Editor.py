# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
import pandasql as ps

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
# 2.1 - EDITOR DE CONSULTAS SQL
# =====================================================================================

# Subtítulo
st.subheader('Editor manual de consultas SQL')
# Resumen de sección
st.markdown('Escribe y ejecuta tus propias consultas SQL para explorar los datos de FitLife. '
            'Usa la sintaxis estándar de SQL y las columnas de **`members`**.\n\n'
            
            '**Ejemplo:**\n'
            '```sql\n'
            'SELECT member_id, SUM(visits_this_month) AS visits_last_month\n'
            'FROM members\n'
            'WHERE month = "2024-12"\n'
            'GROUP BY 1\n'
            'ORDER BY 2 DESC\n'
            'LIMIT 10\n'
            '```')

# 1. QUERY DE USUARIO

# Formulario con caja de texto y botón
with st.form(key='form_sql_editor', border=False):
    # Query de usuario
    query = st.text_area(placeholder='Escribe una query', height=30, key='input_sql_editor', label='', label_visibility='collapsed')
    btn_sql_editor = st.form_submit_button('Ejecutar query')

# Ejecutar consultas con SQL
if btn_sql_editor and query:
    
    # 2. EJECUCIÓN DE QUERY
    result_sql_editor = ps.sqldf(query, {'members': df})

    # 3. RESULTADO DE QUERY
    st.success('Query ejecutada correctamente')
    st.dataframe(result_sql_editor)
