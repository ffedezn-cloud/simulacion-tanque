import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulador de Tanque Gravitatorio", layout="wide")

st.markdown("""
<style>
    /* DeepSeek Dark Mode style */
    .stApp {
        background-color: #0a0a0a;
        font-family: 'Courier New', 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
    }
    
    .main {
        background-color: #0a0a0a;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Courier New', monospace;
        color: #e0e0e0;
        font-weight: normal;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 1.8rem;
        border-bottom: 1px solid #2a2a2a;
        padding-bottom: 8px;
    }
    
    h2 {
        font-size: 1.4rem;
        border-left: 3px solid #3a6ea5;
        padding-left: 12px;
    }
    
    .stMarkdown, .stText, .stCaption, p, li, .stAlert {
        font-family: 'Courier New', monospace;
        color: #c0c0c0;
    }
    
    .stSidebar {
        background-color: #0d0d0d;
        border-right: 1px solid #1f1f1f;
    }
    
    .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar .stNumberInput, .stSidebar .stSlider {
        color: #c0c0c0;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #d0d0d0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button {
        font-family: 'Courier New', monospace;
        background-color: #1a1a1a;
        color: #d0d0d0;
        border: 1px solid #333;
        border-radius: 0px;
    }
    
    .stButton > button:hover {
        background-color: #252525;
        border-color: #3a6ea5;
        color: #e0e0e0;
    }
    
    .stAlert {
        background-color: #0d0d0d;
        border-left: 3px solid #3a6ea5;
        border-radius: 0px;
        padding: 8px 12px;
    }
    
    .stMetric {
        background-color: #0d0d0d;
        border: 1px solid #1f1f1f;
        border-radius: 0px;
        padding: 8px;
    }
    
    .stMetric label {
        color: #808080 !important;
        font-size: 0.7rem;
        text-transform: uppercase;
    }
    
    .stMetric .stMetricValue {
        color: #d0d0d0 !important;
        font-size: 1.4rem;
    }
    
    .stSelectbox, .stNumberInput, .stSlider {
        background-color: #0d0d0d;
    }
    
    input, textarea, .stSelectbox div {
        background-color: #0d0d0d !important;
        color: #d0d0d0 !important;
        border-color: #2a2a2a !important;
        font-family: 'Courier New', monospace !important;
    }
    
    hr {
        border-color: #1f1f1f;
        margin: 16px 0;
    }
    
    code, pre {
        background-color: #0d0d0d;
        color: #d0d0d0;
        font-family: 'Courier New', monospace;
        border: 1px solid #1f1f1f;
    }
    
    .stExpander {
        background-color: #0d0d0d;
        border: 1px solid #1f1f1f;
        border-radius: 0px;
    }
    
    .stExpander summary {
        font-family: 'Courier New', monospace;
        color: #c0c0c0;
    }
    
    .stInfo {
        background-color: #0d0d0d;
        border-left: 3px solid #3a6ea5;
    }
    
    .stSuccess {
        background-color: #0d0d0d;
        border-left: 3px solid #2d6a4f;
    }
    
    .stWarning {
        background-color: #0d0d0d;
        border-left: 3px solid #b45309;
    }
    
    .stError {
        background-color: #0d0d0d;
        border-left: 3px solid #991b1b;
    }
    
    .stCaption {
        color: #6a6a6a;
        font-size: 0.7rem;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d0d0d;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2a2a2a;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3a3a3a;
    }
</style>
""", unsafe_allow_html=True)

st.title("tanque_gravitatorio")
st.caption("simulacion dinamica de nivel con descarga por gravedad")
st.markdown("---")

