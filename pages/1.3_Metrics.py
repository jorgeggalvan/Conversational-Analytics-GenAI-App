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

# Ruta del dataset
ROOT_PATH = Path(__file__).parent.parent
DATA_PATH = ROOT_PATH / 'data' / 'fitlife_members.csv'

# Lectura del dataset
df = pd.read_csv(DATA_PATH)

# Extracción de mes numérico de registro
df['month_num'] = pd.to_datetime(df['month'], format='%Y-%m').dt.month
# Extracción de trimestre de registro
df['quarter'] = pd.to_datetime(df['month'], format='%Y-%m').dt.quarter
# Extracción de año de registro
df['year'] = pd.to_datetime(df['month'], format='%Y-%m').dt.year

# =====================================================================================
# SECCIÓN DE FILTROS
# =====================================================================================

# Subtítulo
st.subheader('🎯 Indicadores de negocio')

# 1. CREACIÓN DE FILTROS

# Cálculo de último mes y año
month_last = df['month_num'].max()
year_last = df['year'].max()

with st.expander('Filtros de datos', expanded=False):
    # Creación de columnas para filtros principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtro de planes
        plans = st.multiselect('Planes de suscripción', options=sorted(df['plan'].unique()), default=df['plan'].unique())   
    with col2:
        # Filtro de centros
        centers_ordered = df.drop_duplicates(subset='member_id')['center'].value_counts().index.tolist()
        centers = st.multiselect('Centros', options=centers_ordered, placeholder='Elige uno o varios centros') 
    with col3:
        # Filtro de canales de adquisición
        channels_ordered = df.drop_duplicates(subset='member_id')['acquisition_channel'].value_counts().index.tolist()
        acq_channels = st.multiselect('Canales de adquisición', options=channels_ordered, placeholder='Elige uno o varios canales')
    
    # Creación de columnas para filtros temporales
    col4, col5 = st.columns([1, 2])
    
    with col4:
        # Filtro de Año
        years = st.multiselect('Años', options=sorted(df['year'].unique(), reverse=True), default=year_last)
    with col5:
        #Filtro de mes
        months = st.slider('Rango de meses', min_value=int(df['month_num'].min()), max_value=int(df['month_num'].max()), value=(month_last-2, month_last))


# 2. APLICACIÓN DE FILTROS

# Copia de DataFrame original
df_filtered = df.copy()

# Filtrar DataFrame por año
if years:
    df_filtered = df_filtered[df_filtered['year'].isin(years)]

# Filtrar DataFrame por rango de meses
df_filtered = df_filtered[(df_filtered['month_num'] >= months[0]) & (df_filtered['month_num'] <= months[1])]

# Filtrar DataFrame por centros
if centers:
    df_filtered = df_filtered[df_filtered['center'].isin(centers)]

# Filtrar DataFrame por planes
if plans:
    df_filtered = df_filtered[df_filtered['plan'].isin(plans)]

# Filtrar DataFrame por canales de adquisición
if acq_channels:
    df_filtered = df_filtered[df_filtered['acquisition_channel'].isin(acq_channels)]


# =====================================================================================
# 1.3 - INDICADORES DE NEGOCIO
# =====================================================================================

# 1. FILTRADO POR EL TRIMESTRE ACTUAL 

