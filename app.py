import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulador de Tanque Gravitatorio", layout="wide")

st.markdown("""
<style>
    /* Estilo GitHub Dark */
    .stApp {
        background-color: #0d1117;
        font-family: 'Courier New', 'SF Mono', 'Consolas', monospace;
    }
    
    .main {
        background-color: #0d1117;
    }
    
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stMetric, .stAlert {
        font-family: 'Courier New', 'SF Mono', 'Consolas', monospace !important;
        color: #c9d1d9 !important;
    }
    
    .stSidebar {
        background-color: #161b22;
        font-family: 'Courier New', 'SF Mono', 'Consolas', monospace;
    }
    
    .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar .stNumberInput, .stSidebar .stSlider {
        color: #c9d1d9;
    }
    
    .stButton > button {
        font-family: 'Courier New', monospace;
        background-color: #238636;
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        background-color: #2ea043;
    }
    
    .stAlert {
        background-color: #161b22;
        border-left: 3px solid #f0883e;
    }
    
    .stMetric label {
        color: #8b949e !important;
    }
    
    .stMetric .stMetricValue {
        color: #c9d1d9 !important;
    }
    
    .stSelectbox, .stNumberInput, .stSlider {
        background-color: #0d1117;
    }
    
    hr {
        border-color: #30363d;
    }
    
    code, pre {
        background-color: #161b22;
        color: #c9d1d9;
        font-family: 'Courier New', monospace;
    }
    
    .stExpander {
        background-color: #161b22;
        border: 1px solid #30363d;
    }
    
    .stInfo {
        background-color: #161b22;
        border-left: 3px solid #58a6ff;
    }
    
    .stSuccess {
        background-color: #161b22;
        border-left: 3px solid #2ea043;
    }
    
    .stWarning {
        background-color: #161b22;
        border-left: 3px solid #d29922;
    }
    
    .stError {
        background-color: #161b22;
        border-left: 3px solid #f85149;
    }
</style>
""", unsafe_allow_html=True)

st.title("simulador_de_tanque")
st.markdown("tanque con descarga gravitatoria")
st.markdown("---")

