import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.title("🧪 Simulación: Tanque con Descarga Gravitatoria")
st.markdown("Ajustá los parámetros y observá la respuesta del nivel del tanque")

# Parámetros ajustables
col1, col2 = st.columns(2)
with col1:
    Qe = st.slider("Caudal de entrada Qe (m³/s)", 0.01, 0.1, 0.02, 0.005)
    k = st.slider("Coeficiente de descarga k", 0.01, 0.1, 0.05, 0.01)
with col2:
    H0 = st.slider("Altura inicial H₀ (m)", 0.1, 1.0, 0.5, 0.05)
    A = st.slider("Área del tanque A (m²)", 0.5, 2.0, 1.0, 0.1)

# Modelo de la dinámica
def modelo(H, t, Qe, A, k):
    g = 9.81
    Qs = k * np.sqrt(2 * g * max(H[0], 0.001))
    dHdt = (Qe - Qs) / A
    return [dHdt]

# Simulación
t = np.linspace(0, 200, 500)
H = odeint(modelo, [H0], t, args=(Qe, A, k))

# Gráfico
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(t, H, 'b-', linewidth=2)
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Altura H (m)")
ax.set_title("Evolución del nivel del tanque")
ax.grid(True, alpha=0.3)
st.pyplot(fig)

st.info("💡 **Ecuación de descarga:** Qs = k·√(2gH) → ¡comportamiento no lineal!")