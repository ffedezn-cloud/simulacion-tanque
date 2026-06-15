import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulador de Tanque Gravitatorio", layout="wide")

st.markdown("""
<style>
    /* DeepSeek Dark Mode exact style */
    .stApp {
        background-color: #0d0d0d;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    }
    
    .main {
        background-color: #0d0d0d;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        color: #f0f0f0;
        letter-spacing: -0.3px;
    }
    
    h1 {
        font-size: 1.8rem;
        border-bottom: 1px solid #262626;
        padding-bottom: 8px;
    }
    
    h2 {
        font-size: 1.3rem;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
    }
    
    h3 {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #9ca3af;
        margin-bottom: 0.5rem;
    }
    
    .stMarkdown, .stText, p, li, .stAlert, .stCaption {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e5e5e5;
        line-height: 1.5;
    }
    
    .stSidebar {
        background-color: #0a0a0a;
        border-right: 1px solid #262626;
    }
    
    .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar .stNumberInput, .stSidebar .stSlider {
        color: #e5e5e5;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #d4d4d4;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-left: 2px solid #3b82f6;
        padding-left: 10px;
        margin-top: 1rem;
    }
    
    .stButton > button {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #1a1a1a;
        color: #e5e5e5;
        border: 1px solid #333;
        border-radius: 4px;
    }
    
    .stButton > button:hover {
        background-color: #252525;
        border-color: #3b82f6;
        color: #f0f0f0;
    }
    
    .stAlert {
        background-color: #0a0a0a;
        border-left: 3px solid #3b82f6;
        border-radius: 0px;
        padding: 10px 14px;
    }
    
    .stMetric {
        background-color: #0a0a0a;
        border: 1px solid #262626;
        border-radius: 4px;
        padding: 10px;
    }
    
    .stMetric label {
        color: #9ca3af !important;
        font-size: 0.75rem;
        font-weight: 400;
        text-transform: none;
    }
    
    .stMetric .stMetricValue {
        color: #f0f0f0 !important;
        font-size: 1.5rem;
        font-weight: 500;
    }
    
    .stSelectbox, .stNumberInput, .stSlider {
        background-color: #0a0a0a;
    }
    
    input, textarea, .stSelectbox div {
        background-color: #1a1a1a !important;
        color: #e5e5e5 !important;
        border-color: #333 !important;
        border-radius: 4px !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    hr {
        border-color: #262626;
        margin: 20px 0;
    }
    
    code, pre {
        background-color: #1a1a1a;
        color: #e5e5e5;
        font-family: 'SF Mono', 'Courier New', monospace;
        border: 1px solid #333;
        border-radius: 4px;
    }
    
    .stExpander {
        background-color: #0a0a0a;
        border: 1px solid #262626;
        border-radius: 4px;
    }
    
    .stExpander summary {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #e5e5e5;
    }
    
    .stInfo {
        background-color: #0a0a0a;
        border-left: 3px solid #3b82f6;
    }
    
    .stSuccess {
        background-color: #0a0a0a;
        border-left: 3px solid #22c55e;
    }
    
    .stWarning {
        background-color: #0a0a0a;
        border-left: 3px solid #f59e0b;
    }
    
    .stError {
        background-color: #0a0a0a;
        border-left: 3px solid #ef4444;
    }
    
    .stCaption {
        color: #737373;
        font-size: 0.7rem;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #444;
    }
</style>
""", unsafe_allow_html=True)

st.title("Tanque con descarga gravitatoria")
st.caption("Simulación dinámica de nivel con modelo no lineal")
st.markdown("---")

