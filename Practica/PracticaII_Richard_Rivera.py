import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# -----------------------------------------------------------------------------
# Configuración inicial de la página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OS Market Share Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Carga de Datos (Caché)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('Practica/os_market_share_clean.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar)
# -----------------------------------------------------------------------------
st.sidebar.header("Filtros Globales")

regiones_disponibles = list(df['Region'].unique())
default_region = ["World Wide"] if "World Wide" in regiones_disponibles else [regiones_disponibles[0]]
selected_regions = st.sidebar.multiselect("Selecciona Región(es):", regiones_disponibles, default=default_region)

min_date = df['Date'].min().to_pydatetime()
max_date = df['Date'].max().to_pydatetime()
start_date, end_date = st.sidebar.slider(
    "Selecciona Rango de Fechas:",
    min_value=min_date, max_value=max_date,
    value=(min_date, max_date), format="YYYY-MM"
)

categorias_disp = list(df['Device_Category'].unique())
selected_categories = st.sidebar.multiselect("Categoría de Dispositivo:", categorias_disp, default=categorias_disp)

# Aplicar filtros
mask = (
    (df['Region'].isin(selected_regions)) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date)) &
    (df['Device_Category'].isin(selected_categories))
)
df_filtered = df[mask]

# -----------------------------------------------------------------------------
# Cuerpo Principal del Dashboard
# -----------------------------------------------------------------------------
st.title(":blue[_UOC - Visualización de Datos - Richard Rivera_]",text_alignment="center")
st.title("📊 Evolución Global y Regional de la Cuota de Mercado de Sistemas Operativos (2009-2026)")
st.markdown("""
Este dashboard interactivo analiza la evolución de la cuota de mercado de los diferentes sistemas operativos a nivel mundial y regional. 
Permite explorar la transición histórica hacia los dispositivos móviles y evaluar el nivel de concentración tecnológica.
""")
st.markdown("Además explora la evolución tecnológica, la concentración de mercado y su relación con los hitos de ciberseguridad a nivel mundial y regional.")

# Creación de las 8 pestañas fusionadas
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "1. Evolución General", 
    "2. La Inflexión Móvil", 
    "3. Concentración y Legacy",
    "4. Hitos Ciberseguridad", 
    "5. Animación Global", 
    "6. Cementerio de OS", 
    "7. Zoom Sudamérica", 
    "8. Predicción 2030"
])

# ==========================================
# PESTAÑAS ORIGINALES (1 a 3)
# ==========================================

# --- PESTAÑA 1: Evolución General ---
with tab1:
    st.subheader("Evolución de la Cuota de Mercado por Sistema Operativo")
    if not df_filtered.empty:
        fig1 = px.area(
            df_filtered, x='Date', y='Market_Share', color='OS_Name',
            facet_col='Region', facet_col_wrap=2,
            title="Cuota de Mercado Histórica (Áreas Apiladas)"
        )
        fig1.update_layout(height=600)
        st.plotly_chart(fig1, width='stretch')
    else:
        st.warning("No hay datos para los filtros seleccionados.")

# --- PESTAÑA 2: La Inflexión Móvil ---
with tab2:
    st.subheader("Desktop vs Mobile: El Cambio de Paradigma")
    st.markdown("¿En qué momento los sistemas operativos móviles superaron a los de escritorio?")
    df_category = df[df['Region'].isin(selected_regions)].groupby(['Date', 'Region', 'Device_Category'])['Market_Share'].sum().reset_index()
    df_cat_filtered = df_category[df_category['Device_Category'].isin(['Mobile', 'Desktop'])]
    
    if not df_cat_filtered.empty:
        fig2 = px.line(
            df_cat_filtered, x='Date', y='Market_Share', color='Device_Category',
            line_dash='Region', title="Comparativa de Adopción: Escritorio vs Móvil"
        )
        fig2.add_hline(y=50, line_dash="dot", annotation_text="Punto de Inflexión (50%)", annotation_position="bottom right")
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, width='stretch')

# --- PESTAÑA 3: Concentración y Legacy ---
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Sistemas Soportados vs Abandonados")
        df_legacy_gen = df_filtered.groupby(['Date', 'Is_Active'])['Market_Share'].sum().reset_index()
        df_legacy_gen['Estado'] = df_legacy_gen['Is_Active'].map({True: 'Soportado', False: 'Legacy (Abandonado)'})
        
        fig3_1 = px.area(
            df_legacy_gen, x='Date', y='Market_Share', color='Estado',
            color_discrete_map={'Soportado': '#2ca02c', 'Legacy (Abandonado)': '#d62728'},
            title="Proporción de Sistemas Legacy Globales"
        )
        st.plotly_chart(fig3_1, width='stretch')

    with col2:
        st.subheader("Índice de Concentración (HHI)")
        df_hhi = df[df['Region'].isin(selected_regions)][['Date', 'Region', 'Market_Concentration_Index']].drop_duplicates()
        fig3_2 = px.line(
            df_hhi, x='Date', y='Market_Concentration_Index', color='Region',
            title="Evolución del Monopolio de OS por Región"
        )
        st.plotly_chart(fig3_2, width='stretch')

# ==========================================
# PESTAÑAS NUEVAS (4 a 8)
# ==========================================

