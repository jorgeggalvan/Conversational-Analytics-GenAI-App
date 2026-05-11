# Importación de librerías
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import pandas as pd
from ydata_profiling import ProfileReport

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
# 1.2 - PERFILADO DE DATOS
# =====================================================================================

# Subtítulo
st.subheader('📝 Reporte de perfilado')

with st.spinner('Generando informe de perfil...'):
    # Generación de informe de perfil
    profile = ProfileReport(df, explorative=True)
        
    # Mostrar informe HTML dentro de Streamlit
    components.html(profile.to_html(), height=1200, scrolling=True)