with st.sidebar:
    st.markdown("### Geometría")
    D = st.number_input("Diámetro [m]", value=1.0, min_value=0.3, max_value=5.0, step=0.05)
    A = np.pi * (D/2)**2
    st.caption(f"Área = {A:.4f} m²")
    
    L0 = st.number_input("Nivel inicial [m]", value=1.0, min_value=0.0, max_value=5.0, step=0.05)
    L_max = st.number_input("Nivel máximo [m]", value=2.0, min_value=0.5, max_value=10.0, step=0.1)
    
    st.markdown("### Operación")
    F0 = st.number_input("Caudal de entrada [m³/s]", value=0.002, min_value=0.0001, max_value=0.1, format="%.5f")
    x0 = st.slider("Apertura inicial", 0.0, 1.0, 0.5, 0.01)
    xf = st.slider("Apertura final", 0.0, 1.0, 0.25, 0.01)
    
    st.markdown("### Fluido")
    rho = st.number_input("Densidad [kg/m³]", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
    
    st.markdown("### Válvula")
    tipo_valvula = st.selectbox(
        "Característica",
        ["lineal", "isoporcentual", "apertura rápida"]
    )
    
    R = 50
    if tipo_valvula == "isoporcentual":
        R = st.slider("Relación de rango", 20, 100, 50, 5)
    
    st.markdown("### Simulación")
    t_final = st.slider("Tiempo [s]", 100, 2000, 1100, 100)

g = 9.81

def f_apertura(x, tipo, R):
    x = max(0.0, min(1.0, x))
    if tipo == "lineal":
        return x
    elif tipo == "isoporcentual":
        return R**(x-1)
    elif tipo == "apertura rápida":
        return 1 - (1-x)**2
    return x

f0 = f_apertura(x0, tipo_valvula, R)
Cv_max = F0 / (f0 * np.sqrt(rho * g * L0))

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Área", f"{A:.4f} m²")
    st.metric("Cv máximo", f"{Cv_max:.3e}")
with col_b:
    st.metric("Caudal entrada", f"{F0:.5f} m³/s")
    st.metric("Nivel inicial", f"{L0:.2f} m")

def caudal_salida(L, x):
    f = f_apertura(x, tipo_valvula, R)
    return Cv_max * f * np.sqrt(rho * g * np.maximum(L, 0.001))

def modelo_dinamico(X, t, F0, A, x):
    L = X[0]
    F = caudal_salida(L, x)
    dLdt = (F0 - F) / A
    return [dLdt]

st.markdown("### Análisis estacionario")

L_ss_inicial = (F0/(Cv_max * f_apertura(x0, tipo_valvula, R)))**2/(rho*g) if x0 > 0 and f_apertura(x0, tipo_valvula, R) > 0 else np.inf
L_ss_final = (F0/(Cv_max * f_apertura(xf, tipo_valvula, R)))**2/(rho*g) if xf > 0 and f_apertura(xf, tipo_valvula, R) > 0 else np.inf

col1, col2 = st.columns(2)
with col1:
    st.info(f"Apertura x = {x0:.3f}")
    st.write(f"Nivel estacionario: **{L_ss_inicial:.2f} m**")
    st.write(f"{'No rebalsa' if L_ss_inicial <= L_max else 'Rebalsa'}")
with col2:
    st.info(f"Apertura x = {xf:.3f}")
    st.write(f"Nivel estacionario: **{L_ss_final:.2f} m**")
    st.write(f"{'No rebalsa' if L_ss_final <= L_max else 'Rebalsa'}")

x_min = F0/(Cv_max * np.sqrt(rho * g * L_max))
st.metric("Apertura mínima segura", f"{x_min:.4f}")

if xf < x_min:
    st.warning("Alerta: La apertura final es menor que la apertura mínima segura.")
else:
    st.success("Operación segura.")

x_vals = np.linspace(0, 1, 100)
f_vals = [f_apertura(x, tipo_valvula, R) for x in x_vals]

fig_valv, ax_valv = plt.subplots(figsize=(8, 4))
ax_valv.plot(x_vals, f_vals, '#3b82f6', linewidth=1.5)
ax_valv.plot(x0, f_apertura(x0, tipo_valvula, R), 'o', markersize=5, color='#e5e5e5')
ax_valv.set_xlabel("Apertura x", fontsize=10)
ax_valv.set_ylabel("Flujo f(x)", fontsize=10)
ax_valv.set_title(f"Característica de la válvula: {tipo_valvula}", fontsize=11)
ax_valv.grid(True, alpha=0.15, color='#333')
ax_valv.set_facecolor('#0d0d0d')
fig_valv.patch.set_facecolor('#0d0d0d')
ax_valv.tick_params(colors='#9ca3af')
for spine in ax_valv.spines.values():
    spine.set_color('#333')
ax_valv.xaxis.label.set_color('#e5e5e5')
ax_valv.yaxis.label.set_color('#e5e5e5')
ax_valv.title.set_color('#f0f0f0')
st.pyplot(fig_valv)

st.markdown("### Simulación dinámica")

t = np.linspace(0, t_final, 1000)
X0 = [L0]
sol = odeint(modelo_dinamico, X0, t, args=(F0, A, xf))
L = sol[:, 0]
F = caudal_salida(L, xf)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

ax1.plot(t, L, '#3b82f6', linewidth=1.5)
ax1.axhline(y=L_max, color='#f59e0b', linestyle='--', linewidth=1, label=f'Nivel máximo = {L_max} m')
ax1.axhline(y=L0, color='#9ca3af', linestyle=':', linewidth=0.8, alpha=0.5, label=f'Nivel inicial = {L0} m')
ax1.set_xlabel("Tiempo [s]", fontsize=10)
ax1.set_ylabel("Nivel [m]", fontsize=10)
ax1.set_title("Evolución del nivel", fontsize=11)
ax1.grid(True, alpha=0.15, color='#333')
ax1.legend(loc='best', facecolor='#0a0a0a', edgecolor='#333', labelcolor='#e5e5e5')

ax2.plot(t, np.ones_like(t)*F0, '#22c55e', linestyle='--', linewidth=1.2, label=f'Caudal entrada = {F0:.5f}')
ax2.plot(t, F, '#ef4444', linewidth=1.5, label='Caudal salida')
ax2.set_xlabel("Tiempo [s]", fontsize=10)
ax2.set_ylabel("Caudal [m³/s]", fontsize=10)
ax2.set_title("Caudales", fontsize=11)
ax2.grid(True, alpha=0.15, color='#333')
ax2.legend(loc='best', facecolor='#0a0a0a', edgecolor='#333', labelcolor='#e5e5e5')

for ax in [ax1, ax2]:
    ax.set_facecolor('#0d0d0d')
    ax.tick_params(colors='#9ca3af')
    for spine in ax.spines.values():
        spine.set_color('#333')
    ax.xaxis.label.set_color('#e5e5e5')
    ax.yaxis.label.set_color('#e5e5e5')
    ax.title.set_color('#f0f0f0')

fig.patch.set_facecolor('#0d0d0d')
plt.tight_layout()
st.pyplot(fig)

st.markdown("### Informe")

L_final = L[-1]
tiempo_rebalse = None
for i, nivel in enumerate(L):
    if nivel >= L_max:
        tiempo_rebalse = t[i]
        break

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("Nivel final", f"{L_final:.3f} m")
with col_r2:
    st.metric("Caudal salida final", f"{F[-1]:.5f} m³/s")
with col_r3:
    st.metric("Error estacionario", f"{abs(F0 - F[-1]):.6f}")

if tiempo_rebalse:
    st.error(f"Rebalse detectado en t = {tiempo_rebalse:.1f} s")
else:
    st.success(f"Sin rebalse - Nivel máximo: {max(L):.3f} m")

st.markdown("### Recomendación")
if xf < x_min:
    st.markdown(f"""
    - Apertura actual: **{xf:.4f}**
    - Apertura mínima segura: **{x_min:.4f}**
    
    Ajustar la válvula a una apertura mayor o igual a **{x_min:.4f}**.
    """)
else:
    st.markdown(f"""
    - Apertura actual: **{xf:.4f}**
    - Apertura mínima segura: **{x_min:.4f}**
    
    Operación segura.
    """)

with st.expander("Modelo matemático"):
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    st.caption("A: área del tanque, L: nivel, F0: caudal de entrada, f(x): característica de la válvula, Cv: coeficiente de válvula, ρ: densidad, g = 9.81 m/s²")
