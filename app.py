import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.integrate import odeint


# ===================================================================
#                    MODELO DE ESPACIO DE ESTADOS (Backend)
# ===================================================================

# ---------- PARÁMETROS FIJOS (Sistema SI) ----------
# Estos son los valores por defecto. En la interfaz se pueden modificar.
# Pero las funciones de simulación los usan como argumentos.
# No definimos constantes globales acá, las pasamos como parámetros.

# ---------- AEs (Ecuaciones Algebraicas/Constitutivas) ----------
def AEs(L, x, params):
    """
    Calcula las variables algebraicas (Y) a partir del estado X y parámetros.
    En Octave, esta función devolvía [A, F0, F].
    Aquí devolvemos un diccionario con las variables que necesitamos.
    """
    F0 = params['F0']
    Cv = params['Cv']
    rho = params['rho']
    g = params['g']
    A = params['A']

    # Caudal de salida (modelo gravitatorio)
    # Protección para L negativo o muy pequeño
    L_segura = max(L, 0.001)
    # Caudal de salida 
    F = Cv * x * np.sqrt(rho * g * L_segura)
    
    return {
        'A': A,
        'F0': F0,
        'F': F
    }

# ---------- ODEs (Ecuaciones Diferenciales) ----------
def ODEs(X, t, x, params):
    """
    Devuelve las derivadas de las variables de estado.
    """
    # Recuperar variables de estado
    L = X[0]
    
    # Calcular variables algebraicas
    Y = AEs(L, x, params)
    
    # Ecuación diferencial
    dL = (Y['F0'] - Y['F']) / Y['A']
    
    return [dL]

# ---------- Característica de la Válvula ----------
def f_apertura(x, tipo, R=50):
    """
    Calcula el flujo normalizado f(x) según el tipo de válvula.
    """
    x = max(0.0, min(1.0, x))
    
    if tipo == "Lineal":
        return x
    elif tipo == "Igual porcentaje":
        return R**(x-1)
    elif tipo == "Apertura rápida":
        return 1 - (1-x)**2
    else:
        return x

# ---------- Inicialización ----------
def inicializar(params_por_defecto):
    """
    Inicializa la simulación con los parámetros dados.
    Devuelve las condiciones iniciales y las leyendas.
    """
    # Condiciones iniciales
    L0 = params_por_defecto['L0']
    Xini = [L0]
    
    # Leyendas (para las gráficas)
    LX = ['L']   # Variables de estado
    LY = ['A', 'F0', 'F']  # Variables algebraicas
    
    return Xini, LX, LY

# ---------- Simulación ----------
def simulacion(tfin, dt, Xini, x, params):
    """
    Realiza la simulación dinámica.
    """
    # Vector de tiempo
    nts = int(np.ceil(tfin / dt)) + 1
    tpts = np.linspace(0, tfin, nts)
    
    # Resolver ODEs
    sol = odeint(ODEs, Xini, tpts, args=(x, params))
    X = sol[:, 0]  # Extraer L
    
    # Calcular variables dependientes (Y) en cada instante
    Y = {}
    Y['A'] = np.full_like(tpts, params['A'])
    Y['F0'] = np.full_like(tpts, params['F0'])
    F = np.zeros_like(tpts)
    for i, L in enumerate(X):
        # AEs en cada instante
        Y_local = AEs(L, x, params)
        F[i] = Y_local['F']
    Y['F'] = F
    
    return tpts, X, Y

# ---------- Análisis Estacionario (CORREGIDO) ----------
def nivel_estacionario(F0, Cv, x, rho, g, tipo, R=50):
    """
    Calcula el nivel estacionario para una apertura x dada.
    """
    if x <= 0 or Cv <= 0:
        return np.inf
    f = f_apertura(x, tipo, R)
    return (F0 / (Cv * f))**2 / (rho * g)

# ---------- Cálculo de Cv (CORREGIDO) ----------
def calcular_Cv(F0, x0, rho, g, L0, tipo, R=50):
    """
    Calcula Cv a partir del punto de operación inicial.
    """
    f0 = f_apertura(x0, tipo, R)
    if f0 <= 0 or L0 <= 0:
        return 0
    return F0 / (f0 * np.sqrt(rho * g * L0))

