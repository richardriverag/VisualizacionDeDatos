import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Historia de Reservas Hoteleras", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    return pd.read_csv("PEC3/hotel_bookings_clean.csv")

df_original = load_data()

# ==========================================
# ⚙️ CONFIGURACIÓN DE LA BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/285/285025.png", width=100) 
st.sidebar.title("Menú de Control")
st.sidebar.markdown("---")

# 1. Filtro Global: Tipo de Hotel
st.sidebar.subheader("Filtros de Datos")
opcion_hotel = st.sidebar.selectbox(
    "🏨 Elige el Tipo de Hotel:",
    ["Todos", "Resort Hotel", "City Hotel"]
)

# Lógica del filtro global:
if opcion_hotel == "Todos":
    df_filtrado = df_original.copy()
else:
    df_filtrado = df_original[df_original['hotel'] == opcion_hotel]

st.sidebar.markdown("---")

# 2. Navegación de la Historia
st.sidebar.subheader("📖 Capítulos")
capitulo = st.sidebar.radio(
    "Navega por la historia:",
    ["Introducción", "I: El Huésped", "II: Cancelaciones", "III: Rentabilidad"]
)

# Un pequeño resumen de datos en la sidebar
st.sidebar.markdown("---")
st.sidebar.info(f"**Datos actuales:**\n{len(df_filtrado):,} reservas analizadas.")

# ==========================================
# 🎨 LIENZO PRINCIPAL 
# ==========================================

# Título principal dinámico
st.title(":blue[_UOC - Visualización de Datos - Richard Rivera_]",text_alignment="center")
st.title("Explorando el comportamiento de los huéspedes y las oportunidades de negocio")

# Lógica para mostrar contenido según la opción seleccionada en el menú
if capitulo == "Introducción":
    st.markdown("### Bienvenido al análisis interactivo.")
    st.write("Utiliza el menú de la izquierda para navegar por los diferentes actos de nuestra historia y filtrar por tipo de propiedad.")
    
    st.header("El Escenario Actual")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Reservas", f"{len(df_filtrado):,}")
    tasa_cancelacion = (df_filtrado['is_canceled'].mean() * 100)
    col2.metric("Tasa de Cancelación Global", f"{tasa_cancelacion:.1f}%")
    col3.metric("Tarifa Media Diaria (ADR)", f"${df_filtrado['adr'].mean():.2f}")


