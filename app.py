import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulador de Tanque Gravitatorio", layout="wide")

st.title("Simulador de Tanque con Descarga Gravitatoria")
st.markdown("---")

with st.sidebar:
    st.header("Datos Geometricos del Tanque")
    D = st.number_input("Diametro del tanque D (m)", value=1.0, min_value=0.3, max_value=5.0, step=0.05)
    A = np.pi * (D/2)**2
    st.caption(f"Area calculada: {A:.4f} m²")
    
    L0 = st.number_input("Nivel inicial L0 (m)", value=1.0, min_value=0.0, max_value=5.0, step=0.05)
    L_max = st.number_input("Nivel maximo (rebalse) L_max (m)", value=2.0, min_value=0.5, max_value=10.0, step=0.1)
    
    st.header("Datos de Operacion")
    F0 = st.number_input("Caudal de entrada F0 (m³/s)", value=0.002, min_value=0.0001, max_value=0.1, format="%.5f")
    x0 = st.slider("Apertura inicial de valvula x0", 0.0, 1.0, 0.5, 0.01)
    xf = st.slider("Apertura final de valvula xf", 0.0, 1.0, 0.25, 0.01)
    
    st.header("Datos del Fluido")
    rho = st.number_input("Densidad del fluido rho (kg/m³)", value=1000.0, min_value=500.0, max_value=2000.0, step=10.0)
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

st.markdown("---")
st.subheader("Documentacion del Modelo")

