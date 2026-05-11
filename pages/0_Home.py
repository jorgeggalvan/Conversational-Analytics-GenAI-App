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
# 0 - PÁGINA DE  INICIO
# =====================================================================================

# Subtítulo
st.subheader('📈 La escalera de la sofisticación en los sistemas conversacionales')

# Columnas para centrar imagen 1
col1, col2, col3 = st.columns([1, 5, 1])
# Imagen 1
with col2:
    st.image(ROOT_PATH / 'assets' / 'image1.png', use_container_width=True)

# Encabezado
st.markdown('#### Evaluación de capacidades y puntos críticos')

# Columnas para centrar imagen 2
col4, col5, col6 = st.columns([1, 5, 1])
# Imagen 2
with col5:
    st.image(ROOT_PATH / 'assets' / 'image2.png', use_container_width=True)
