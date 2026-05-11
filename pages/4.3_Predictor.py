# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
from google import genai

from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, recall_score

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

# ================================================================================
# 4.3.1 - MODELO DE ML PARA PREDECIR CHURN
# ================================================================================

# Subtítulo
st.subheader('Predictor de *churn*')

# Función cacheada para entrenar modelo de ML
@st.cache_resource
def train_model():
 
    df_model = df.copy()
    
    # Preparación de variables

    # Ordenar cronológicamente por miembro
    df_model = df_model.sort_values(['member_id', 'month'])
        
    # Gestión de nulos
    df_model['satisfaction_survey'] = df_model['satisfaction_survey'].fillna(df_model['satisfaction_survey'].median())
    df_model = df_model.fillna(0)

    # Creación de variable dependiente
    df_model['target_churn'] = df_model.groupby('member_id')['status'].shift(-1).apply(lambda x: 1 if x == 'churned' else 0)
    
    # Cálculo de diferencia de precio respecto a la competencia
    df_model['price_diff'] = df_model['price_paid'] - df_model['competitor_lowcost_price']

    # Cálculo de diferencia de visitas vs. hace 1 mes
    df_model['visits_diff_1m'] = df_model.groupby('member_id')['visits_this_month'].diff(periods=1)
    
    # Eliminación de la última fila de cada socio
    df_model = df_model.dropna(subset=['target_churn', 'visits_diff_1m'])
    
    # Lista de variables independientes
    features = [
        'age',
        'price_diff',
        'tenure_months',
        'visits_this_month',
        'visits_diff_1m',
        'group_classes_attended',
        'support_contacts',
        'satisfaction_survey',
        'service_incident'
    ]
    
    # Conversión de variables categóricas
    X = pd.get_dummies(df_model[features], drop_first=True)
    # Variable dependiente
    y = df_model['target_churn']
    
    # División estratificada para mantener el % de bajas en entrenamiento y test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Cálculo de ratio de desequilibrio para scale_pos_weight
    ratio = (y_train == 0).sum() / (y_train == 1).sum()
    
    # Modelo XGBoost
    model = XGBClassifier(
        n_estimators=200,
        max_depth=4, 
        learning_rate=0.05,
        scale_pos_weight=ratio,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    
    # Entrenamiento
    model.fit(X_train, y_train)
    
    # Predicción
    y_probs = model.predict_proba(X_test)[:, 1]
    # Ajuste de umbral para mayor agresividad en la predicción
    y_pred = (y_probs >= 0.3).astype(int)
    
    # Métricas de rendimiento
    roc_auc = roc_auc_score(y_test, y_probs).round(2)
    recall = recall_score(y_test, y_pred).round(2)
    
    # Importancia de variables
    importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

    return df_model, features, model, importances

# 1. ENTRENAMIENTO DE MODELO DE ML
df_model, features, model, importances = train_model()

# 2. ENTRADA DE DATOS

# Últimos registros de cada miembros
df_last_status = df.drop_duplicates(subset='member_id', keep='last')

# Formulario con botón
with st.form(key='form_ml', border=False):

    # Entradas de modelo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write('###### 👤 Perfil')
        age = st.slider('Edad', int(df_last_status['age'].min()), int(df_last_status['age'].max()), int(df_last_status['age'].mean()))
        tenure = st.slider('Antigüedad (meses)', 0, df_last_status['tenure_months'].max(), 12)
        price_paid = st.number_input('Precio pagado (€)', value=df_last_status[df_last_status['plan'] == 'basic']['price_paid'].max())
    
    with col2:
        st.write('###### 🏋️ Actividad')
        visits_actual = st.number_input('Visitas este mes', 0, 31, 7)
        visits_prev = st.number_input('Visitas mes anterior', 0, 31, 10)
        group_classes = st.number_input('Clases colectivas', 0, 30, int(df_last_status['group_classes_attended'].mean()))

    with col3:
        st.write('###### 🛠️ Servicio')
        satisfaction = st.slider('Satisfacción (1-10)', 1, 10, int(df_last_status['satisfaction_survey'].mean()))
        support_contacts = st.number_input('Contactos soporte', 0, df_last_status['support_contacts'].max(), 0)
        incidents = st.selectbox('Incidente detectado', ['Ninguno', 'app_outage', 'heating_failure', 'pool_maintenance'])
    
    # Botón para predecir
    btn_ml = st.form_submit_button('Predecir')

# Variable de probabilidad inicial
prob = None

# Predecir probabilidad de cancelación a partir de entradas
if btn_ml:

    # Cálculo de entradas derivadas
    price_diff = price_paid - df_last_status['competitor_lowcost_price'].min()
    visits_diff_1m = visits_actual - visits_prev
    
    # Inputs de modelo
    inputs = {'age': age,
              'price_diff': price_diff,
              'tenure_months': tenure,
              'visits_this_month': visits_actual,
              'visits_diff_1m': visits_diff_1m,
              'group_classes_attended': group_classes,
              'support_contacts': support_contacts,
              'satisfaction_survey': satisfaction
             }

    # Conversión de inputs a DataFrame para procesarlo
    df_inputs = pd.DataFrame([inputs])

    # One-Hot Encoding manual para los incidentes
    df_inputs['service_incident_app_outage'] = 1 if incidents == 'app_outage' else 0
    df_inputs['service_incident_heating_failure'] = 1 if incidents == 'heating_failure' else 0
    df_inputs['service_incident_pool_maintenance'] = 1 if incidents == 'pool_maintenance' else 0

    # Alineación de orden y cantidad de variables al modelo
    model_columns = model.get_booster().feature_names
    df_inputs = df_inputs.reindex(columns=model_columns)

    # 3. PROCESAMIENTO DE PREDICCIÓN
    prob = model.predict_proba(df_inputs)[0, 1]

    # Importancia de variables
    feature_importance = importances.head(5).to_dict()
    feature_importance = '\n'.join([f'- **{k}**: {v:.1%}' for k, v in feature_importance.items()])

    # 4. RESULTADO DE PREDICCIÓN
    
    # Mostrar resultados según el nivel de riesgo
    if prob >= 0.33:
        st.error(f'###### Riesgo de abandono: {prob:.1%}', icon='⚠️')
    else:
        st.success(f'###### Riesgo de abandono: {prob:.1%}', icon='✅')

# ================================================================================
# 4.3.2 - GENERACIÓN DE INTERPRETACIONES DE PREDICCION
# ================================================================================

# Encabezado
st.markdown('##### Explicador de predicción')

# 5. INICIALIZACIÓN DE LLM

# API Key
GEMINI_API_KEY = st.secrets['GEMINI_API_KEY']
# Selección de modelo
GEMINI_MODEL = 'gemini-2.5-flash'

# Client Gemini
gemini = genai.Client(api_key=GEMINI_API_KEY)

# Interpretar predicción de cancelación
with st.expander('Explicatividad de modelo', expanded=False):

    if prob is not None:

        # 6. DEFINICIÓN DE PROMPT
        prompt_ml = ('Actúa como un Senior Growth Analyst experto en retención y abandono en el sector fitness.\n\n'
    
                     '## OBJETIVO:\n'
                     'Traducir la predicción técnica en un diagnóstico estratégico que identifique la causalidad del riesgo y proporcione claridad operativa.\n\n'
                     
                     '## PREDICCIÓN DEL MODELO:\n'
                     f'### PROBABILIDAD DE ABANDONO:\n{prob:.1%}\n\n'
                     f'### PERFIL DE MIEMBRO:\n{inputs}\n\n'
                     f'### INCIDENTES RECIENTES:\n{incidents}\n\n'
                     f'### IMPORTANCIA DE VARIABLES:\n{feature_importance}\n\n'
    
                     '## INSTRUCCIONES OBLIGATORIAS:\n'
                     '1. Basa tu análisis exclusivamente en las variables proporcionadas en la predicción.\n'
                     '2. No sólo listes los factores, explica cómo el factor X está impulsando la probabilidad de abandono en este miembro.\n'
                     "3. Si una variable tiene un peso bajo en 'Feature Importance', no le des protagonismo aunque parezca importante intuitivamente.\n"
                     '4. El tono debe ser profesional, ejecutivo y orientado a la toma de decisiones.\n\n'
                     
                     '## FORMATO DE RESPUESTA:\n'
                     '- Empieza directamente con el contenido, sin introducciones.\n'
                     '- Usa exclusivamente Markdown enriquecido (negritas, listas).\n'
                     '- Respeta la siguiente estructura de tres bloques:\n\n'
    
                     '🎯 **DIAGNÓSTICO DE PREDICCIÓN**: Resume de manera por qué es o no es probable que el miembro cancele su suscripción.\n'
                     '⚖️ **FACTORES QUE INFLUYEN**: Analiza las 5 variables con mayor peso en la predicción y cómo afectan a este miembro en particular.\n'
                     '🔍 **PATRONES DE ABANDONO**: Identifica patrones de comportamiento o señales de alerta temprana que expliquen la trayectoria del usuario.'
                    )

        # 7. LLAMADA Y PROCESAMIENTO DEL LLM
        with st.spinner('El LLM está interpretando la predicción...'):
    
            # Llamada al LLM con Gemini
            response_ml = gemini.models.generate_content(model=GEMINI_MODEL, contents=prompt_ml)
            response_ml = response_ml.text

        # 8. RESULTADO DEL LLM
        st.markdown(response_ml)
            
    else:
        st.write('👉 Realiza la predicción para diagnosticar los resultados.')