with st.expander("Modelo Conceptual"):
    st.markdown("### 1. Modelo Dinamico")
    st.markdown("""
    El balance de masa en el tanque da lugar a la siguiente ecuacion diferencial ordinaria (ODE):
    """)
    st.latex(r"A \frac{dL}{dt} = F_0 - F")
    st.markdown("""
    Donde el caudal de salida por gravedad se modela con la siguiente ecuacion algebraica (AE):
    """)
    st.latex(r"F = C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.markdown("""
    Combinando ambas ecuaciones:
    """)
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    
    st.markdown("### 2. Modelo Estacionario")
    st.markdown("""
    En estado estacionario, la derivada temporal es cero (dL/dt = 0):
    """)
    st.latex(r"F_0 = C_v \cdot f(x) \cdot \sqrt{\rho g L_{ss}}")
    st.markdown("""
    Despejando el nivel estacionario:
    """)
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    
    st.markdown("### Variables del Modelo")
    st.markdown("""
    | Simbolo | Descripcion | Unidad |
    |---------|-------------|--------|
    | A | Area transversal del tanque | m² |
    | L | Nivel del liquido | m |
    | F0 | Caudal de entrada | m³/s |
    | F | Caudal de salida | m³/s |
    | Cv | Coeficiente de valvula | - |
    | f(x) | Caracteristica de valvula | - |
    | rho | Densidad del fluido | kg/m³ |
    | g | Gravedad | m/s² |
    | x | Apertura de valvula | - |
    """)

with st.expander("Modelo en Octave"):
    st.markdown("""
    Codigo autocontenido para simular el tanque en Octave.
    Para utilizarlo:
    1. Copiar el codigo
    2. Guardarlo en un archivo con extension .m
    3. Ejecutarlo en Octave
    """)
    
    codigo_octave = '''% Simulador de Tanque con Descarga Gravitatoria
% Modelo dinamico y estacionario
% Compatible con Octave

clear all; close all; clc;

% =============== PARAMETROS DEL SISTEMA ===============

% Geometria del tanque
D = 1.0;                % Diametro (m)
A = pi * (D/2)^2;       % Area (m²)
L0 = 1.0;               % Nivel inicial (m)
L_max = 2.0;            % Nivel maximo (rebalse) (m)

% Operacion
F0 = 2e-3;              % Caudal de entrada (m³/s)
x0 = 0.5;               % Apertura inicial de valvula
xf = 0.25;              % Apertura final de valvula

% Fluido
rho = 1000;             % Densidad (kg/m³)
g = 9.81;               % Gravedad (m/s²)

% Valvula
tipo_valvula = "lineal";  % Opciones: "lineal", "isoporcentual", "apertura_rapida"
R = 50;                   % Relacion de rango (para isoporcentual)

% Simulacion
t_final = 1100;         % Tiempo final (s)

% =============== FUNCIONES DEL MODELO ===============

% Funcion de apertura de valvula
function f = f_apertura(x, tipo, R)
    if strcmp(tipo, "lineal")
        f = x;
    elseif strcmp(tipo, "isoporcentual")
        f = R^(x-1);
    elseif strcmp(tipo, "apertura_rapida")
        f = 1 - (1-x)^2;
    else
        f = x;
    endif
endfunction

% Caudal de salida
function F = caudal_salida(L, x, Cv_max, tipo, R, rho, g)
    f = f_apertura(x, tipo, R);
    L_seguro = max(L, 0.001);
    F = Cv_max * f * sqrt(rho * g * L_seguro);
endfunction

% =============== CALCULO DE PARAMETROS DERIVADOS ===============

f0 = f_apertura(x0, tipo_valvula, R);
Cv_max = F0 / (f0 * sqrt(rho * g * L0));

% =============== DEFINICION DE LA ODE PARA LSODE ===============

global params
params.F0 = F0;
params.A = A;
params.xf = xf;
params.Cv_max = Cv_max;
params.tipo = tipo_valvula;
params.R = R;
params.rho = rho;
params.g = g;

function dLdt = modelo_tanque(L, t)
    global params
    F = caudal_salida(L, params.xf, params.Cv_max, params.tipo, params.R, params.rho, params.g);
    dLdt = (params.F0 - F) / params.A;
endfunction

% =============== ANALISIS ESTACIONARIO ===============

f_final = f_apertura(xf, tipo_valvula, R);
L_ss = (F0 / (Cv_max * f_final))^2 / (rho * g);

fprintf("\n========== ANALISIS ESTACIONARIO ==========\n");
fprintf("Apertura final de valvula: xf = %.3f\n", xf);
fprintf("Nivel estacionario teorico: L_ss = %.2f m\n", L_ss);
fprintf("Nivel maximo permitido: L_max = %.2f m\n", L_max);

if L_ss > L_max
    fprintf("Resultado: El tanque REBALSARA en estado estacionario\n");
else
    fprintf("Resultado: El tanque NO rebalsara en estado estacionario\n");
endif

x_min = F0 / (Cv_max * sqrt(rho * g * L_max));
fprintf("\nApertura minima para no rebalsar: x_min = %.4f\n", x_min);

if xf < x_min
    fprintf("ALERTA: La apertura actual (%.4f) es menor que la minima segura (%.4f)\n", xf, x_min);
else
    fprintf("OK: La apertura actual (%.4f) es mayor o igual que la minima segura (%.4f)\n", xf, x_min);
endif

% =============== SIMULACION DINAMICA ===============

t = linspace(0, t_final, 1000);
L = lsode(@modelo_tanque, L0, t);

for i = 1:length(L)
    F(i) = caudal_salida(L(i), xf, Cv_max, tipo_valvula, R, rho, g);
endfor

% =============== GRAFICOS ===============

figure('Position', [100, 100, 1000, 450]);

subplot(1,2,1);
plot(t, L, 'b-', 'LineWidth', 2);
hold on;
plot([t(1), t(end)], [L_max, L_max], 'r--', 'LineWidth', 1.5);
plot([t(1), t(end)], [L0, L0], 'k:', 'LineWidth', 1);
xlabel('Tiempo (s)');
ylabel('Nivel L (m)');
title('Evolucion del nivel del tanque');
grid on;
legend('L(t)', 'L_{max}', 'L_0', 'Location', 'northeast');

subplot(1,2,2);
plot(t, F, 'r-', 'LineWidth', 2);
hold on;
plot([t(1), t(end)], [F0, F0], 'g--', 'LineWidth', 1.5);
xlabel('Tiempo (s)');
ylabel('Caudal (m³/s)');
title('Caudales de entrada y salida');
grid on;
legend('F_{salida}', 'F_{entrada}', 'Location', 'northeast');

% =============== DETECCION DE REBALSE ===============

tiempo_rebalse = [];
for i = 1:length(L)
    if L(i) >= L_max
        tiempo_rebalse = t(i);
        break;
    endif
endfor

fprintf("\n========== SIMULACION DINAMICA ==========\n");
fprintf("Nivel final simulado: L_final = %.3f m\n", L(end));
fprintf("Nivel maximo alcanzado: L_max_sim = %.3f m\n", max(L));

if ~isempty(tiempo_rebalse)
    fprintf("REBALSE DETECTADO: El tanque alcanza L_max = %.2f m en t = %.1f s\n", L_max, tiempo_rebalse);
else
    fprintf("NO HAY REBALSE durante los %.0f s de simulacion\n", t_final);
endif

% =============== RESUMEN PARA EL OPERARIO ===============

fprintf("\n========== RESUMEN PARA EL OPERARIO ==========\n");
fprintf("Caudal de entrada: F0 = %.5f m³/s (%.2f L/s)\n", F0, F0*1000);
fprintf("Area del tanque: A = %.4f m²\n", A);
fprintf("Coeficiente de valvula: Cv_max = %.3e\n", Cv_max);
fprintf("\nRECOMENDACION:\n");
if xf < x_min
    fprintf("Abrir la valvula al menos a x = %.4f para evitar el rebalse.\n", x_min);
else
    fprintf("Operacion segura. Mantener la valvula en x = %.3f o superior.\n", x_min);
endif
'''
    
    st.code(codigo_octave, language="octave")
    
    st.download_button(
        label="Descargar modelo_tanque.m",
        data=codigo_octave,
        file_name="modelo_tanque.m",
        mime="text/plain"
    )

with st.expander("Ecuaciones del Modelo Matematico"):
    st.latex(r"A \frac{dL}{dt} = F_0 - C_v \cdot f(x) \cdot \sqrt{\rho g L}")
    st.latex(r"L_{ss} = \frac{1}{\rho g} \left( \frac{F_0}{C_v \cdot f(x)} \right)^2")
    st.markdown("""
    **Variables:**
    - A = area del tanque (m²)
    - L = nivel del liquido (m)
    - F0 = caudal de entrada (m³/s)
    - f(x) = funcion de caracteristica de la valvula
    - Cv_max = coeficiente de valvula a maxima apertura
    - rho = densidad del fluido (kg/m³)
    - g = gravedad (m/s²)
    - x = apertura de la valvula
    """)