elif capitulo == "I: El Huésped":
    st.header("🌎 ¿De dónde vienen y cómo nos encuentran?")
    st.markdown("Antes de analizar los problemas, veamos de dónde provienen nuestros clientes reales (aquellos que no cancelaron).")
    st.divider()
    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 1. Preparación de los datos
        # Filtramos solo las reservas que NO fueron canceladas
        df_reales = df_filtrado[df_filtrado['is_canceled'] == 0]

        # Contamos cuántas reservas hay por cada país
        # reset_index() convierte el resultado en un DataFrame tabular perfecto para Plotly
        mapa_data = df_reales['country'].value_counts().reset_index()
        mapa_data.columns = ['country', 'total_reservas'] # Renombramos las columnas para mayor claridad

        # 2. Creación del Mapa con Plotly Express
        fig_mapa = px.choropleth(
            mapa_data,
            locations="country",               # Columna con los códigos de país (ISO-3)
            color="total_reservas",            # Variable que determinará la intensidad del color
            hover_name="country",              # Lo que se muestra al pasar el ratón
            color_continuous_scale="Sunset",  # Escala de colores (puedes usar 'Blues', 'Teal', 'Sunset', etc.)
            title="Volumen de Reservas Efectivas por País de Origen",
            labels={'total_reservas': 'Número de Reservas'} # Limpia la etiqueta de la leyenda
        )

        # Opcional: Ajustar el diseño del mapa para que se vea más limpio
        fig_mapa.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
            margin={"r":0,"t":40,"l":0,"b":0} # Reduce los márgenes en blanco
        )

        # 3. Mostrar en Streamlit
        st.plotly_chart(fig_mapa, use_container_width=True)
    with col2:
        # Añadimos un pequeño insight o conclusión debajo del gráfico
        st.info("💡 **Insight:** Al pasar el cursor sobre el mapa, notarás si existe una fuerte dependencia del mercado nacional (ej. Portugal o España) frente al mercado internacional.")

    # ********************Gráfico 2:********************
    st.header("🚪 ¿Por qué puerta entran nuestros clientes?")
    st.markdown("""
    Ya sabemos de dónde vienen, pero... ¿cómo nos encuentran? 
    Analicemos los canales de adquisición (segmentos de mercado) y empecemos a descubrir un patrón interesante: **no todos los canales se comportan igual a la hora de cancelar.**
    """)

    # 1. Preparación de los datos
    # Para que la leyenda del gráfico sea clara, creamos una columna temporal con etiquetas de texto
    df_filtrado['Estado_Reserva'] = df_filtrado['is_canceled'].map({0: 'Efectiva', 1: 'Cancelada'})

    # Agrupamos por segmento de mercado y estado de reserva, y contamos el número de casos
    canal_data = df_filtrado.groupby(['market_segment', 'Estado_Reserva']).size().reset_index(name='Total_Reservas')

    # 2. Creación del Gráfico con Plotly Express
    fig_canal = px.bar(
        canal_data,
        x="Total_Reservas",
        y="market_segment",
        color="Estado_Reserva",
        orientation="h", # Barras horizontales para facilitar la lectura de los nombres
        title="Volumen de Reservas y Cancelaciones por Segmento de Mercado",
        labels={
            "market_segment": "Segmento de Mercado", 
            "Total_Reservas": "Número Total de Reservas"
        },
        # Forzamos los colores para mantener la narrativa: Rojo (peligro/cancelado) y Azul (bien/efectivo)
        color_discrete_map={"Efectiva": "#2E86C1", "Cancelada": "#E74C3C"} 
    )

    # 3. Ajuste del diseño
    # Ordenamos las barras para que el segmento con MÁS reservas en total aparezca arriba.
    # 'total ascending' en el eje Y (que es horizontal) pone el mayor valor en la parte superior.
    fig_canal.update_layout(
        yaxis={'categoryorder':'total ascending'},
        legend_title_text='Estado de la Reserva'
    )
    st.divider()
    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 4. Mostrar en Streamlit
        st.plotly_chart(fig_canal, use_container_width=True)
    with col2:
        # Añadimos la conclusión narrativa
        st.warning("🔍 **El Gran Descubrimiento:** Fíjate en la barra de 'Online TA' (Agencias de Viaje Online como Booking o Expedia). Es el canal que más volumen nos trae, ¡pero también el responsable de la inmensa mayoría de nuestras cancelaciones! Por el contrario, los segmentos 'Direct' (Reserva directa con el hotel) o 'Corporate' (Empresas) son mucho más seguros.")
