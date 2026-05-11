# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd

# Configuración inicial de la app de Streamlit
st.set_page_config(page_title = 'Gen-AI App', layout='wide', page_icon='https://www.isdi.education/es/wp-content/uploads/2024/02/cropped-Favicon.png')

# Título principal de la app
st.title('Analítica Conversacional con IA Generativa')
# Línea separadora
st.divider()

# =====================================================================================
# 1.1 - CARGA DE DATOS
# =====================================================================================

# Subtítulo
st.subheader('📥 Carga de datos')
# Texto explicativo
st.write('A continuación se muestran los datos disponibles:')

# 1. LECTURA DE DATASET

# Ruta del dataset
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / 'data' / 'fitlife_members.csv'

# Lectura del dataset
df = pd.read_csv(DATA_PATH)

# 2. EDITOR INTERACTIVO DEL DATASET 

# Todas las columnas excepto 'campaign_active' y 'service_incident'
disabled_columns = [col for col in df.columns if col not in ['campaign_active', 'service_incident']]

# Mostrar dataset interactivo
df_edited = st.data_editor(
    df.reset_index(drop=True), # Dataset        
    hide_index=True,           # Ocultar el índice
    num_rows='dynamic',        # Permitir agregar/eliminar filas
    disabled=disabled_columns, # Columnas no editables
    height=500
)

# Actualización de DataFrame con los cambios realizados en el editor
df = df_edited
