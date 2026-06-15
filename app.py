= st.number_input("Densidad del fluido rho (kg/m³)", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
    g = 9.81
    st.caption(f"Gravedad fija: g = {g} m/s²")
    
    st.header("Caracteristica de la Valvula")
    tipo_valvula = st.selectbox(
        "Tipo de caracteristica",
        ["Lineal", "Igual porcentaje (isoporcentual)", "Apertura rapida (quick opening)"]
    )
    
    R = 50
    if tipo_valvula == "Igual porcentaje (isoporcentual)":
        R = st.slider("Relacion de rango R (tipico 20-50)", 20, 100, 50, 5)
    
    st.header("Parametros de Simulacion")
    t_final = st.slider("Tiempo de simulacion (s)", 100, 2000, 1100, 100)

def f_apertura(x, tipo, R):
    x = max(0.0, min(1.0, x))
    
    if tipo == "Lineal":
        return x
    elif tipo == "Igual porcentaje (isoporcentual)":
        return R**(x-1)
    elif tipo == "Apertura rapida (quick opening)":
        return 1 - (1-x)**2
    else:
        return x

f0 = f_apertura(x0, tipo_valvula, R)
Cv_max = F0 / (f0 * np.sqrt(rho * g * L0))

st.subheader("Parametros Calculados")
col_a, col_b = st.columns(2)
with col_a:
    st.metric("Area del tanque A", f"{A:.4f} m²")
    st.metric("Cv maximo (valvula totalmente abierta)", f"{Cv_max:.3e}")
with col_b:
    st.metric("Caudal de entrada F0", f"{F0:.5f} m³/s = {F0*1000:.2f} L/s")
    st.metric("Nivel inicial L0", f"{L0:.2f} m")

def caudal_salida(L, x):
    f = f_apertura(x, tipo_valvula, R)
    return Cv_max * f * np.sqrt(rho * g * np.maximum(L, 0.001))

def modelo_dinamico(X, t, F0, A, x):
    L = X[0]
    F = caudal_salida(L, x)
    dLdt = (F0 - F) / A
    return [dLdt]

st.subheader("Analisis Estacionario")
L_ss_inicial = (F0/(Cv_max * f_apertura(x0, tipo_valvula, R)))**2/(rho*g) if x0 > 0 and f_apertura(x0, tipo_valvula, R) > 0 else np.inf
L_ss_final = (F0/(Cv_max * f_apertura(xf, tipo_valvula, R)))**2/(rho*g) if xf > 0 and f_apertura(xf, tipo_valvula, R) > 0 else np.inf

col1, col2 = st.columns(2)
with col1:
    st.info(f"Con apertura x = {x0:.3f} (inicial)")
    st.write(f"Nivel estacionario: {L_ss_inicial:.2f} m")
    st.write(f"{'No rebalsa' if L_ss_inicial <= L_max else 'Rebalsa'}")
with col2:
    st.info(f"Con apertura x = {xf:.3f} (final)")
    st.write(f"Nivel estacionario: {L_ss_final:.2f} m")
    st.write(f"{'No rebalsa' if L_ss_final <= L_max else 'Rebalsa'}")

x_min = F0/(Cv_max * np.sqrt(rho * g * L_max))
st.metric("Apertura minima para no rebalsar", f"{x_min:.4f}", delta=f"Actual (final): {xf:.4f}")

if xf < x_min:
    st.warning("Alerta: La apertura final es menor que la apertura minima. El tanque va a rebalsar.")
else:
    st.success("La apertura final es mayor o igual a la minima. Operacion segura.")

x_vals = np.linspace(0, 1, 100)
f_lineal = [f_apertura(x, "Lineal", R) for x in x_vals]
f_isoporc = [f_apertura(x, "Igual porcentaje (isoporcentual)", R) for x in x_vals]
f_rapida = [f_apertura(x, "Apertura rapida (quick opening)", R) for x in x_vals]

fig_valv, ax_valv = plt.subplots(figsize=(8, 5))
ax_valv.plot(x_vals, f_lineal, 'b-', label='Lineal', linewidth=2)
ax_valv.plot(x_vals, f_isoporc, 'r-', label=f'Isoporcentual (R={R})', linewidth=2)
ax_valv.plot(x_vals, f_rapida, 'g-', label='Apertura rapida', linewidth=2)
ax_valv.plot(x0, f_apertura(x0, tipo_valvula, R), 'ko', markersize=8, label=f'Punto operacion (x0={x0:.2f})')
ax_valv.set_xlabel("Apertura x")
ax_valv.set_ylabel("Flujo normalizado f(x)")
ax_valv.set_title("Caracteristicas inherentes de valvulas de control")
ax_valv.grid(True, alpha=0.3)
ax_valv.legend()
st.pyplot(fig_valv)

st.subheader("Simulacion Dinamica")
t = np.linspace(0, t_final, 1000)
X0 = [L0]
sol = odeint(modelo_dinamico, X0, t, args=(F0, A, xf))
L = sol[:, 0]
F = caudal_salida(L, xf)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(t, L, 'b-', linewidth=2)
ax1.axhline(y=L_max, color='r', linestyle='--', label=f'L_max = {L_max} m')
ax1.axhline(y=L0, color='gray', linestyle=':', alpha=0.5, label=f'L0 = {L0} m')
ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Nivel L (m)")
ax1.set_title("Evolucion del nivel del tanque")
ax1.grid(True, alpha=0.3)
ax1.legend()
ax2.plot(t, np.ones_like(t)*F0, 'g--', linewidth=2, label=f'F0 = {F0:.5f} m³/s')
ax2.plot(t, F, 'r-', linewidth=2, label='F (salida)')
ax2.set_xlabel("Tiempo (s)")
ax2.set_ylabel("Caudal (m³/s)")
ax2.set_title("Caudales de entrada y salida")
ax2.grid(True, alpha=0.3)
ax2.legend()
plt.tight_layout()
st.pyplot(fig)

st.subheader("Informe para el Operario")
L_final = L[-1]
tiempo_rebalse = None
for i, nivel in enumerate(L):
    if nivel >= L_max:
        tiempo_rebalse = t[i]
        break

col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.metric("Nivel final", f"{L_final:.3f} m", delta=f"{L_final - L0:.3f} m")
with col_r2:
    st.metric("Caudal salida final", f"{F[-1]:.5f} m³/s")
with col_r3:
    st.metric("Error estacionario", f"{abs(F0 - F[-1]):.6f} m³/s")

if tiempo_rebalse:
    st.error(f"Rebalse detectado: El tanque alcanza el nivel maximo de {L_max} m a los {tiempo_rebalse:.1f} segundos.")
else:
    st.success(f"Sin rebalse durante los {t_final} s de simulacion. Nivel maximo: {max(L):.3f} m")

st.subheader("Recomendacion")
if xf < x_min:
    st.markdown(f"""
    Situacion actual:
    - Valvula cerrada a x = {xf:.3f}
    - Apertura minima segura: x_min = {x_min:.3f}
    
    Recomendacion:
    Abrir la valvula al menos a x = {x_min:.3f} para evitar el rebalse.
    """)
else:
    st.markdown(f"""
    Situacion actual:
    - Valvula en x = {xf:.3f} (mayor a x_min = {x_min:.3f})
    
    Resultado: Operacion segura. El tanque no rebalsara.
    """)

with st.expander("Ver detalles del modelo matematico"):
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    st.markdown("""
    Donde:
    - A = area del tanque (m²)
    - L = nivel del liquido (m)
    - F0 = caudal de entrada (m³/s)
    - f(x) = funcion de caracteristica de la valvula (0 a 1)
    - Cv_max = coeficiente de valvula a maxima apertura
    - rho = densidad del fluido (kg/m³)
    - g = gravedad (m/s²)
    """)