# --- PESTAÑA 4: Hitos Ciberseguridad ---
with tab4:
    st.subheader("Superficie de Ataque y Eventos Históricos")
    st.markdown("Observa cómo los picos de adopción o el fin de soporte coinciden con hitos clave en el mundo del malware.")
    if not df_filtered.empty:
        fig4 = px.line(
            df_filtered, x='Date', y='Market_Share', color='OS_Name',
            facet_col='Region', facet_col_wrap=2, title="Hitos de Seguridad Tecnológica"
        )
        hitos = {
            '2010-08-01': '1er Troyano Android',
            '2014-04-08': 'Fin Win XP',
            '2017-05-12': 'WannaCry',
            '2020-01-14': 'Fin Win 7'
        }
        for date_str, event in hitos.items():
            fig4.add_vline(
                x=pd.to_datetime(date_str).timestamp() * 1000, 
                line_width=1.5, line_dash="dash", line_color="red",
                annotation_text=event, annotation_position="top right"
            )
        fig4.update_layout(height=600)
        st.plotly_chart(fig4, width='stretch')

# --- PESTAÑA 5: Animación Global ---
with tab5:
    st.subheader("Carrera de Barras: El Cambio de Hegemonía")
    df_anim = df_filtered.copy()
    df_anim['Year'] = df_anim['Date'].dt.year
    df_anim_grouped = df_anim.groupby(['Year', 'Region', 'OS_Name'])['Market_Share'].mean().reset_index()
    top_os = ['Windows', 'Android', 'iOS', 'OS X', 'macOS', 'Linux']
    df_anim_grouped = df_anim_grouped[df_anim_grouped['OS_Name'].isin(top_os)]
    
    fig5 = px.bar(
        df_anim_grouped, x="OS_Name", y="Market_Share", color="OS_Name",
        animation_frame="Year", animation_group="OS_Name",
        facet_col="Region", facet_col_wrap=2,
        range_y=[0, 100], title="Evolución Anual (Presiona Play ▶️)"
    )
    st.plotly_chart(fig5, width='stretch')

# --- PESTAÑA 6: Cementerio de OS ---
with tab6:
    st.subheader("El Cementerio de los Sistemas Operativos")
    legacy_systems = ['SymbianOS', 'BlackBerry OS', 'Series 40', 'bada', 'Sony Ericsson', 'Nokia Unknown']
    df_legacy_spec = df_filtered[df_filtered['OS_Name'].isin(legacy_systems)]
    
    if not df_legacy_spec.empty:
        fig6 = px.area(
            df_legacy_spec, x='Date', y='Market_Share', color='OS_Name',
            title="Caída de los Gigantes (Foco en Plataformas Antiguas)"
        )
        st.plotly_chart(fig6, width='stretch')
    else:
        st.info("Ajusta los filtros de la barra lateral para incluir la categoría 'Mobile' y fechas anteriores a 2015.")

# --- PESTAÑA 7: Zoom Sudamérica ---
with tab7:
    st.subheader("Foco Regional: Sudamérica vs El Mundo")
    df_sa_ww = df[df['Region'].isin(['South America', 'World Wide'])]
    df_sa_ww = df_sa_ww[df_sa_ww['OS_Name'].isin(['Windows', 'Android'])]
    
    fig7 = px.line(
        df_sa_ww, x='Date', y='Market_Share', color='Region', line_dash='OS_Name',
        title="Retrasos Tecnológicos: Windows y Android (Sudamérica vs Mundo)",
        color_discrete_map={'South America': '#1f77b4', 'World Wide': '#7f7f7f'}
    )
    st.plotly_chart(fig7, width='stretch')

# --- PESTAÑA 8: Predicción 2030 ---
with tab8:
    st.subheader("Proyección a Futuro (Modelo Predictivo)")
    col_p1, col_p2 = st.columns(2)
    pred_region = col_p1.selectbox("Región para predicción:", df['Region'].unique(), index=0)
    pred_os = col_p2.selectbox("Sistema para predecir:", ['Android','Windows', 'iOS', 'macOS', 'Linux'], index=0)
    
    df_train = df[(df['Region'] == pred_region) & (df['OS_Name'] == pred_os)].copy()
    
    if not df_train.empty:
        df_train['Date_ordinal'] = df_train['Date'].map(pd.Timestamp.toordinal)
        X = df_train[['Date_ordinal']]
        y = df_train['Market_Share']
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_dates = pd.date_range(start=df_train['Date'].max(), end='2030-12-31', freq='ME')
        future_ordinal = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
        future_preds = np.clip(model.predict(future_ordinal), 0, 100)
        
        df_future = pd.DataFrame({'Date': future_dates, 'Market_Share': future_preds, 'Type': 'Predicción (Hasta 2030)'})
        df_train['Type'] = 'Datos Históricos'
        df_combined = pd.concat([df_train[['Date', 'Market_Share', 'Type']], df_future])
        
        fig8 = px.scatter(
            df_combined, x='Date', y='Market_Share', color='Type',
            title=f"Tendencia Proyectada para {pred_os} en {pred_region}",
            color_discrete_map={'Datos Históricos': 'blue', 'Predicción (Hasta 2030)': 'orange'}
        )
        st.plotly_chart(fig8, width='stretch')

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
footer_html = """
<div style="text-align: center; color: gray; font-size: small;">
    <p><b>Proyecto de Visualización de Datos</b> | Autor: <a href= "https://richardriverag.github.io">Richard Rivera</a></p>
    <p>Desarrollado con Streamlit y Plotly | Datos: <a href= "https://gs.statcounter.com">StatCounter</a></p>
    <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/deed.es" target="_blank">
        <img alt="Licencia Creative Commons" style="border-width:0; margin-bottom: 5px;" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" />
    </a>
    <br />
    Esta obra está bajo una <a rel="license" href="https://creativecommons.org/licenses/by-sa/4.0/deed.es" target="_blank" style="color: gray;">Licencia Creative Commons Atribución-CompartirIgual 4.0 Internacional</a>.
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)