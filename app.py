# app.py - Tanque con descarga gravitatoria (versión mejorada)
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Tanque Gravitatorio", layout="wide")
st.title("🧪 Tanque con descarga gravitatoria")
st.markdown("**Parámetros obtenidos del análisis en estado estacionario**")

# ============================================================
# PARÁMETROS (obtenidos de tu análisis estacionario)
# ============================================================
rho = 1000      # densidad del agua (kg/m³)
g = 9.81        # gravedad (m/s²)
Cv = 4.039E-5   # coeficiente de válvula

# Parámetros editables por el usuario
st.sidebar.header("⚙️ Parámetros del sistema")

A = st.sidebar.number_input("Área del tanque A (m²)", value=0.785, min_value=0.2, max_value=2.0, step=0.01)
F0 = st.sidebar.number_input("Caudal de entrada F0 (m³/s)", value=2e-3, min_value=0.5e-3, max_value=5e-3, format="%.5f")
L0 = st.sidebar.number_input("Nivel inicial L₀ (m)", value=1.0, min_value=0.0, max_value=2.0, step=0.05)
x = st.sidebar.slider("Apertura de válvula x (0=cerrada, 1=abierta)", 0.0, 1.0, 0.25, 0.01)
t_final = st.sidebar.slider("Tiempo de simulación (s)", 100, 2000, 1100, 100)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**📊 Parámetros fijos:**  
- ρ = {rho} kg/m³  
- g = {g} m/s²  
- Cv = {Cv:.2e}
""")

# ============================================================
# FUNCIONES DEL MODELO
# ============================================================
def AEs(L, x):
    """Ecuación algebraica: caudal de salida F"""
    return Cv * x * np.sqrt(rho * g * max(L, 0.001))

def ODEs(X, t, F0, A, x):
    """Ecuación diferencial: dL/dt = (F0 - F)/A"""
    L = X[0]
    F = AEs(L, x)
    dL = (F0 - F) / A
    return [dL]

# ============================================================
# SIMULACIÓN
# ============================================================
t = np.linspace(0, t_final, 500)
X0 = [L0]
sol = odeint(ODEs, X0, t, args=(F0, A, x))
L = sol[:, 0]

# Calcular caudal de salida
F = Cv * x * np.sqrt(rho * g * np.maximum(L, 0.001))

# ============================================================
# GRÁFICOS
# ============================================================
st.subheader("📈 Resultados de la simulación")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Nivel vs tiempo
ax1.plot(t, L, 'b-', linewidth=2)
ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Nivel L (m)")
ax1.set_title("Nivel del tanque")
ax1.grid(True, alpha=0.3)
ax1.axhline(y=L0, color='gray', linestyle='--', alpha=0.5, label=f'L₀ = {L0:.2f} m')
ax1.legend()

# Gráfico 2: Caudales vs tiempo
ax2.plot(t, np.ones_like(t)*F0, 'g--', linewidth=2, label=f'F₀ (entrada) = {F0:.5f} m³/s')
ax2.plot(t, F, 'r-', linewidth=2, label='F (salida)')
ax2.set_xlabel("Tiempo (s)")
ax2.set_ylabel("Caudal (m³/s)")
ax2.set_title("Caudales de entrada y salida")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
st.pyplot(fig)

# ============================================================
# ANÁLISIS DE RESULTADOS
# ============================================================
st.subheader("📊 Análisis")

col1, col2, col3 = st.columns(3)

with col1:
    L_final = L[-1]
    st.metric("Nivel final", f"{L_final:.3f} m", delta=f"{L_final - L0:.3f} m")

with col2:
    F_final = F[-1]
    st.metric("Caudal salida final", f"{F_final:.5f} m³/s")

with col3:
    error = abs(F0 - F_final)
    st.metric("Error estacionario", f"{error:.6f} m³/s")

# Verificar rebalse
L_max = 2.0
if max(L) > L_max:
    st.error(f"⚠️ ¡El tanque rebalsó! Nivel máximo: {max(L):.3f} m")
else:
    st.success(f"✅ El tanque NO rebalsa. Nivel máximo: {max(L):.3f} m")

# Estado estacionario teórico
if x > 0:
    L_eq = (F0/(Cv*x))**2/(rho*g)
    st.info(f"""
    **🔬 Análisis estacionario (teórico):**
    
    - Caudal de entrada F₀ = {F0:.5f} m³/s
    - En equilibrio: F = F₀ → L_eq = (F₀/(Cv·x))²/(ρ·g) = **{L_eq:.3f} m**
    - El nivel final simulado es **{L_final:.3f} m**
    - Diferencia: **{abs(L_eq - L_final):.4f} m**
    """)
else:
    st.warning("⚠️ Válvula cerrada (x=0). No hay caudal de salida.")