elif capitulo == "II: Cancelaciones":
    st.header("⚠️ II: El Problema de las Cancelaciones")
    st.markdown("""
    Ya hemos identificado el "dónde" y el "cómo", ahora busquemos el **"por qué"**. 
    El tiempo es una variable crítica en la hostelería. Veamos cómo el tiempo de antelación con el que el cliente hace la reserva (`lead_time`) afecta a la probabilidad de que acabe cancelando.
    """)

    # 1. Preparación de los datos: Agrupación (Binning)
    # En lugar de ver días sueltos, creamos rangos de tiempo lógicos
    df_tiempo = df_filtrado.copy() # Hacemos una copia para no afectar a otros gráficos
    df_tiempo['Estado_Reserva'] = df_tiempo['is_canceled'].map({0: 'Efectiva', 1: 'Cancelada'})

    # Definimos los límites (días) y las etiquetas para los rangos
    cortes = [-1, 7, 28, 90, 180, 365, 1000]
    etiquetas = ['Última hora (0-7 días)', '1-4 semanas', '1-3 meses', '3-6 meses', '6-12 meses', 'Más de 1 año']

    # pd.cut asigna cada fila a uno de los rangos basándose en 'lead_time'
    df_tiempo['Rango_Antelacion'] = pd.cut(df_tiempo['lead_time'], bins=cortes, labels=etiquetas)

    # 2. Creación del Gráfico
    # Usamos un histograma de Plotly que cuente cuántas reservas caen en cada rango
    fig_tiempo = px.histogram(
        df_tiempo,
        x="Rango_Antelacion",
        color="Estado_Reserva",
        title="Evolución de las Cancelaciones según la Antelación de Compra",
        labels={
            "Rango_Antelacion": "Momento de la Reserva (Antelación)",
            "count": "Número Total de Reservas" # Eje Y por defecto en un histograma
        },
        color_discrete_map={"Efectiva": "#2E86C1", "Cancelada": "#E74C3C"},
        barmode="group", # 'group' pone las barras una al lado de la otra para comparar volúmenes
        text_auto=True   # ¡Truco! Esto añade los números exactos encima de las barras
    )

    # Ajustes de diseño para mejorar la legibilidad
    fig_tiempo.update_layout(
        xaxis_title=None, # Quitamos el título redundante del eje X
        yaxis_title="Volumen de Reservas"
    )
    # Formatear los números encima de las barras para que usen formato de miles (ej. 15k en vez de 15000)
    fig_tiempo.update_traces(texttemplate='%{y:.2s}', textposition='outside')
    st.divider()
    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 3. Mostrar en Streamlit
        st.plotly_chart(fig_tiempo, use_container_width=True)

    with col2:
        # La conclusión / El insight
        st.error("📈 **La Tensión de la Historia:** Observa el patrón escalofriante. En las reservas de 'Última hora', las cancelaciones son mínimas (la barra azul domina por completo). Sin embargo, a medida que nos desplazamos hacia la derecha (reservas hechas con meses de antelación), la barra roja crece agresivamente, ¡llegando a superar a las reservas efectivas en el rango de más de 1 año!")

    # ********************Gráfico 4:********************
    
    st.subheader("🛡️ El Antídoto: El compromiso del huésped")
    st.markdown("""
    Si el tiempo juega en nuestra contra, ¿hay algo que nos proteja? 
    Veamos qué ocurre con aquellos huéspedes que hacen **peticiones especiales** (ej. cama extra, piso alto, llegada anticipada). ¿Están más comprometidos con su viaje?
    """)

    # 1. Preparación de los datos
    # Usaremos el mismo df_tiempo del gráfico anterior porque ya tiene la columna 'Estado_Reserva'
    # Vamos a contar el volumen de reservas según la cantidad de peticiones especiales

    # 2. Creación del Gráfico
    # Usamos nuevamente un histograma agrupado
    fig_req = px.histogram(
        df_tiempo,
        x="total_of_special_requests",
        color="Estado_Reserva",
        title="Impacto del Nivel de Interacción en las Cancelaciones",
        labels={
            "total_of_special_requests": "Número de Peticiones Especiales"
        },
        barmode="group",
        text_auto=True,
        color_discrete_map={"Efectiva": "#2E86C1", "Cancelada": "#E74C3C"}
    )

    # Ajustes de diseño cruciales
    fig_req.update_layout(
    xaxis=dict(
        type='category', 
        categoryorder='category ascending' # ¡Esta es la magia que fuerza el orden 0, 1, 2, 3!
    ),
    yaxis_title="Volumen de Reservas"
    )
    fig_req.update_traces(texttemplate='%{y:.2s}', textposition='outside')

    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 3. Mostrar en Streamlit
        st.plotly_chart(fig_req, use_container_width=True)
    with col2:
        # La conclusión narrativa
        st.success("💡 **El Giro de la Historia:** ¡Mira el brutal contraste! Los clientes que hacen **0 peticiones** tienen un volumen de cancelación casi igual al de reservas efectivas. Sin embargo, en el momento en que un cliente hace tan solo **1 petición**, la probabilidad de cancelación se desploma (la barra azul aplasta a la roja). ¡Interactuar con el hotel asegura la reserva!")    


