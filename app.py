import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA WEB PROFESIONAL
st.set_page_config(
    page_title="AstroEngine 3D | Ingeniería Orbital y Defensa Planetaria",
    page_icon="🪐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual personalizado
st.title("🪐 AstroEngine 3D: Propulsión Planetaria y Defensa Orbital")
st.markdown("Simulador de astrodinámica de N-cuerpos, motores rotacionales de anillo y comparación de desvío de asteroides.")

# 2. BARRA LATERAL DE CONTROL (PANEL DE INGENIERÍA)
st.sidebar.header("🎛️ Centro de Control de Misión")
mision = st.sidebar.radio(
    "Selecciona el Modo de Simulación:",
    ["🚀 Misión 1: Mover Planeta (Escape Solar 3D)", "☄️ Misión 2: Defensa Planetaria (Comparativa de Desvíos)"]
)

st.sidebar.markdown("---")

# CONSTANTES DEL UNIVERSO REAL
G = 6.67430e-11
M_sol = 1.989e30
M_tierra_base = 5.972e24
UA = 1.496e11

def gravedad_3d(p1, p2, m2):
    vec = p2 - p1
    d = np.linalg.norm(vec)
    if d == 0:
        return np.zeros(3)
    return G * m2 * vec / (d**3)

# ==============================================================================
# LÓGICA MISIÓN 1: MOVER UN PLANETA POR EL UNIVERSO
# ==============================================================================
if "Misión 1" in mision:
    st.sidebar.subheader("⚙️ Parámetros del Motor Rotacional")
    fuerza_exp = st.sidebar.slider("Empuje del Motor (x10¹⁹ Newtons)", 0.5, 5.0, 2.2, 0.1)
    vel_plasma_kms = st.sidebar.slider("Velocidad del Plasma (km/s)", 5000, 40000, 15000, 1000)
    elevacion_deg = st.sidebar.slider("Ángulo de Elevación Eclíptica Z (°)", 0.0, 25.0, 8.0, 1.0)
    ancho_anillo_km = st.sidebar.slider("Ancho del Cinturón Ecuatorial (km)", 5, 150, 50, 5)

    # Cálculos de Ingeniería Estructural
    fuerza_motor = fuerza_exp * 1e19
    vel_escape_motor = vel_plasma_kms * 1000.0
    consumo_seg = fuerza_motor / vel_escape_motor
    potencia_watts = 0.5 * consumo_seg * (vel_escape_motor**2)

    radio_tierra = 6.371e6
    radio_anillo = radio_tierra + 100_000.0
    vel_contrarot = (2 * np.pi * radio_anillo) / 86164.0
    grav_anillo = 9.81 * ((radio_tierra / radio_anillo)**2)
    vel_orb_anillo = np.sqrt(grav_anillo * radio_anillo)
    tension_gpa = (1600.0 * abs(vel_orb_anillo**2 - vel_contrarot**2)) / 1e9
    presion_mpa = (fuerza_motor / ((2 * np.pi * radio_tierra) * (ancho_anillo_km * 1000.0))) / 1e6

    # Simulación Orbital 3D
    masa_t = M_tierra_base
    masa_m = 6.39e23
    masa_j = 1.898e27

    pos_t = np.array([1.0 * UA, 0.0, 0.0])
    vel_t = np.array([0.0, 29780.0, 0.0])

    inc_m = np.radians(1.85)
    pos_m = np.array([0.0, 1.524 * UA * np.cos(inc_m), 1.524 * UA * np.sin(inc_m)])
    vel_m = np.array([-24070.0, 0.0, 0.0])

    inc_j = np.radians(1.30)
    dist_j = 5.204 * UA
    vel_j_mag = 13070.0
    pos_j = np.array([-dist_j * 0.7071, dist_j * 0.7071 * np.cos(inc_j), dist_j * 0.7071 * np.sin(inc_j)])
    vel_j = np.array([-vel_j_mag * 0.7071, -vel_j_mag * 0.7071 * np.cos(inc_j), -vel_j_mag * 0.7071 * np.sin(inc_j)])

    dt = 86400
    dias = 2400
    elev_rad = np.radians(elevacion_deg)

    tx, ty, tz, mx, my, mz, jx, jy, jz = [], [], [], [], [], [], [], [], []
    dia_escape = None

    for d in range(dias):
        tx.append(pos_t[0]/UA); ty.append(pos_t[1]/UA); tz.append(pos_t[2]/UA)
        mx.append(pos_m[0]/UA); my.append(pos_m[1]/UA); mz.append(pos_m[2]/UA)
        jx.append(pos_j[0]/UA); jy.append(pos_j[1]/UA); jz.append(pos_j[2]/UA)

        rap = np.linalg.norm(vel_t)
        dist_s = np.linalg.norm(pos_t)
        if rap >= np.sqrt(2 * G * M_sol / dist_s) and dia_escape is None:
            dia_escape = d

        dir_av = vel_t / rap
        dir_emp = (dir_av * np.cos(elev_rad)) + (np.array([0.0, 0.0, 1.0]) * np.sin(elev_rad))
        dir_emp /= np.linalg.norm(dir_emp)
        acel_mot = (fuerza_motor / masa_t) * dir_emp

        acel_t = gravedad_3d(pos_t, np.zeros(3), M_sol) + gravedad_3d(pos_t, pos_m, masa_m) + gravedad_3d(pos_t, pos_j, masa_j) + acel_mot
        acel_m = gravedad_3d(pos_m, np.zeros(3), M_sol) + gravedad_3d(pos_m, pos_t, masa_t) + gravedad_3d(pos_m, pos_j, masa_j)
        acel_j = gravedad_3d(pos_j, np.zeros(3), M_sol) + gravedad_3d(pos_j, pos_t, masa_t) + gravedad_3d(pos_j, pos_m, masa_m)

        vel_t += acel_t * dt; pos_t += vel_t * dt
        vel_m += acel_m * dt; pos_m += vel_m * dt
        vel_j += acel_j * dt; pos_j += vel_j * dt
        masa_t -= consumo_seg * dt

    masa_perdida_pct = ((M_tierra_base - masa_t) / M_tierra_base) * 100

    # TARJETAS DE TELEMETRÍA SUPERIOR
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tiempo de Escape Solar", f"{dia_escape} días" if dia_escape else "No alcanzado", f"{dia_escape/365:.1f} años" if dia_escape else "Aumenta empuje")
    c2.metric("Potencia del Reactor", f"{potencia_watts:.2e} W", f"-{masa_perdida_pct:.4f}% masa")
    c3.metric("Tensión del Anillo", f"{tension_gpa:.1f} GPa", "Viable (Grafeno)" if tension_gpa <= 130 else "Colapso estructural", delta_color="normal" if tension_gpa <= 130 else "inverse")
    c4.metric("Presión Corteza", f"{presion_mpa:.1f} MPa", "Segura (<150 MPa)" if presion_mpa < 150 else "¡Riesgo Tectónico!", delta_color="normal" if presion_mpa < 150 else "inverse")

    # GRÁFICO 3D INTERACTIVO
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=14, color='yellow'), name='Sol'))
    fig.add_trace(go.Scatter3d(x=tx, y=ty, z=tz, mode='lines', line=dict(color='cyan', width=4), name='Tierra (Ruta Escape 3D)'))
    fig.add_trace(go.Scatter3d(x=mx, y=my, z=mz, mode='lines', line=dict(color='indianred', width=2, dash='dash'), name='Marte'))
    fig.add_trace(go.Scatter3d(x=jx, y=jy, z=jz, mode='lines', line=dict(color='orange', width=2, dash='dot'), name='Júpiter'))
    if dia_escape:
        fig.add_trace(go.Scatter3d(x=[tx[dia_escape]], y=[ty[dia_escape]], z=[tz[dia_escape]], mode='markers', marker=dict(size=7, color='lime', symbol='diamond'), name='Punto Escape Solar'))

    fig.update_layout(template='plotly_dark', height=650, scene=dict(aspectmode='data', xaxis_title='X (UA)', yaxis_title='Y (UA)', zaxis_title='Z (UA)'))
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# LÓGICA MISIÓN 2: DEFENSA PLANETARIA COMPARATIVA EN 3D (ASTEROIDE GIGANTE)
# ==============================================================================
else:
    st.sidebar.subheader("☄️ Parámetros de Intercepción Comparativa")
    # Rango ampliado de 10 a 1000 Millones de Toneladas para simular un asteroide masivo de clase de extinción global
    masa_ast_mt = st.sidebar.slider("Masa del Asteroide (Millones Toneladas)", 10, 1000, 350, 10)
    fuerza_desvio = st.sidebar.slider("Empuje del Motor (Newtons)", 0.0, 500.0, 150.0, 5.0)
    vel_escape_desvio_kms = st.sidebar.slider("Velocidad Escape Motor Desvío (km/s)", 10.0, 50.0, 30.0, 1.0)

    masa_asteroide = masa_ast_mt * 1e9  # kg
    dt = 86400
    dia_impacto = 300
    dias = 365

    pos_T0 = np.array([1.0 * UA, 0.0, 0.0])
    vel_T0 = np.array([0.0, 29780.0, 0.0])

    # Calcular trayectoria futura de impacto en día 300
    p_t, v_t = pos_T0.copy(), vel_T0.copy()
    for _ in range(dia_impacto):
        a_t = -G * M_sol * p_t / (np.linalg.norm(p_t)**3)
        v_t += a_t * dt; p_t += v_t * dt

    p_a = p_t.copy()
    v_a = np.array([v_t[0] * 0.85 - 8500.0, v_t[1] * 0.92, 6200.0])
    for _ in range(dia_impacto):
        a_a = -G * M_sol * p_a / (np.linalg.norm(p_a)**3)
        p_a -= v_a * dt; v_a -= a_a * dt

    # Simulación de las tres trayectorias en paralelo
    pos_T, vel_T = pos_T0.copy(), vel_T0.copy()
    pos_Asin, vel_Asin = p_a.copy(), v_a.copy()
    pos_Atan, vel_Atan = p_a.copy(), v_a.copy()
    pos_Avert, vel_Avert = p_a.copy(), v_a.copy()

    tx, ty, tz = [], [], []
    axs, ays, azs = [], [], []
    axt, ayt, azt = [], [], []
    axv, ayv, azv = [], [], []

    dist_min_sin = float("inf")
    dist_min_tan = float("inf")
    dist_min_vert = float("inf")

    for d in range(dias):
        tx.append(pos_T[0]/UA); ty.append(pos_T[1]/UA); tz.append(pos_T[2]/UA)
        axs.append(pos_Asin[0]/UA); ays.append(pos_Asin[1]/UA); azs.append(pos_Asin[2]/UA)
        axt.append(pos_Atan[0]/UA); ayt.append(pos_Atan[1]/UA); azt.append(pos_Atan[2]/UA)
        axv.append(pos_Avert[0]/UA); ayv.append(pos_Avert[1]/UA); azv.append(pos_Avert[2]/UA)

        dist_sin_km = np.linalg.norm(pos_Asin - pos_T) / 1000.0
        if dist_sin_km < dist_min_sin:
            dist_min_sin = dist_sin_km

        dist_tan_km = np.linalg.norm(pos_Atan - pos_T) / 1000.0
        if dist_tan_km < dist_min_tan:
            dist_min_tan = dist_tan_km

        dist_vert_km = np.linalg.norm(pos_Avert - pos_T) / 1000.0
        if dist_vert_km < dist_min_vert:
            dist_min_vert = dist_vert_km

        # Gravedades base
        acel_T = gravedad_3d(pos_T, np.zeros(3), M_sol)
        acel_Asin = gravedad_3d(pos_Asin, np.zeros(3), M_sol) + gravedad_3d(pos_Asin, pos_T, M_tierra_base)

        # Fuerza Tangencial
        dir_tan = vel_Atan / np.linalg.norm(vel_Atan)
        acel_mot_tan = (fuerza_desvio / masa_asteroide) * dir_tan
        acel_Atan = gravedad_3d(pos_Atan, np.zeros(3), M_sol) + gravedad_3d(pos_Atan, pos_T, M_tierra_base) + acel_mot_tan

        # Fuerza Vertical Z
        dir_vert = np.array([0.0, 0.0, 1.0])
        acel_mot_vert = (fuerza_desvio / masa_asteroide) * dir_vert
        acel_Avert = gravedad_3d(pos_Avert, np.zeros(3), M_sol) + gravedad_3d(pos_Avert, pos_T, M_tierra_base) + acel_mot_vert

        # Avances físicos
        vel_T += acel_T * dt; pos_T += vel_T * dt
        vel_Asin += acel_Asin * dt; pos_Asin += vel_Asin * dt
        vel_Atan += acel_Atan * dt; pos_Atan += vel_Atan * dt
        vel_Avert += acel_Avert * dt; pos_Avert += vel_Avert * dt

    # Diagnóstico de viabilidad
    col1, col2, col3 = st.columns(3)
    col1.metric("Opción Inercial (Sin Desvío)", f"{dist_min_sin:,.0f} km", "💥 ¡Impacto Directo!", delta_color="inverse")
    salvo_tan = dist_min_tan > 15000.0
    col2.metric("Estrategia Tangencial", f"{dist_min_tan:,.0f} km", "🛡️ Planeta Seguro" if salvo_tan else "💥 Insuficiente", delta_color="normal" if salvo_tan else "inverse")
    salvo_vert = dist_min_vert > 15000.0
    col3.metric("Estrategia Vertical Z", f"{dist_min_vert:,.0f} km", "🛡️ Planeta Seguro" if salvo_vert else "💥 Insuficiente", delta_color="normal" if salvo_vert else "inverse")

    # CÁLCULOS DE COMBUSTIBLE PARA TABLA DE COSTO-BENEFICIO
    ve_desvio_ms = vel_escape_desvio_kms * 1000.0
    consumo_seg_desvio = fuerza_desvio / ve_desvio_ms
    combustible_mision_kg = consumo_seg_desvio * (dia_impacto * dt)
    combustible_mision_ton = combustible_mision_kg / 1000.0

    desv_neto_tan_km = abs(dist_min_tan - dist_min_sin)
    desv_neto_vert_km = abs(dist_min_vert - dist_min_sin)

    eficiencia_tan = desv_neto_tan_km / combustible_mision_ton if combustible_mision_ton > 0 else 0
    eficiencia_vert = desv_neto_vert_km / combustible_mision_ton if combustible_mision_ton > 0 else 0

    # CREACIÓN DE LA TABLA COMPARATIVA COSTO-BENEFICIO
    st.subheader("⚖️ Análisis Comparativo de Costo-Beneficio (Asteroides de Gran Masa)")

    datos_comparativa = {
        "Estrategia de Defensa": ["Inercial (Sin Acción)", "Desvío Tangencial", "Desvío Vertical Z"],
        "Masa Combustible Requerida": ["0.00 t", f"{combustible_mision_ton:.3f} t", f"{combustible_mision_ton:.3f} t"],
        "Desviación Lograda (km)": ["0 km", f"{desv_neto_tan_km:,.1f} km", f"{desv_neto_vert_km:,.1f} km"],
        "Eficiencia (km desvío / Tonelada)": ["0.0 km/t", f"{eficiencia_tan:,.2f} km/t", f"{eficiencia_vert:,.2f} km/t"],
        "Resultado de Viabilidad": ["❌ Impacto Catastrófico", "🟢 Planeta Salvado" if salvo_tan else "❌ Impacto Catastrófico", "🟢 Planeta Salvado" if salvo_vert else "❌ Impacto Catastrófico"]
    }

    df_comparativa = pd.DataFrame(datos_comparativa)
    st.table(df_comparativa)

    # GRÁFICACIÓN COMPARATIVA 3D COMPLETA
    st.subheader("🛰️ Simulador Dinámico en Tiempo Real (Vista 3D)")
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers', marker=dict(size=14, color='yellow'), name='Sol'))
    fig.add_trace(go.Scatter3d(x=tx, y=ty, z=tz, mode='lines', line=dict(color='cyan', width=3), name='Órbita de la Tierra'))
    fig.add_trace(go.Scatter3d(x=[tx[dia_impacto]], y=[ty[dia_impacto]], z=[tz[dia_impacto]], mode='markers', marker=dict(size=9, color='deepskyblue'), name='Punto de Impacto (Tierra D300)'))

    fig.add_trace(go.Scatter3d(x=axs, y=ays, z=azs, mode='lines', line=dict(color='crimson', width=3, dash='dash'), name='Asteroide Inalterado (Impacto)'))
    fig.add_trace(go.Scatter3d(x=axt, y=ayt, z=azt, mode='lines', line=dict(color='lime', width=4), name='Desvío Tangencial (Acelerar/Frenar)'))
    fig.add_trace(go.Scatter3d(x=axv, y=ayv, z=azv, mode='lines', line=dict(color='fuchsia', width=4), name='Desvío Vertical (Empuje en eje Z)'))

    fig.update_layout(template='plotly_dark', height=680, scene=dict(aspectmode='data', xaxis_title='X (UA)', yaxis_title='Y (UA)', zaxis_title='Z (UA)'))
    st.plotly_chart(fig, use_container_width=True)
