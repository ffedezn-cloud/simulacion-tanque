import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulador de Tanque Gravitatorio", layout="wide")

st.title("Simulador de Tanque con Descarga Gravitatoria")
# ====== IMAGEN DEL PROCESO  ======
st.markdown(
    f'''
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/ffedezn-cloud/simulacion-tanque/main/diagrama_tanque.png" 
             alt="Esquema del tanque" 
             style="width: 70%; max-width: 700px; border: 1px solid #ddd; border-radius: 8px;">
        <p style="font-size: 13px; color: #888; margin-top: 4px;">Esquema del tanque con descarga gravitatoria</p>
    </div>
    ''',
    unsafe_allow_html=True
)
st.markdown("---")

with st.sidebar:
       # ===== INFORMACIÓN DEL DESARROLLADOR =====
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0;">
            <p style="font-size: 0.75rem; color: #6c6c8a; margin-bottom: 2px;">
                <strong>Federico Franco</strong>
            </p>
            <p style="font-size: 0.7rem; color: #8a8aaa; margin-bottom: 2px;">
                Ingeniería Química
            </p>
            <a href="mailto:tu.email@gmail.com" 
               style="font-size: 0.7rem; color: #6c6c8a; text-decoration: none;">
                📧 ffede.zn@gmail.com
            </a>
            <br>
            <a href="https://www.linkedin.com/in/fede-franco-70a301418/" 
               target="_blank"
               style="font-size: 0.7rem; color: #6c6c8a; text-decoration: none;">
                🔗 LinkedIn
            </a>
            <br>
            <a href="https://github.com/ffedezn-cloud" 
               target="_blank"
               style="font-size: 0.7rem; color: #6c6c8a; text-decoration: none;">
                🐙 GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
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
% Tanque con descarga gravitatoria
% Curva característica de la válvula: lineal
% En X estan las variables de estado.
% En Y estan las variables que se requieren en las ODEs o que se quieren graficar.

clear all; close all; clc;

disp('Simulador de Tanque con Descarga Gravitatoria');
disp('');

% =============== MODELO =================

% ODEs
function dX = ODEs(t, X)
    % En dX devuelve el vector columna de derivadas
    
    % Recupera variables X
    [L] = num2cell(X'){1,:};
    
    % Recupera variables Y
    Y = AEs(t, X);
    [A, F0, F] = num2cell(Y){1,:};
    
    % Ecuaciones diferenciales
    dL = (F0 - F) / A;
    
    dX = [dL]'; % vector columna
endfunction

% AEs
function Y = AEs(t, X)
    % En Y devuelve el vector fila de variables requeridas por ODEs o a graficar.
    
    % Recupera variables X
    [L] = num2cell(X'){1,:};
    
    % Parametros
    F0 = 2e-3;          % Caudal de entrada (m³/s)
    A = 0.785;          % Area del tanque (m²)
    Cv = 4.039e-5;      % Coeficiente de valvula
    rho = 1000;         % Densidad (kg/m³)
    g = 9.81;           % Gravedad (m/s²)
    
    % Ecuaciones algebraicas
    if t < 0
        x = 0.5;        % Apertura inicial
    else
        x = 0.25;       % Apertura final (perturbacion)
    endif
    
    F = Cv * x * sqrt(rho * g * L);
    
    Y = [A, F0, F];
endfunction

% =============== INICIALIZACION ===============

function [tfin, dt, Xini, LX, LY] = inicializacion()
    % Inicializa la simulacion
    
    % Parametros de simulacion
    tfin = 1100;        % tiempo final (s)
    dt = 10;            % paso temporal (s)
    
    % Inicializacion
    Lini = 1;           % nivel inicial (m)
    Xini = [Lini];      % variable de estado
    
    % Leyendas
    LX = {'L'};                     % variables X
    LY = {'A', 'F0', 'F'};          % variables Y
endfunction

% =============== FUNCIONES DE POST-PROCESAMIENTO ===============

function v = vector(leyenda, LX, LY, tpts, X, Y)
    % Devuelve el vector columna correspondiente a la variable leyenda.
    
    indicex = find(strcmp(LX, leyenda));
    if length(indicex) == 1
        v = X(:, indicex);
    else
        indicey = find(strcmp(LY, leyenda));
        if length(indicey) == 1
            v = Y(:, indicey);
        else
            disp(['Error: Variable "' leyenda '" no encontrada.']);
            error('Variable no encontrada');
        endif
    endif
endfunction

function graficar(LV, titulo, rotulox, rotuloy, limitesy, LX, LY, tpts, X, Y)
    % Crea una figura
    % LV: Arreglo de celdas fila con las leyendas de las variables a graficar.
    % titulo: Titulo de la figura.
    % rotulox: Rotulo para la abscisa.
    % rotuloy: Rotulo para la ordenada.
    % limitesy: Vector fila con limite inferior y superior (opcional).
    
    colores = ['r', 'g', 'b', 'c', 'm', 'y', 'k'];
    
    figure;
    hold on;
    
    for i = 1:length(LV)
        v = vector(LV{i}, LX, LY, tpts, X, Y);
        plot(tpts, v, colores(mod(i-1, length(colores)) + 1), 'LineWidth', 2);
    endfor
    
    title(titulo);
    xlabel(rotulox);
    ylabel(rotuloy);
    
    if nargin >= 5 && ~isempty(limitesy)
        ylim(limitesy);
    endif
    
    grid on;
    legend(LV, 'Location', 'northeast');
endfunction

function [tpts, X, Y] = simulacion(tfin, dt, Xini)
    % Realiza la simulacion
    
    % Resolucion temporal
    nts = ceil(tfin/dt + 1);
    tpts = linspace(0, tfin, nts)';
    
    % Resolver ODEs
    [tpts, X] = ode15s(@ODEs, tpts, Xini');
    
    % Calcular variables algebraicas
    for i = 1:size(tpts, 1)
        Y(i, :) = AEs(tpts(i), X(i, :)');
    endfor
endfunction

% =============== ANALISIS ===============

function analizar(LX, LY, tpts, X, Y)
    % Analisis de resultados
    
    % Graficos
    graficar({'L'}, 'Nivel vs. tiempo', 's', 'm', [], LX, LY, tpts, X, Y);
    graficar({'F0', 'F'}, 'Caudales vs. tiempo', 's', 'm3/s', [0, 4e-3], LX, LY, tpts, X, Y);
    
    % Deteccion de rebalse
    L_max = 2;
    Lt = vector('L', LX, LY, tpts, X, Y);
    
    fprintf('\n========== RESULTADOS ==========\n');
    fprintf('Nivel final: %.3f m\n', Lt(end));
    fprintf('Nivel maximo permitido: %.2f m\n', L_max);
    
    if Lt(end) <= L_max
        disp('El tanque NO rebalsa');
    else
        tr = interp1(Lt, tpts, L_max);
        fprintf('El tanque rebalsa en t = %.1f s\n', tr);
    endif
endfunction

% =============== SIMULACION PRINCIPAL ===============

% Inicializacion
[tfin, dt, Xini, LX, LY] = inicializacion();

% Simulacion
[tpts, X, Y] = simulacion(tfin, dt, Xini);

% Analisis y resultados
analizar(LX, LY, tpts, X, Y);

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


