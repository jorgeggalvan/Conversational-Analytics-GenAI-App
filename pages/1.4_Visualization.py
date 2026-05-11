# Importación de librerías
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

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
# Extracción de año de registro
df['year'] = pd.to_datetime(df['month'], format='%Y-%m').dt.year

# =====================================================================================
# 1.4 - VISUALIZACIÓN DE DATOS
# =====================================================================================

# Subtítulo
st.subheader('📊 Visualización descriptiva')

# 1. SERIE TEMPORAL DE MIEMBROS ACTIVOS POR MES

# Creación de dos columnas
fig1, fig2 = st.columns(2)

# Encabezado
fig1.markdown('##### Evolución histórica de membresía')

# Excluir cancelaciones
df_active = df[df['status'] != 'churned']

# Miembros activos por mes
monthly_members = df_active.groupby('month').agg({'member_id':'nunique', 'competitor_lowcost_price':'mean'}).reset_index()

# Gráfico de líneas
fig_line1 = px.line(monthly_members, x='month', y='member_id',
                     # Etiquetas a los ejes x e y
                     labels = {'month':'Mes', 'member_id':'Miembros activos'}) 

# Mostrar gráfico
fig1.plotly_chart(fig_line1, width='stretch')


# 2. SERIE TEMPORAL DE PRECIO MEDIO DE PLAN BÁSICO Y COMPETENCIA POR MES

# Encabezado
fig2.markdown('##### Comparativa mensual de precios: plan básico vs. competencia')

# Filtrar registros de plan básico
df_active = df[df['plan'] == 'basic']

# Precio medio de plan básico y competencia por mes
monthly_price = df_active.groupby('month').agg({'price_paid':'mean', 'competitor_lowcost_price':'mean'}).reset_index()   

# Gráfico de líneas
fig_line2 = px.line(monthly_price, x='month', y=['price_paid', 'competitor_lowcost_price'], 
                     
                     # Etiquetas a los ejes x e y, y leyenda
                     labels = {
                         'month':'Mes', 
                         'value':'Precio promedio (€)', 
                         'variable':'Tipo de precio', 
                         'price_paid':'Plan básico (FitLife)', 'competitor_lowcost_price':'Competencia'}, 
                     
                     # Colores de líneas
                     color_discrete_map = {
                         'price_paid':'royalblue', 
                         'competitor_lowcost_price':'orange'})

# Renombrado de valores de leyenda
price_names = {'price_paid':'Plan básico (FitLife)', 'competitor_lowcost_price':'Competencia'}
fig_line2.for_each_trace(lambda t: t.update(name = price_names.get(t.name, t.name)))
# Limitación de eje y
fig_line2.update_yaxes(rangemode='tozero')

# Mostrar gráfico
fig2.plotly_chart(fig_line2, width='stretch')


# 3. GRÁFICO DE BARRAS CON LOS INGRESOS MEDIOS POR CENTRO

# Creación de tres columnas
fig3, fig4, fig5 = st.columns(3)

# Encabezado
fig3.markdown('##### Ranking de gimnasios FitLife')

# Ingresos por centro
revenue_per_centre = df.groupby('center').agg({'price_paid':'sum'}).reset_index() 

# Gráfico de barras
fig_bar = px.bar(revenue_per_centre, x='price_paid', y='center',
                 # Etiquetas a los ejes x e y
                 labels={'price_paid':'Ingresos obtenidos (€)', 'center':'Centro'},
                 # Orden de barras
                 category_orders={'center': revenue_per_centre.sort_values('price_paid', ascending=False)['center'].tolist()})

# Mostrar gráfico
fig3.plotly_chart(fig_bar, width='stretch')


# 4. GRÁFICO DE TARTA CON EL Nº DE MIEMBROS POR PLAN

# Encabezado
fig4.markdown('##### Distribución de planes de suscripción')

# Últimos registros por cada 'member_id'
df_current_plan = df[['month', 'member_id', 'plan', 'status']].sort_values(['member_id', 'month']).drop_duplicates(subset='member_id', keep='last')
# Filtrar por miembros activos
df_current_plan = df_current_plan[df_current_plan['status'] == 'active']

# Número de miembros por plan
plan_distribution = df_current_plan['plan'].value_counts().reset_index()

# Gráfico de tarta
fig_pie = px.pie(plan_distribution, names='plan', values='count')

# Mostrar gráfico
fig4.plotly_chart(fig_pie, width='stretch')


# 5. MAPA DE CALOR CON LAS VISITAS TOTALES POR AÑO Y MES 

# Encabezado
fig5.markdown('##### Actividad mensual de miembros')

# Visitas totales por año y mes
monthly_visits = df.groupby(['year', 'month_num']).agg({'visits_this_month':'sum'}).reset_index()

# Reestructuración de agregación a formato pivot
monthly_visits_pivoted = monthly_visits.pivot(index='month_num', columns='year', values='visits_this_month')
monthly_visits_pivoted = monthly_visits_pivoted.sort_index()

# Mapa de calor
fig_heatmap = px.imshow(monthly_visits_pivoted, x=monthly_visits_pivoted.columns, y=monthly_visits_pivoted.index,                          
                        labels={'x':'Año', 'y':'Mes', 'color':'Visitas'},
                        color_continuous_scale='OrRd',
                        text_auto=True,
                        aspect='auto'
                       )

# Mostrar todos los meses en las etiquetas
month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
fig_heatmap.update_yaxes(tickmode='array', tickvals=monthly_visits_pivoted.index, ticktext=[month_names[i-1] for i in monthly_visits_pivoted.index])

# Mostrar gráfico
fig5.plotly_chart(fig_heatmap, width='stretch')
