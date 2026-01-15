import streamlit as st
import pandas as pd
import os

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Avance y Ranking",
    layout="wide"
)

# =========================
# CARGA DE DATA
# =========================
@st.cache_data(ttl=3600)  # se refresca cada hora
def cargar_data():
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(ruta_script, "avance.xlsx")
    return pd.read_excel(ruta)

df = cargar_data()

df["Ranking"] = pd.to_numeric(df["Ranking"], errors="coerce")
df = df.sort_values("Ranking", na_position="last")

# =========================
# LIMPIEZA BÁSICA
# =========================
df["DEMPARTAMENTO"] = df["DEMPARTAMENTO"].astype(str).str.strip()
df["CANAL"] = df["CANAL"].astype(str).str.strip()

# =========================
# SIDEBAR – FILTROS
# =========================
st.sidebar.title("Filtros")

departamentos = ["Todos"] + sorted(df["DEMPARTAMENTO"].unique().tolist())
canales = ["Todos"] + sorted(df["CANAL"].unique().tolist())

dep_sel = st.sidebar.selectbox("Departamento", departamentos)
canal_sel = st.sidebar.selectbox("Canal", canales)

solo_ganadores = st.sidebar.checkbox("Mostrar solo ganadores")
top_n = st.sidebar.slider("Top Ranking", 1, 50, 10)

# =========================
# APLICAR FILTROS
# =========================
df_filt = df.copy()

if dep_sel != "Todos":
    df_filt = df_filt[df_filt["DEMPARTAMENTO"] == dep_sel]

if canal_sel != "Todos":
    df_filt = df_filt[df_filt["CANAL"] == canal_sel]

if solo_ganadores:
    df_filt = df_filt[df_filt["Ganadores"] == 1]

# =========================
# KPIs
# =========================
st.title("📊 Avance, Ranking y Ganadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Participantes", len(df_filt))
col2.metric("Ganadores", df_filt["Ganadores"].sum())
col3.metric(
    "Avance PP Promedio",
    f"{df_filt['Avance PP Total'].mean():.1f}%"
)
col4.metric(
    "Avance Eqv Promedio",
    f"{df_filt['Avance Eqv Total'].mean():.1f}%"
)

st.divider()

# =========================
# RANKING
# =========================
st.subheader("🏆 Ranking por Proyección Total")

df_rank = (
    df_filt
    .sort_values("Ranking")
    .head(top_n)
)

st.dataframe(
    df_rank[[
        "Ranking",
        "HC",
        "NOMBRE",
        "CANAL",
        "Avance Eqv Total",
        "Avance PP Total",
        "Cumple PP",
        "Cumple SS",
        "Ganadores"
    ]],
    use_container_width=True
)

# =========================
# GRÁFICOS
# =========================
st.subheader("📈 Avance por Departamento")

avance_dep = (
    df_filt
    .groupby("DEMPARTAMENTO", as_index=False)
    .agg({
        "Avance Eqv Total": "mean",
        "Avance PP Total": "mean"
    })
)

st.bar_chart(
    avance_dep.set_index("DEMPARTAMENTO")
)