with st.sidebar:
    st.markdown("## datos_geometricos")
    D = st.number_input("diametro D (m)", value=1.0, min_value=0.3, max_value=5.0, step=0.05)
    A = np.pi * (D/2)**2
    st.caption(f"area calculada: {A:.4f} m²")
    
    L0 = st.number_input("nivel inicial L0 (m)", value=1.0, min_value=0.0, max_value=5.0, step=0.05)
    L_max = st.number_input("nivel maximo L_max (m)", value=2.0, min_value=0.5, max_value=10.0, step=0.1)
    
    st.markdown("## datos_operacion")
    F0 = st.number_input("caudal entrada F0 (m³/s)", value=0.002, min_value=0.0001, max_value=0.1, format="%.5f")
    x0 = st.slider("apertura inicial x0", 0.0, 1.0, 0.5, 0.01)
    xf = st.slider("apertura final xf", 0.0, 1.0, 0.25, 0.01)
    
    st.markdown("## datos_fluido")
    rho = st.number_input("densidad rho (kg/m³)", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
    g = 9.81
    st.caption(f"gravedad fija: g = {g} m/s²")
    
    st.markdown("## caracteristica_valvula")
    tipo_valvula = st.selectbox(
        "tipo",
        ["lineal", "isoporcentual", "apertura_rapida"]
    )
    
    R = 50
    if tipo_valvula == "isoporcentual":
        R = st.slider("relacion_rango R", 20, 100, 50, 5)
    
    st.markdown("## simulacion")
    t_final = st.slider("tiempo_simulacion (s)", 100, 2000, 1100, 100)

def f_apertura(x, tipo, R):
    x = max(0.0, min(1.0, x))
    
    if tipo == "lineal":
        return x
    elif tipo == "isoporcentual":
        return R**(x-1)
    elif tipo == "apertura_rapida":
        return 1 - (1-x)**2
    else:
        return x

f0 = f_apertura(x0, tipo_valvula, R)
Cv_max = F0 / (f0 * np.sqrt(rho * g * L0))

st.markdown("## parametros_calculados")
col_a, col_b = st.columns(2)
with col_a:
    st.metric("area_tanque_A", f"{A:.4f} m²")
    st.metric("Cv_max", f"{Cv_max:.3e}")
with col_b:
    st.metric("caudal_entrada_F0", f"{F0:.5f} m³/s = {F0*1000:.2f} L/s")
    st.metric("nivel_inicial_L0", f"{L0:.2f} m")

def caudal_salida(L, x):
    f = f_apertura(x, tipo_valvula, R)
    return Cv_max * f * np.sqrt(rho * g * np.maximum(L, 0.001))

def modelo_dinamico(X, t, F0, A, x):
    L = X[0]
    F = caudal_salida(L, x)
    dLdt = (F0 - F) / A
    return [dLdt]

st.markdown("## analisis_estacionario")
L_ss_inicial = (F0/(Cv_max * f_apertura(x0, tipo_valvula, R)))**2/(rho*g) if x0 > 0 and f_apertura(x0, tipo_valvula, R) > 0 else np.inf
L_ss_final = (F0/(Cv_max * f_apertura(xf, tipo_valvula, R)))**2/(rho*g) if xf > 0 and f_apertura(xf, tipo_valvula, R) > 0 else np.inf

col1, col2 = st.columns(2)
with col1:
    st.info(f"apertura x = {x0:.3f} (inicial)")
    st.write(f"nivel_estacionario: {L_ss_inicial:.2f} m")
    st.write(f"{'no_rebalsa' if L_ss_inicial <= L_max else 'rebalsa'}")
with col2:
    st.info(f"apertura x = {xf:.3f} (final)")
    st.write(f"nivel_estacionario: {L_ss_final:.2f} m")
    st.write(f"{'no_rebalsa' if L_ss_final <= L_max else 'rebalsa'}")

x_min = F0/(Cv_max * np.sqrt(rho * g * L_max))
st.metric("apertura_minima_segura", f"{x_min:.4f}", delta=f"actual: {xf:.4f}")

if xf < x_min:
    st.warning("alerta: apertura final menor que minima. tanque rebalsara.")
else:
    st.success("apertura final mayor que minima. operacion segura.")

x_vals = np.linspace(0, 1, 100)
if tipo_valvula == "lineal":
    f_vals = [f_apertura(x, "lineal", R) for x in x_vals]
elif tipo_valvula == "isoporcentual":
    f_vals = [f_apertura(x, "isoporcentual", R) for x in x_vals]
else:
    f_vals = [f_apertura(x, "apertura_rapida", R) for x in x_vals]

fig_valv, ax_valv = plt.subplots(figsize=(8, 5))
ax_valv.plot(x_vals, f_vals, 'b-', linewidth=2)
ax_valv.plot(x0, f_apertura(x0, tipo_valvula, R), 'ro', markersize=8, label=f'x0={x0:.2f}')
ax_valv.set_xlabel("apertura x")
ax_valv.set_ylabel("flujo normalizado f(x)")
ax_valv.set_title(f"caracteristica_valvula: {tipo_valvula}")
ax_valv.grid(True, alpha=0.3)
ax_valv.legend()
ax_valv.set_facecolor('#0d1117')
fig_valv.patch.set_facecolor('#0d1117')
ax_valv.tick_params(colors='#c9d1d9')
ax_valv.spines['bottom'].set_color('#c9d1d9')
ax_valv.spines['top'].set_color('#c9d1d9')
ax_valv.spines['left'].set_color('#c9d1d9')
ax_valv.spines['right'].set_color('#c9d1d9')
ax_valv.xaxis.label.set_color('#c9d1d9')
ax_valv.yaxis.label.set_color('#c9d1d9')
ax_valv.title.set_color('#c9d1d9')
st.pyplot(fig_valv)

st.markdown("## simulacion_dinamica")
t = np.linspace(0, t_final, 1000)
X0 = [L0]
sol = odeint(modelo_dinamico, X0, t, args=(F0, A, xf))
L = sol[:, 0]
F = caudal_salida(L, xf)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(t, L, 'b-', linewidth=2)
ax1.axhline(y=L_max, color='r', linestyle='--', label=f'L_max = {L_max} m')
ax1.axhline(y=L0, color='gray', linestyle=':', alpha=0.5, label=f'L0 = {L0} m')
ax1.set_xlabel("tiempo (s)")
ax1.set_ylabel("nivel L (m)")
ax1.set_title("evolucion del nivel")
ax1.grid(True, alpha=0.3)
ax1.legend()
ax2.plot(t, np.ones_like(t)*F0, 'g--', linewidth=2, label=f'F0 = {F0:.5f} m³/s')
ax2.plot(t, F, 'r-', linewidth=2, label='F_salida')
ax2.set_xlabel("tiempo (s)")
ax2.set_ylabel("caudal (m³/s)")
ax2.set_title("caudales")
ax2.grid(True, alpha=0.3)
ax2.legend()

for ax in [ax1, ax2]:
    ax.set_facecolor('#0d1117')
    ax.tick_params(colors='#c9d1d9')
    ax.spines['bottom'].set_color('#c9d1d9')
    ax.spines['top'].set_color('#c9d1d9')
    ax.spines['left'].set_color('#c9d1d9')
    ax.spines['right'].set_color('#c9d1d9')
    ax.xaxis.label.set_color('#c9d1d9')
    ax.yaxis.label.set_color('#c9d1d9')
    ax.title.set_color('#c9d1d9')
    ax.legend(loc='best', facecolor='#161b22', edgecolor='#30363d', labelcolor='#c9d1d9')

fig.patch.set_facecolor('#0d1117')
plt.tight_layout()
st.pyplot(fig)

st.markdown("## informe_operario")
L_final = L[-1]
tiempo_rebalse = None
for i, nivel in enumerate(L):
    if nivel >= L_max:
        tiempo_rebalse = t[i]
        break

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("nivel_final", f"{L_final:.3f} m", delta=f"{L_final - L0:.3f} m")
with col_r2:
    st.metric("caudal_salida_final", f"{F[-1]:.5f} m³/s")
with col_r3:
    st.metric("error_estacionario", f"{abs(F0 - F[-1]):.6f} m³/s")

if tiempo_rebalse:
    st.error(f"rebalse_detectado: nivel {L_max} m alcanzado a los {tiempo_rebalse:.1f} s")
else:
    st.success(f"sin_rebalse en {t_final} s. nivel_maximo: {max(L):.3f} m")

st.markdown("## recomendacion")
if xf < x_min:
    st.markdown(f"""
    situacion_actual:
    - valvula en x = {xf:.3f}
    - apertura_minima_segura: x_min = {x_min:.3f}
    
    recomendacion: abrir valvula a x = {x_min:.3f}
    """)
else:
    st.markdown(f"""
    situacion_actual:
    - valvula en x = {xf:.3f}
    - apertura_minima_segura: x_min = {x_min:.3f}
    
    resultado: operacion segura
    """)

with st.expander("modelo_matematico"):
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    st.markdown("""
    variables:
    - A = area (m²)
    - L = nivel (m)
    - F0 = caudal entrada (m³/s)
    - f(x) = funcion valvula
    - Cv_max = coeficiente valvula
    - rho = densidad (kg/m³)
    - g = gravedad (m/s²)
    """)