# ---------- Función de caudal de salida (para cálculos rápidos) ----------
def caudal_salida(L, x, params):
    """
    Calcula el caudal de salida para un nivel L y apertura x dados.
    """
    Y = AEs(L, x, params)
    return Y['F']


# ===================================================================
#                    INTERFAZ DE USUARIO (Frontend)
# ===================================================================

# ---------- Configuración de la página ----------
st.set_page_config(
    page_title="Simulador de Tanque Gravitatorio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- INYECCIÓN DE CSS PERSONALIZADO ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    footer {visibility: hidden;}
    /* #MainMenu visible para que el selector de temas funcione */
    
    .css-1d391kg, .css-1lcbmhc {
        background-color: #f5f6f7 !important;
        border-right: 1px solid #d0d0d5 !important;
        padding-top: 2rem !important;
    }
    
    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; }
    h3 { font-size: 1.1rem !important; }
    
    .stButton > button {
        background-color: #e8e8ea !important;
        color: #1b1b32 !important;
        border: 1px solid #d0d0d5 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.01em !important;
    }
    
    .stButton > button:hover {
        background-color: #1b1b32 !important;
        color: #ffffff !important;
        border-color: #1b1b32 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    }
    
    .stButton > button:active { transform: scale(0.98) !important; }
    
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1px solid #d0d0d5 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div:focus {
        border-color: #1b1b32 !important;
        box-shadow: 0 0 0 2px rgba(27, 27, 50, 0.1) !important;
    }
    
    .streamlit-expanderHeader {
        font-weight: 500 !important;
        background-color: #f5f6f7 !important;
        border-radius: 8px !important;
        border: 1px solid #e8e8ee !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .streamlit-expanderHeader:hover { background-color: #e8e8ea !important; }
    
    /* ============================================================
       TARJETAS MÉTRICAS - TAMAÑO MÁS PEQUEÑO
       ============================================================ */
    div[data-testid="metric-container"] {
        border: 1px solid #d0d0d5 !important;
        border-radius: 12px !important;
        padding: 0.8rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
        background: transparent !important;
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="metric-container"] > label {
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-weight: 600 !important;
    }
    
    /* Ajustar el tamaño del valor numérico de las tarjetas */
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
    }
    
    .stAlert {
        border-radius: 10px !important;
        border-left: 4px solid #1b1b32 !important;
    }
    
    .stAlert > div {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stCaption, .caption {
        font-size: 0.75rem !important;
        font-weight: 400 !important;
    }
    
    @media (max-width: 768px) {
        .main .block-container { padding: 0.5rem 0.8rem !important; }
        .stButton > button { font-size: 0.8rem !important; padding: 0.5rem 1.2rem !important; }
        div[data-testid="metric-container"] { padding: 0.5rem !important; }
        div[data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
    }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #f5f6f7; }
    ::-webkit-scrollbar-thumb { background: #d0d0d5; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #b0b0b8; }
</style>
""", unsafe_allow_html=True)

# ---------- Título y contenido ----------
st.title("Simulador de Tanque con Descarga Gravitatoria")

# ---------- Imagen ----------
st.markdown(
    f'''
    <div style="text-align: center; margin: 20px 0;">
    <img src="https://raw.githubusercontent.com/ffedezn-cloud/simulacion-tanque/main/assets/images/diagrama_tanque.png"
             alt="Esquema del tanque" 
             style="width: 60%; max-width: 500px; border: 1px solid #ddd; border-radius: 8px;">
        <p style="margin-top: 8px;">Esquema del tanque con descarga gravitatoria</p>
    </div>
    ''',
    unsafe_allow_html=True
)
st.markdown("---")

# ---------- Barra lateral (Entrada de datos) ----------
with st.sidebar:
    # Información del desarrollador
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <p style="font-size: 17px; font-weight: 600; margin-bottom: 2px;">Federico Franco</p>
            <p style="font-size: 16px; color: #888; margin-bottom: 2px;">Ingeniería Química</p>
            <a href="mailto:ffede.zn@gmail.com" style="font-size: 16px; color: #888; text-decoration: none;">
                ffede.zn@gmail.com
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.subheader("Datos Geométricos del Tanque")
    D = st.number_input("Diámetro del tanque D (m)", value=1.0, min_value=0.3, max_value=5.0, step=0.05)
    A = np.pi * (D/2)**2
    st.caption(f"Area calculada: {A:.4f} m²")
    
    L0 = st.number_input("Nivel inicial L0 (m)", value=1.0, min_value=0.0, max_value=5.0, step=0.05)
    L_max = st.number_input("Nivel máximo (rebalse) L_max (m)", value=2.0, min_value=0.5, max_value=10.0, step=0.1)
    
    st.subheader("Datos de Operación")
    F0 = st.number_input("Caudal de entrada F0 (m³/s)", value=0.002, min_value=0.0001, max_value=0.1, format="%.5f")
    x0 = st.slider("Apertura inicial de válvula x0", 0.0, 1.0, 0.5, 0.01)
    xf = st.slider("Apertura final de válvula xf", 0.0, 1.0, 0.25, 0.01)
    
    st.subheader("Datos del Fluido")
    rho = st.number_input("Densidad del fluido ρ (kg/m³)", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
    g = 9.81
    st.caption(f"Gravedad fija: g = {g} m/s²")
    
    st.subheader("Característica de la Válvula")
    tipo_valvula = st.selectbox(
        "Tipo de caracteristíca",
        ["Lineal", "Igual porcentaje", "Apertura rápida"]
    )
    
    R = 50
    if tipo_valvula == "Igual porcentaje (isoporcentual)":
        R = st.slider("Relacion de rango R (tipico 20-50)", 20, 100, 50, 5)
    
    st.subheader("Parámetros del sistema")
    t_final = st.slider("Tiempo de simulación (s)", 100, 2000, 1100, 100)

# ---------- Parámetros del modelo (CORREGIDO) ----------
params = {
    'A': A,
    'F0': F0,
    'rho': rho,
    'g': g,
    'L0': L0
}

# Calcular Cv a partir del punto de operación inicial (AHORA CON tipo_valvula y R)
Cv = calcular_Cv(F0, x0, rho, g, L0, tipo_valvula, R)
params['Cv'] = Cv

# Verificar que Cv no sea cero (para evitar errores)
if Cv == 0:
    st.error("Error: Cv es cero. Verifique que la apertura inicial x0 > 0 y L0 > 0.")
    st.stop()

# Calcular variables estacionarias (AHORA CON tipo_valvula y R)
L_ss_inicial = nivel_estacionario(F0, Cv, x0, rho, g, tipo_valvula, R)
L_ss_final = nivel_estacionario(F0, Cv, xf, rho, g, tipo_valvula, R)
x_min = F0 / (Cv * np.sqrt(rho * g * L_max)) if Cv > 0 and L_max > 0 else np.inf


# ---------- Mostrar parámetros calculados en tarjetas ----------
st.subheader("Parámetros del sistema")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Area del tanque A", f"{A:.4f} m²")
    st.metric("Cv (valvula)", f"{Cv:.4e}")
with col_b:
    st.metric("Caudal de entrada F0", f"{F0:.5f} m³/s")
    st.metric("Nivel inicial L0", f"{L0:.2f} m")
with col_c:
    st.metric("Densidad ρ", f"{rho:.0f} kg/m³")
    st.metric("Gravedad g", f"{g:.2f} m/s²")


# ===================================================================
#                    SECCIÓN 1: ANÁLISIS DEL MODELO ESTACIONARIO
# ===================================================================

st.subheader("Análisis del Modelo Estacionario")

col_ss1, col_ss2, col_ss3 = st.columns(3)

with col_ss1:
    st.metric(
        label="Coeficiente Cv",
        value=f"{Cv:.4e}"
    )

with col_ss2:
    if np.isfinite(L_ss_final):
        st.metric(
            label=f"Nivel con xf = {xf:.3f}",
            value=f"{L_ss_final:.2f} m"
        )
    else:
        st.metric(
            label=f"Nivel con xf = {xf:.3f}",
            value="No disponible"
        )

with col_ss3:
    if np.isfinite(x_min):
        st.metric(
            label="Apertura minima para no rebalsar",
            value=f"{x_min:.4f}"
        )
    else:
        st.metric(
            label="Apertura mínima para no rebalsar",
            value="No disponible"
        )

# Advertencias
if np.isfinite(L_ss_final):
    if L_ss_final > L_max:
        st.error(f"REBALSE DETECTADO\n\nEl tanque alcanza un nivel final de {L_ss_final:.2f} m, superando el nivel maximo de {L_max:.1f} m.")
    else:
        st.success(f"Sin rebalse\n\nEl tanque alcanza un nivel final de {L_ss_final:.2f} m, dentro del limite de {L_max:.1f} m.")


# ===================================================================
#                    SECCIÓN 2: ANÁLISIS DEL MODELO DINÁMICO
# ===================================================================

st.subheader("Análisis del Modelo Dinamico")

# Parámetros de simulación
dt = 10  # paso temporal fijo

# Ejecutar simulación
Xini, LX, LY = inicializar(params)
tpts, L, Y = simulacion(t_final, dt, Xini, xf, params)

# Calcular caudales
F = Y['F']
F0_constante = params['F0']

# Detectar rebalse
tiempo_rebalse = None
for i, nivel in enumerate(L):
    if nivel >= L_max:
        tiempo_rebalse = tpts[i]
        break

# Mostrar resultados en tarjetas
col_r1, col_r2 = st.columns(2)

with col_r1:
    st.metric(
        label="Nivel final",
        value=f"{L[-1]:.3f} m"
    )

with col_r2:
    st.metric(
        label="Caudal salida final",
        value=f"{F[-1]:.5f} m³/s"
    )

# Alertas de estado
if tiempo_rebalse:
    st.error(f"REBALSE DURANTE LA SIMULACION\n\nEl tanque alcanza el nivel maximo de {L_max} m a los {tiempo_rebalse:.1f} segundos.")
else:
    st.success(f"Sin rebalse durante la simulacion\n\nNivel maximo alcanzado: {max(L):.3f} m (limite: {L_max} m)")


# ---------- GRÁFICAS CON PESTAÑAS Y MEJORAS PARA MÓVILES ----------
st.subheader("Gráficas de la Simulación")

# Detectar tema del navegador
tema_oscuro = st.get_option("theme.base") == "dark"

if tema_oscuro:
    bg_color = 'rgba(30,30,30,0.95)'
    text_color = 'white'
    grid_color = 'rgba(255,255,255,0.15)'
    legend_bg = 'rgba(0,0,0,0.6)'
    template = "plotly_dark"
    colors = {
        'primary': '#4dabf7',
        'success': '#51cf66',
        'danger': '#ff6b6b',
        'secondary': '#868e96'
    }
else:
    bg_color = 'white'
    text_color = 'black'
    grid_color = 'rgba(0,0,0,0.1)'
    legend_bg = 'rgba(255,255,255,0.8)'
    template = "plotly_white"
    colors = {
        'primary': '#1f77b4',
        'success': '#2ca02c',
        'danger': '#d62728',
        'secondary': '#7f7f7f'
    }

# Configuración común para todas las gráficas
config_plotly = {
    'scrollZoom': False,
    'displayModeBar': False,
    'responsive': True
}

# Crear pestañas para organizar las gráficas
tab1, tab2, tab3 = st.tabs(["Nivel del Tanque", "Caudales", "Características de Válvula"])

with tab1:
    with st.container(border=True):
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=tpts, y=L, mode='lines', name='Nivel L(t)', line=dict(color=colors['primary'], width=2.5)))
        
        fig1.add_hline(y=L_max, line=dict(color=colors['danger'], width=1.5, dash='dash'))
        fig1.add_hline(y=L0, line=dict(color=colors['secondary'], width=1, dash='dot'))
        if np.isfinite(L_ss_final) and L_ss_final <= L_max:
            fig1.add_hline(y=L_ss_final, line=dict(color=colors['success'], width=1, dash='dash'))
        if tiempo_rebalse:
            fig1.add_vline(x=tiempo_rebalse, line=dict(color=colors['danger'], width=1.5, dash='dot'))
        
        fig1.add_annotation(
            x=50, y=L_max+0.05, 
            text=f'L_max = {L_max} m', 
            showarrow=False,
            font=dict(color=text_color, size=12),
            bgcolor=legend_bg,
            bordercolor=colors['danger'],
            borderwidth=1
        )
        if tiempo_rebalse:
            fig1.add_annotation(
                x=tiempo_rebalse+20, y=L_max-0.15, 
                text=f'Rebalse t={tiempo_rebalse:.1f}s', 
                showarrow=True,
                arrowhead=1,
                ax=30, ay=-30,
                font=dict(color=text_color, size=12),
                bgcolor=legend_bg,
                bordercolor=colors['danger'],
                borderwidth=1
            )
        
        fig1.update_layout(
            template=template,
            dragmode=False, 
            
            xaxis=dict(
                title='Tiempo (s)',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1
            ),
            yaxis=dict(
                title='Nivel L (m)',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1
            ),
            height=350,  
            hovermode='x unified',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color=text_color, size=12),
            legend=dict(
                font=dict(color=text_color, size=11),
                bgcolor=legend_bg,
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            margin=dict(l=40, r=10, t=50, b=50)
        )
        st.plotly_chart(fig1, use_container_width=True, config=config_plotly)

with tab2:
    with st.container(border=True):
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=tpts, y=[F0_constante]*len(tpts), mode='lines', name='F0 (entrada)', line=dict(color=colors['success'], width=2.5, dash='dash')))
        fig2.add_trace(go.Scatter(x=tpts, y=F, mode='lines', name='F (salida)', line=dict(color=colors['danger'], width=2.5)))
        
        if tiempo_rebalse:
            fig2.add_vline(x=tiempo_rebalse, line=dict(color=colors['danger'], width=1.5, dash='dot'))
            fig2.add_annotation(
                x=tiempo_rebalse+20, y=max(F)*0.8, 
                text=f'Rebalse t={tiempo_rebalse:.1f}s', 
                showarrow=True,
                arrowhead=1,
                ax=30, ay=-30,
                font=dict(color=text_color, size=12),
                bgcolor=legend_bg,
                bordercolor=colors['danger'],
                borderwidth=1
            )
        
        fig2.update_layout(
            template=template,
            dragmode=False, 
            
            xaxis=dict(
                title='Tiempo (s)',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1
            ),
            yaxis=dict(
                title='Caudal (m³/s)',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1
            ),
            height=350,  
            hovermode='x unified',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color=text_color, size=12),
            legend=dict(
                font=dict(color=text_color, size=11),
                bgcolor=legend_bg,
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            margin=dict(l=40, r=10, t=50, b=50)
        )
        st.plotly_chart(fig2, use_container_width=True, config=config_plotly)

with tab3:
    with st.container(border=True):
        x_vals = np.linspace(0, 1, 200)
        f_lineal = [f_apertura(x, "Lineal", R) for x in x_vals]
        f_isoporc = [f_apertura(x, "Igual porcentaje", R) for x in x_vals]
        f_rapida = [f_apertura(x, "Apertura rápida", R) for x in x_vals]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=x_vals, y=f_lineal, mode='lines', name='Lineal', line=dict(color='#1f77b4', width=3, dash='solid')))
        fig3.add_trace(go.Scatter(x=x_vals, y=f_isoporc, mode='lines', name=f'Isoporcentual (R={R})', line=dict(color='#d62728', width=3, dash='dash')))
        fig3.add_trace(go.Scatter(x=x_vals, y=f_rapida, mode='lines', name='Apertura rápida', line=dict(color='#2ca02c', width=3, dash='dot')))
        
        fig3.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Referencia y=x', line=dict(color='gray', width=1, dash='dash'), opacity=0.5))
        
        fig3.add_trace(go.Scatter(x=[x0], y=[f_apertura(x0, tipo_valvula, R)], mode='markers', name=f'x₀ = {x0:.2f}', marker=dict(color='#ff7f0e', size=14, symbol='circle', line=dict(color='white', width=2))))
        fig3.add_trace(go.Scatter(x=[xf], y=[f_apertura(xf, tipo_valvula, R)], mode='markers', name=f'x_f = {xf:.2f}', marker=dict(color='#9467bd', size=14, symbol='diamond', line=dict(color='white', width=2))))
        
        if np.isfinite(x_min):
            fig3.add_vline(x=x_min, line=dict(color='#ff7f0e', width=2, dash='dash'))
            fig3.add_annotation(
                x=x_min+0.03, y=0.9, 
                text=f'x_min = {x_min:.3f}', 
                showarrow=False,
                font=dict(color=text_color, size=12),
                bgcolor=legend_bg,
                bordercolor='#ff7f0e',
                borderwidth=1,
                borderpad=4
            )
        
        fig3.update_layout(
            template=template,
            dragmode=False,  
            
            xaxis=dict(
                title='Apertura x',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1,
                range=[-0.05, 1.05]
            ),
            yaxis=dict(
                title='Flujo f(x)',
                title_font=dict(color=text_color, size=14),
                tickfont=dict(color=text_color, size=12),
                gridcolor=grid_color,
                showgrid=True,
                zeroline=True,
                zerolinecolor=grid_color,
                zerolinewidth=1,
                showline=True,
                linecolor=grid_color,
                linewidth=1,
                range=[-0.05, 1.05]
            ),
            height=350,  
            hovermode='x unified',
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            font=dict(color=text_color, size=12),
            legend=dict(
                font=dict(color=text_color, size=11),
                bgcolor=legend_bg,
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='center',
                x=0.5
            ),
            margin=dict(l=40, r=10, t=60, b=50)
        )
        st.plotly_chart(fig3, use_container_width=True, config=config_plotly)


# ===================================================================
#                    SECCIÓN 4: DOCUMENTACIÓN DEL MODELO
# ===================================================================

st.markdown("---")
st.subheader("Documentación del Modelo")

with st.expander("Modelo Conceptual"):
    pdf_url = "https://raw.githubusercontent.com/ffedezn-cloud/simulacion-tanque/main/assets/docs/modelo_conceptual.pdf"

    viewer_url = f"https://docs.google.com/viewer?url={pdf_url}&embedded=true"
    
    st.markdown(
        f'''
        <iframe src="{viewer_url}" 
                width="100%" 
                height="700px" 
                style="border: 1px solid #ddd; border-radius: 4px;">
        </iframe>
        ''',
        unsafe_allow_html=True
    )

with st.expander("Codigo en Octave"):
    st.markdown("""
    Codigo autocontenido para simular el tanque en Octave.
    Para utilizarlo:
    1. Copiar el codigo
    2. Guardarlo en un archivo con extension .m
    3. Ejecutarlo en Octave
    """)
    
    codigo_octave = '''% Simulador de Tanque con Descarga Gravitatoria
% Tanque con descarga gravitatoria
% En X estan las variables de estado.
% En Y deben ir las variables que se requieren en las ODEs o que se quieren graficar.

clear all; close all; clc;

%=============== Modelo =================

% ODEs
function dX = ODEs(t,X)
  % En dX devuelve el vector columna de derivadas

  % Recupera variables X
  [L] = num2cell(X'){1,:};

  % Recupera variables Y
  Y = AEs(t,X);
  [A, F0, F] = num2cell(Y){1,:};

  % Ecuaciones diferenciales
  dL = (F0 - F)/A;

  dX = [dL]'; % vector columna
endfunction % ODEs
%---------------------------------------

% AEs
function Y = AEs(t,X)
  % En Y devuelve el vector fila de variables requeridas por ODEs o a graficar.

  % Recupera variables X
  [L] = num2cell(X'){1,:};

  % Parametros
  F0 = 2E-3; A = 0.785; Cv = 4.039E-5; rho = 1000; g = 9.81; % Sistema SI

  % Ecuaciones algebraicas
  if t < 0                 %Apertura de la valvula
    x = 0.5;
  else
    x = 0.25;
  endif

  F = Cv*x*sqrt(rho*g*L);      %Caudal de salida

  Y = [A, F0, F];
endfunction % AEs
%---------------------------------------

% Inicializacion
function [tfin dt Xini LX LY] = inicializacion
  % Inicializa la simulacion

  % Parametros de simulacion
  tfin = 1100; % tiempo final
  dt = 10; % paso temporal

  % Inicializacion
  Lini = 1; % m
  Xini = [Lini]; % Inicializa la variable de estado

  % Leyendas
  LX = {'L'}; % Leyendas de las variables X
  LY = {'A' 'F0' 'F'}; % Leyendas de las variables Y
endfunction % inicializar
%---------------------------------------

% Analisis
function analizar(LX,LY,tpts,X,Y)
  % Analisis de resultados. Funciones disponibles:
  % graficar({leyendas}, 'titulo', 'rotulo x', 'rotulo y', [limitesy])
  % vector(leyenda)

  % Solo graficar, sin exportar
  graficar({'L'}, 'Nivel vs. tiempo', 's', 'm', [0 3]);
  graficar({'F0' 'F'}, 'Caudales vs. tiempo', 's', 'm^3/s', [0 4E-3]);

  % Control de rebalse
  Lmax = 2; % m Altura del tanque
  Lt = vector('L'); % Recupera el vector de niveles.
  if Lt(end) <= Lmax % Verifica el ultimo nivel porque es el mayor.
    disp('El tanque no rebalso.');
  else
    tr = interp1(Lt, tpts, Lmax); % Se puede usar interp1 porque Lt es creciente.
    disp(['El tanque rebalso en el tiempo igual a ' num2str(tr) ' s.']);
  endif

endfunction % analizar
%=======================================

%=============== Resolvedor (integrado) =================

function v = vector(leyenda)
  % Devuelve el vector columna correspondiente a la variable leyenda.
  global LX LY tpts X Y
  indicex = find(strcmp(LX, leyenda)); % Indice del elemento
  if length(indicex) == 1
    v = X(:,indicex);
  else
    indicey = find(strcmp(LY, leyenda)); % Indice del elemento
    if length(indicey) == 1
      v = Y(:,indicey);
    else
      disp(['Error: Variable "' leyenda '" no encontrada.']);
      error('Codigo de error: %d - Descripcion del error', 1); % Detener con un mensaje
    endif
  endif
endfunction % vector
%---------------------------------------

function graficar(LV, titulo, rotulox, rotuloy, limitesy)
  % Crea una figura
  % LV: Arreglo de celdas fila que contiene los textos para las leyendas de las variables a graficar.
  % titulo: Titulo de la figura.
  % rotulox: Rotulo para la abscisa.
  % rotuloy: Rotulo para la ordenada.
  % limitesy: Vector fila con el limite inferior y el superior para la ordenada. Es opcional.
  global tpts

  colores = ['r' 'g' 'b' 'c' 'm' 'y' 'k'];

  figure;

  % Variables
  hold on; % Mantiene la figura para superponer la siguiente grafica.
  for i = 1:length(LV)
    plot(tpts, vector(LV{i}), colores(mod(i-1,length(LV)) + 1), 'LineWidth', 2); % Linea con espesor 2
  endfor

  % Titulo del grafico
  title(titulo);

  % Configurar los ejes
  xlabel(rotulox); % Titulo del eje x
  ylabel(rotuloy); % Titulo del eje y

  % Verificar y asignar valores predeterminados
  if nargin == 5
    ylim(limitesy); % Rango del eje y
  endif

  % Mostrar la cuadricula
  grid on;

  % Anadir la leyenda
  legend(LV, 'Location', 'northeast'); % Leyenda en la esquina superior derecha

endfunction % graficar
%---------------------------------------

function [tpts X Y] = simulacion(tfin,dt,Xini)
  % Realiza la simulacion.

  % Resolucion
  nts = ceil(tfin/dt + 1); % redondea por exceso
  tpts = linspace(0, tfin, nts)';
  [tpts X] = ode45(@ODEs, tpts, Xini);

  % Calculo de las variables dependientes
  for i = 1:size(tpts,1)
    Y(i,:) = AEs(tpts(i),X(i,:)');
  endfor

endfunction % simulacion

%=============== Simulacion =================
clc;
disp('Resolvedor v01, 2025 (version todo en uno del archivo del Dr. Tarifa)');
disp('');
disp('Resolviendo el modelo...');

global LX LY tpts X Y

% Inicializacion
[tfin dt Xini LX LY] = inicializacion;

% Resolucion
[tpts X Y] = simulacion(tfin,dt,Xini);

% Analisis (solo graficos, sin exportar)
analizar(LX,LY,tpts,X,Y);

disp('');
disp('Simulacion finalizada.');
'''
    
    st.code(codigo_octave, language="octave")
    
    st.download_button(
        label="Descargar modelo_tanque.m",
        data=codigo_octave,
        file_name="modelo_tanque.m",
        mime="text/plain"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 14px; padding: 10px 0;">
        Simulador desplegado con Streamlit por Federico Franco
    </div>
    """,
    unsafe_allow_html=True
)