# Definición de último mes, trimestre y año seleccionado en los filtros
month_actual = months[1]
quarter_actual = ((month_actual - 1) // 3) + 1
year_actual = max(years)

# Cálculo del trimestre anterior
if quarter_actual == 1:
    quarter_prev = 4
    year_prev = year_actual - 1
else:
    quarter_prev = quarter_actual - 1
    year_prev = year_actual

# Filtrar por trimestre actual y trimestre anterior
df_actual = df[(df['year'] == year_actual) & (df['quarter'] == quarter_actual)]
df_prev = df[(df['year'] == year_prev) & (df['quarter'] == quarter_prev)]


# 2. CÁLCULO DE KPIS

# -------------------------------------------------------------------------------------
# Base de miembros
# -------------------------------------------------------------------------------------

# Miembros totales
members = df_actual['member_id'].nunique()
members_prev = df_prev['member_id'].nunique()

# Cancelaciones
churned_members = df_actual[df_actual['status'] == 'churned']['member_id'].nunique()
churned_members_prev = df_prev[df_prev['status'] == 'churned']['member_id'].nunique()
delta_churn = ((churned_members - churned_members_prev) / churned_members_prev)

# Tasa de cancelación (calculado sin distinguir miembros nuevos)
churn_rate = (churned_members / members)
churn_rate_prev = (churned_members_prev / members_prev)
delta_churn_rate = ((churn_rate - churn_rate_prev) / churn_rate_prev)

# Nuevos miembros
df_new_members = df_actual[df_actual['tenure_months'] == 1]
new_members = df_new_members['member_id'].nunique()

df_new_members_prev = df_prev[df_prev['tenure_months'] == 1]
new_members_prev = df_new_members_prev['member_id'].nunique()

delta_new = ((new_members - new_members_prev) / new_members_prev)

# Miembros activos
active_members = df_actual[df_actual['status'] == 'active']['member_id'].nunique()
active_members_prev = df_prev[df_prev['status'] == 'active']['member_id'].nunique()
delta_active = ((active_members - active_members_prev) / active_members_prev)

# -------------------------------------------------------------------------------------
# Resultados económicos
# -------------------------------------------------------------------------------------

# Ingresos
total_revenue = df_actual['price_paid'].sum()
total_revenue_prev = df_prev['price_paid'].sum()
delta_revenue = ((total_revenue - total_revenue_prev) / total_revenue_prev)

# ARPU
arpu = total_revenue / members
arpu_prev = total_revenue_prev / members_prev
delta_arpu = ((arpu - arpu_prev) / arpu_prev)

# CLV (vida media de miembro)
clv = df_actual['tenure_months'].mean()
clv_prev = df_prev['tenure_months'].mean()
delta_clv = ((clv - clv_prev) / clv_prev)

# LTV
ltv = arpu * clv
ltv_prev = arpu_prev * clv_prev
delta_ltv = ((ltv - ltv_prev) / ltv_prev)

# -------------------------------------------------------------------------------------
# Fidelidad y experiencia
# -------------------------------------------------------------------------------------

# NPS
df_survey_actual = df_actual[df_actual['satisfaction_survey'].notna()]
promoters = (df_survey_actual['satisfaction_survey'] >= 9).sum()
detractors = (df_survey_actual['satisfaction_survey'] <= 6).sum()
total_responses = len(df_survey_actual)

nps = ((promoters - detractors) / total_responses * 100)

df_survey_prev = df_prev[df_prev['satisfaction_survey'].notna()]
promoters_prev = (df_survey_prev['satisfaction_survey'] >= 9).sum()
detractors_prev = (df_survey_prev['satisfaction_survey'] <= 6).sum()
total_responses_prev = len(df_survey_prev)

nps_prev = ((promoters_prev - detractors_prev) / total_responses_prev * 100)

delta_nps = ((nps - nps_prev) / nps_prev)

# Valor de visita
visit_value = (total_revenue / df_actual['visits_this_month'].sum())
visit_value_prev = (total_revenue / df_prev['visits_this_month'].sum())
delta_visit_value = ((visit_value - visit_value_prev) / visit_value_prev)

# Visitas por miembro
visits_per_member = df_actual['visits_this_month'].sum() / df_actual['member_id'].nunique()
visits_per_member_prev = df_prev['visits_this_month'].sum() / df_prev['member_id'].nunique()
delta_visits = ((visits_per_member - visits_per_member_prev) / visits_per_member_prev)

# Incidencias reportadas por miembro
incidents_per_member = df_actual['incidents_reported'].sum() / df_actual['member_id'].nunique()
incidents_per_member_prev = df_prev['incidents_reported'].sum() / df_prev['member_id'].nunique()
delta_incidents = ((incidents_per_member - incidents_per_member_prev) / incidents_per_member_prev) 

# -------------------------------------------------------------------------------------
# Competencias y palancas
# -------------------------------------------------------------------------------------

# Captación por campañas
new_with = df_new_members[df_new_members['campaign_active'].notna()]['member_id'].nunique()
new_without = df_new_members[df_new_members['campaign_active'].isna()]['member_id'].nunique()
campaign_singups = (new_with / (new_with + new_without))

new_with_prev = df_new_members_prev[df_new_members_prev['campaign_active'].notna()]['member_id'].nunique()
new_without_prev = df_new_members_prev[df_new_members_prev['campaign_active'].isna()]['member_id'].nunique()
campaign_singups_prev = (new_with_prev / (new_with_prev + new_without_prev))

delta_campaign = ((campaign_singups - campaign_singups_prev) / campaign_singups_prev)

# Gap de precio con competencia
df_basic_price = df_actual[df_actual['plan'] == 'basic']
price_gap = (df_basic_price['price_paid'] - df_basic_price['competitor_lowcost_price']).mean()

df_basic_price_prev = df_prev[df_prev['plan'] == 'basic']
price_gap_prev = (df_basic_price_prev['price_paid'] - df_basic_price_prev['competitor_lowcost_price']).mean()

delta_gap = ((price_gap - price_gap_prev) / price_gap_prev)

# Sensibilidad al precio
avg_price = df_actual['price_paid'].mean()
avg_price_prev = df_prev['price_paid'].mean()
delta_price = ((avg_price - avg_price_prev) / avg_price_prev)
price_elasticity = delta_active / delta_price

# Miembros en riesgo
risk_members = (df_actual[df_actual['visits_this_month'] <= 5]['member_id'].nunique() / active_members)
risk_members_prev = (df_prev[df_prev['visits_this_month'] <= 5]['member_id'].nunique() / active_members_prev)
delta_risk_members = ((risk_members - risk_members_prev) / risk_members_prev)


# 3. MOSTRAR INDICADORES DE NEGOCIO

# Texto antes de las métricas
st.caption(f'**Datos trimestrales** (correspondientes al Q{quarter_actual} de {year_actual}).')

# Función para formatear millones y miles
def format_number(n):
    if n >= 1_000_000:
        return f'{n/1_000_000:.1f}M'
    elif n >= 1_000:
        return f'{n/1_000:.1f}K'
    else:
        return n if n == int(n) else round(n, 1)

# Mostrar métricas principales en columnas
met1, met2, met3, met4 = st.columns(4)

met1.metric('👥 Tasa de Cancelación', f'{churn_rate:.1%}', f'{delta_churn_rate:.1%}', delta_color='inverse')
met2.metric('📈 Ingresos', f'{format_number(total_revenue)} €', f'{delta_revenue:.1%}')
met3.metric('⭐ CLV', f'{format_number(clv):.0f} meses', f'{delta_clv:.1%}')
met4.metric('⚡ Captación por Campañas', f'{format_number(campaign_singups):.0%}', f'{delta_campaign:.1%}')

# Mostrar métricas secundarias en columnas

# Creación de pestañas por categorías de KPIs
tab1, tab2, tab3, tab4 = st.tabs(['👥 Miembros', '📈 Finanzas', '⭐ Fidelidad y experiencia', '⚡ Estrategia'])

with tab1:
    met5, met6, met7, met8 = st.columns(4)
    met5.metric('👥 Cancelaciones', format_number(churned_members), f'{delta_churn:.1%}', delta_color='inverse')
    met6.metric('👥 Nuevos Miembros', format_number(new_members), f'{delta_new:.1%}')
    met7.metric('👥 Total de Miembros Activos', format_number(active_members), f'{delta_active:.1%}')
    
with tab2:
    met9, met10, met11, met12 = st.columns(4)
    met9.metric('📈 ARPU (ingreso promedio por miembro)', f'{format_number(arpu)} €', f'{delta_arpu:.1%}')
    met10.metric('📈 LTV (valor de vida de miembro)', f'{format_number(ltv)} €', f'{delta_ltv:.1%}')

with tab3:
    met13, met14, met15, met16 = st.columns(4)
    met13.metric('⭐ NPS', format_number(nps), f'{delta_nps:.1%}')
    met14.metric('⭐ Valor de Visita (ratio de visitas por ingresos)', f'{format_number(visit_value)} €', f'{delta_visit_value:.1%}')
    met15.metric('⭐ Visitas por Miembro', f'{format_number(visits_per_member):.0f} visitas', f'{delta_visits:.1%}')
    met16.metric('⭐ Incidencias Reportadas por Miembro', f'{format_number(incidents_per_member)} incidencias', f'{delta_incidents:.1%}', delta_color='inverse')

with tab4:
    met17, met18, met19, met20 = st.columns(4)
    met17.metric('⚡ Gap de Precio con Competencia', f'{format_number(price_gap)} €', f'{delta_gap:.1%}', delta_color='off')
    met18.metric('⚡ Sensibilidad al Precio', f'{price_elasticity:.2f}')
    met19.metric('⚡ Miembros en Riesgo', f'{risk_members:.0%}', f'{delta_risk_members:.1%}', delta_color='inverse')