elif capitulo == "III: Rentabilidad":
     # ********************Gráfico 5:********************

    st.header("💰 III: Rentabilidad y Temporadas")
    st.markdown("""
    Ya sabemos cómo proteger nuestras reservas fomentando la interacción. Ahora veamos **cuándo** ganamos más dinero.
    Analizaremos la evolución de nuestra Tarifa Media Diaria (ADR) a lo largo del año, separando nuestros dos tipos de propiedades: el Hotel de Ciudad y el Resort.
    """)

    # 1. Preparación de los datos
    # Filtramos solo las reservas efectivas (las canceladas no generan ADR real)
    df_ingresos = df_filtrado[df_filtrado['is_canceled'] == 0].copy()

    # Truco vital: Ordenar los meses cronológicamente y no alfabéticamente
    meses_orden = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']

    # Convertimos la columna a un tipo "Categoría" con un orden específico
    df_ingresos['arrival_date_month'] = pd.Categorical(
        df_ingresos['arrival_date_month'], 
        categories=meses_orden, 
        ordered=True
    )

    # Agrupamos por mes y por tipo de hotel, calculando la media del ADR
    adr_mensual = df_ingresos.groupby(['arrival_date_month', 'hotel'])['adr'].mean().reset_index()

    # 2. Creación del Gráfico de Líneas
    fig_adr = px.line(
        adr_mensual,
        x="arrival_date_month",
        y="adr",
        color="hotel",
        title="Evolución de la Tarifa Media Diaria (ADR) por Mes",
        labels={
            "arrival_date_month": "Mes de Llegada",
            "adr": "Tarifa Media Diaria ($)",
            "hotel": "Tipo de Hotel"
        },
        markers=True, # Añade un puntito en cada mes para mayor claridad
        color_discrete_map={"City Hotel": "#8E44AD", "Resort Hotel": "#F39C12"} # Morado y Naranja para contrastar con los gráficos anteriores
    )

    fig_adr.update_layout(hovermode="x unified") # Muestra la info de ambas líneas al pasar el ratón

    st.divider()
    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 3. Mostrar en Streamlit
        st.plotly_chart(fig_adr, use_container_width=True)

    with col2:
        # La conclusión narrativa
        st.info("📊 **Insight Estratégico:** Observa la gran diferencia de estacionalidad. El **Resort** tiene un pico brutal de precios en verano (agosto), pero cae drásticamente en invierno. El **Hotel de Ciudad**, en cambio, es mucho más estable durante todo el año, con ligeras subidas en primavera (mayo) y otoño (septiembre). Esto nos indica que las estrategias de marketing deben ser completamente distintas para cada propiedad.")

    # ********************Gráfico 6:********************
    
    st.markdown("---")
    st.subheader("💳 El Giro Final: Las Políticas de Depósito")
    st.markdown("""
    Para cerrar nuestra historia, analicemos la intuición financiera básica: **"Si le cobro al cliente por adelantado y no le devuelvo el dinero, no cancelará, ¿verdad?"**.
    Veamos si nuestra política de depósitos (`deposit_type`) realmente funciona como un escudo contra las cancelaciones.
    """)

    # 1. Preparación de los datos
    df_deposito = df_filtrado.copy()
    df_deposito['Estado_Reserva'] = df_deposito['is_canceled'].map({0: 'Efectiva', 1: 'Cancelada'})

    # 2. Creación del Gráfico
    # Usamos un histograma pero con un truco: barnorm="percent"
    fig_deposito = px.histogram(
        df_deposito,
        x="deposit_type",
        color="Estado_Reserva",
        title="Proporción de Cancelaciones según Política de Depósito",
        labels={
            "deposit_type": "Política de Depósito",
            "percent": "Porcentaje (%)"
        },
        barnorm="percent", # MAGIA: Esto hace que todas las barras midan 100% y muestren la proporción interna
        text_auto='.1f',   # Muestra el número con 1 decimal
        color_discrete_map={"Efectiva": "#2E86C1", "Cancelada": "#E74C3C"}
    )

    # 3. Ajustes de diseño
    fig_deposito.update_layout(
        yaxis_title="Proporción del Total (%)",
        xaxis_title=None
    )
    # Formateamos el texto interior para que lleve el símbolo de porcentaje
    fig_deposito.update_traces(texttemplate='%{y:.1f}%')
    st.divider()
    col1, col2 = st.columns(2, vertical_alignment="center", gap = "medium")
    with col1:
        # 4. Mostrar en Streamlit
        st.plotly_chart(fig_deposito, use_container_width=True)

    with col2:
        # La conclusión / El Twist
        st.error("🤯 **El Giro Inesperado (Plot Twist):** ¡Mira la columna de 'Non Refund' (No Reembolsable)! Casi la totalidad de estas reservas acaban canceladas. ¿Cómo es posible? En el sector hotelero, las tarifas no reembolsables a veces son bloqueadas masivamente por agencias mayoristas que, si no logran vender los paquetes a tiempo, cancelan los bloques enteros a pesar de las penalizaciones. Irónicamente, ¡las reservas sin depósito ('No Deposit') tienen una tasa de éxito muchísimo mayor!")



