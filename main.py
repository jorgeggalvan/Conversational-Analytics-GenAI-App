# Importación de librerías
import streamlit as st

# 1. PÁGINAS DE APP

# Inicio: Página de Inicio
home = st.Page('pages/0_Home.py', title='Página de Inicio', icon='🏠', default=True)

# Sección 1: Análisis descriptivo
data = st.Page('pages/1.1_Load_Data.py', title='Carga de Datos', icon='📥')
profile = st.Page('pages/1.2_Profile_Report.py', title='Reporte de Perfilado', icon='📝')
metrics = st.Page('pages/1.3_Metrics.py', title='Indicadores de Negocio', icon='🎯')
visualization = st.Page('pages/1.4_Visualization.py', title='Visualización Descriptiva', icon='📊')

# Sección 2: Text-to-SQL
zero_shot = st.Page('pages/2.1_Zero_Shot.py', title='LLM Directo', icon='🔢')
sql_code = st.Page('pages/2.2_SQL_Code.py', title='Generador de SQL', icon='💻')
sql_editor = st.Page('pages/2.3_SQL_Editor.py', title='Editor de SQL', icon='⌨️')
sql_auto = st.Page('pages/2.4_SQL_Auto.py', title='Motor de SQL Autónomo', icon='⚙️')

# Sección 3: 
py_code1 = st.Page('pages/3.1_Python_Basic.py', title='Generador de Python Básico', icon='🐍')
py_editor = st.Page('pages/3.2_Python_Editor.py', title='Editor de Python', icon='⌨️')
py_code2 = st.Page('pages/3.3_Python_Advanced.py', title='Generador de Python Avanzado', icon='🐍')
py_code3 = st.Page('pages/3.4_Python_Governed.py', title='Generador Gobernado de Python', icon='🐍')

# Sección 4: Análisis prescriptivo
py_auto = st.Page('pages/4.1_Python_Auto.py', title='Motor de Python Autónomo', icon='⚙️')
interpreter = st.Page('pages/4.2_Interpreter.py', title='Interpretador de Resultados', icon='🧠')
ml = st.Page('pages/4.3_Predictor.py', title='Predictor de Churn', icon='🔮')
recommender = st.Page('pages/4.4_Recommender.py', title='Recomendador Estratégico', icon='💡')

# 2. MENÚ DE NAVEGACIÓN
pg = st.navigation({
    'Principal': [home],
    'Sistema de Decisión Descriptivo': [data, profile, metrics, visualization],
    'Sistema Parametrizable Conversacional': [zero_shot, sql_code, sql_editor, sql_auto],
    'Sistema de Analítica de Negocio Inteligente': [py_code1, py_editor, py_code2, py_code3],
    'Sistema Autónomo de Accionabilidad': [py_auto, interpreter, ml, recommender]
})

# 3. EJECUCIÓN
pg.run()