with st.sidebar:
    st.markdown("### geometria")
    D = st.number_input("diametro [m]", value=1.0, min_value=0.3, max_value=5.0, step=0.05)
    A = np.pi * (D/2)**2
    st.caption(f"area = {A:.4f} m²")
    
    L0 = st.number_input("nivel_inicial [m]", value=1.0, min_value=0.0, max_value=5.0, step=0.05)
    L_max = st.number_input("nivel_maximo [m]", value=2.0, min_value=0.5, max_value=10.0, step=0.1)
    
    st.markdown("### operacion")
    F0 = st.number_input("caudal_entrada [m³/s]", value=0.002, min_value=0.0001, max_value=0.1, format="%.5f")
    x0 = st.slider("apertura_inicial", 0.0, 1.0, 0.5, 0.01)
    xf = st.slider("apertura_final", 0.0, 1.0, 0.25, 0.01)
    
    st.markdown("### fluido")
    rho = st.number_input("densidad [kg/m³]", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
    
    st.markdown("### valvula")
    tipo_valvula = st.selectbox(
        "caracteristica",
        ["lineal", "isoporcentual", "apertura_rapida"]
    )
    
    R = 50
    if tipo_valvula == "isoporcentual":
        R = st.slider("relacion_rango", 20, 100, 50, 5)
    
    st.markdown("### simulacion")
    t_final = st.slider("tiempo [s]", 100, 2000, 1100, 100)

g = 9.81

def f_apertura(x, tipo, R):
    x = max(0.0, min(1.0, x))
    if tipo == "lineal":
        return x
    elif tipo == "isoporcentual":
        return R**(x-1)
    elif tipo == "apertura_rapida":
        return 1 - (1-x)**2
    return x

f0 = f_apertura(x0, tipo_valvula, R)
Cv_max = F0 / (f0 * np.sqrt(rho * g * L0))

col_a, col_b = st.columns(2)
with col_a:
    st.metric("area", f"{A:.4f} m²")
    st.metric("cv_max", f"{Cv_max:.3e}")
with col_b:
    st.metric("caudal_entrada", f"{F0:.5f} m³/s")
    st.metric("nivel_inicial", f"{L0:.2f} m")

def caudal_salida(L, x):
    f = f_apertura(x, tipo_valvula, R)
    return Cv_max * f * np.sqrt(rho * g * np.maximum(L, 0.001))

def modelo_dinamico(X, t, F0, A, x):
    L = X[0]
    F = caudal_salida(L, x)
    dLdt = (F0 - F) / A
    return [dLdt]

st.markdown("### analisis_estacionario")

L_ss_inicial = (F0/(Cv_max * f_apertura(x0, tipo_valvula, R)))**2/(rho*g) if x0 > 0 and f_apertura(x0, tipo_valvula, R) > 0 else np.inf
L_ss_final = (F0/(Cv_max * f_apertura(xf, tipo_valvula, R)))**2/(rho*g) if xf > 0 and f_apertura(xf, tipo_valvula, R) > 0 else np.inf

col1, col2 = st.columns(2)
with col1:
    st.info(f"x = {x0:.3f}")
    st.write(f"nivel_estacionario = {L_ss_inicial:.2f} m")
    st.write(f"{'no_rebalsa' if L_ss_inicial <= L_max else 'rebalsa'}")
with col2:
    st.info(f"x = {xf:.3f}")
    st.write(f"nivel_estacionario = {L_ss_final:.2f} m")
    st.write(f"{'no_rebalsa' if L_ss_final <= L_max else 'rebalsa'}")

x_min = F0/(Cv_max * np.sqrt(rho * g * L_max))
st.metric("apertura_minima_segura", f"{x_min:.4f}")

if xf < x_min:
    st.warning("alerta: apertura_final < minima_segura")
else:
    st.success("operacion_segura")

x_vals = np.linspace(0, 1, 100)
f_vals = [f_apertura(x, tipo_valvula, R) for x in x_vals]

fig_valv, ax_valv = plt.subplots(figsize=(8, 4))
ax_valv.plot(x_vals, f_vals, '#3a6ea5', linewidth=1.5)
ax_valv.plot(x0, f_apertura(x0, tipo_valvula, R), 'o', markersize=5, color='#d0d0d0')
ax_valv.set_xlabel("apertura x", fontsize=10)
ax_valv.set_ylabel("flujo f(x)", fontsize=10)
ax_valv.set_title(f"valvula: {tipo_valvula}", fontsize=11)
ax_valv.grid(True, alpha=0.15, color='#2a2a2a')
ax_valv.set_facecolor('#0a0a0a')
fig_valv.patch.set_facecolor('#0a0a0a')
ax_valv.tick_params(colors='#808080')
for spine in ax_valv.spines.values():
    spine.set_color('#2a2a2a')
ax_valv.xaxis.label.set_color('#c0c0c0')
ax_valv.yaxis.label.set_color('#c0c0c0')
ax_valv.title.set_color('#d0d0d0')
st.pyplot(fig_valv)

st.markdown("### simulacion_dinamica")

t = np.linspace(0, t_final, 1000)
X0 = [L0]
sol = odeint(modelo_dinamico, X0, t, args=(F0, A, xf))
L = sol[:, 0]
F = caudal_salida(L, xf)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

ax1.plot(t, L, '#3a6ea5', linewidth=1.5)
ax1.axhline(y=L_max, color='#b45309', linestyle='--', linewidth=1, label=f'L_max = {L_max} m')
ax1.axhline(y=L0, color='#808080', linestyle=':', linewidth=0.8, alpha=0.5, label=f'L0 = {L0} m')
ax1.set_xlabel("tiempo [s]", fontsize=10)
ax1.set_ylabel("nivel [m]", fontsize=10)
ax1.set_title("evolucion del nivel", fontsize=11)
ax1.grid(True, alpha=0.15, color='#2a2a2a')
ax1.legend(loc='best', facecolor='#0d0d0d', edgecolor='#2a2a2a', labelcolor='#c0c0c0')

ax2.plot(t, np.ones_like(t)*F0, '#2d6a4f', linestyle='--', linewidth=1.2, label=f'F0 = {F0:.5f}')
ax2.plot(t, F, '#b45309', linewidth=1.5, label='F_salida')
ax2.set_xlabel("tiempo [s]", fontsize=10)
ax2.set_ylabel("caudal [m³/s]", fontsize=10)
ax2.set_title("caudales", fontsize=11)
ax2.grid(True, alpha=0.15, color='#2a2a2a')
ax2.legend(loc='best', facecolor='#0d0d0d', edgecolor='#2a2a2a', labelcolor='#c0c0c0')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0a0a0a')
    ax.tick_params(colors='#808080')
    for spine in ax.spines.values():
        spine.set_color('#2a2a2a')
    ax.xaxis.label.set_color('#c0c0c0')
    ax.yaxis.label.set_color('#c0c0c0')
    ax.title.set_color('#d0d0d0')

fig.patch.set_facecolor('#0a0a0a')
plt.tight_layout()
st.pyplot(fig)

st.markdown("### informe")

L_final = L[-1]
tiempo_rebalse = None
for i, nivel in enumerate(L):
    if nivel >= L_max:
        tiempo_rebalse = t[i]
        break

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("nivel_final", f"{L_final:.3f} m")
with col_r2:
    st.metric("caudal_salida_final", f"{F[-1]:.5f} m³/s")
with col_r3:
    st.metric("error_estacionario", f"{abs(F0 - F[-1]):.6f}")

if tiempo_rebalse:
    st.error(f"rebalse en t = {tiempo_rebalse:.1f} s")
else:
    st.success(f"sin rebalse - nivel_maximo = {max(L):.3f} m")

st.markdown("### recomendacion")
if xf < x_min:
    st.markdown(f"""
    apertura_actual = {xf:.4f}
    apertura_minima = {x_min:.4f}
    
    >> ajustar valvula a x = {x_min:.4f}
    """)
else:
    st.markdown(f"""
    apertura_actual = {xf:.4f}
    apertura_minima = {x_min:.4f}
    
    >> operacion segura
    """)

with st.expander("modelo"):
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    st.caption("variables: A = area, L = nivel, F0 = caudal_entrada, f(x) = valvula, Cv = coeficiente, rho = densidad, g = 9.81")
