import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Predios Cercado de Lima 2025",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Predios — Cercado de Lima, Ene–Mar 2025")
st.caption("Análisis exploratorio estadístico · Fuente: dataset municipal")

# ── Carga de datos ───────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("Predios_Cercado_de_Lima_Ene-Mar_2025_4.xlsx")
    df.columns = df.columns.str.replace(r"\s*\n\s*", " ", regex=True).str.strip()
    return df

df = load_data()

# Nombres limpios de columnas clave
COL_AV      = "Autovalúo 2025 (S/)"
COL_MAT     = "Material del predio"
COL_USO     = "Uso de predio"
COL_PISOS   = "Pisos"
COL_ANIO    = "Año construcción"
COL_AREA_C  = "Área construida (m2)"
COL_AREA_T  = "Área de terreno (m2)"
COL_TIPO_P  = "Tipo propietario"
COL_AFECTO  = "Predio afecto a Imp. Predial 2025"
COL_PCT_P   = "Porcentaje propiedad"

# ── Métricas resumen ─────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total predios",      f"{len(df):,}")
m2.metric("Autovalúo mediano",  f"S/ {df[COL_AV].median():,.0f}")
m3.metric("Afectos Imp. Predial", f"{(df[COL_AFECTO]=='S').mean()*100:.1f}%")
m4.metric("Año construcción mediano", int(df[COL_ANIO].median()))

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 1. HISTOGRAMA — Distribución del autovalúo (escala log)
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("1 · Distribución del autovalúo 2025")

df_av = df[df[COL_AV] > 0].copy()
df_av["log_av"] = np.log10(df_av[COL_AV])

fig1 = px.histogram(
    df_av,
    x="log_av",
    nbins=50,
    labels={"log_av": "log₁₀(Autovalúo S/)"},
    color_discrete_sequence=["#7F77DD"],
)
fig1.update_layout(
    xaxis=dict(
        tickvals=[3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7],
        ticktext=["1k", "3k", "10k", "31k", "100k", "316k", "1M", "3M", "10M"],
        title="Autovalúo (S/)",
    ),
    yaxis_title="Número de predios",
    bargap=0.05,
    height=380,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig1.update_traces(marker_line_width=0)
st.plotly_chart(fig1, use_container_width=True)
st.caption("Distribución aproximadamente normal en escala logarítmica. El grueso se concentra entre S/ 10k y S/ 316k.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 2. BOX PLOTS — Autovalúo por material y por uso
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("2 · Box plots: autovalúo por material y por uso")

col_a, col_b = st.columns(2)

with col_a:
    fig2a = px.box(
        df[df[COL_MAT] != "No declarado"],
        x=COL_MAT,
        y=COL_AV,
        color=COL_MAT,
        log_y=True,
        color_discrete_map={
            "Ladrillo":     "#378ADD",
            "Concreto":     "#1D9E75",
            "Adobe":        "#BA7517",
            "Madera u otros": "#888780",
        },
        labels={COL_AV: "Autovalúo 2025 (S/)", COL_MAT: ""},
    )
    fig2a.update_layout(
        showlegend=False, height=380,
        yaxis_title="Autovalúo (S/) — escala log",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2a, use_container_width=True)
    st.caption("Ladrillo presenta la mediana más alta (S/ 56k). Adobe y madera tienen valores similares pero mayor dispersión.")

with col_b:
    top5_uso = df[COL_USO].value_counts().head(5).index.tolist()
    df_uso5 = df[df[COL_USO].isin(top5_uso)].copy()
    labels_cortos = {
        "Vivienda": "Vivienda",
        "Puesto (o stand) en galería comercial": "P. galería",
        "Cochera": "Cochera",
        "Local de servicios (empresarial o profesional)": "Local serv.",
        "Almacén o depósito": "Almacén",
        "Otros usos comerciales no especificados": "Otros com.",
        "Comercial - no identificado": "Comercial n/i",
    }
    df_uso5["Uso corto"] = df_uso5[COL_USO].map(labels_cortos).fillna(df_uso5[COL_USO])

    fig2b = px.box(
        df_uso5,
        x="Uso corto",
        y=COL_AV,
        color="Uso corto",
        log_y=True,
        color_discrete_sequence=["#378ADD", "#D4537E", "#888780", "#1D9E75", "#BA7517"],
        labels={COL_AV: "Autovalúo 2025 (S/)", "Uso corto": ""},
    )
    fig2b.update_layout(
        showlegend=False, height=380,
        yaxis_title="Autovalúo (S/) — escala log",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2b, use_container_width=True)
    st.caption("Vivienda tiene la mediana más alta entre los usos frecuentes. Almacén presenta la mayor dispersión.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 3. CONSTRUCCIONES POR QUINQUENIO
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("3 · Predios construidos por quinquenio (desde 1950)")

df_anio = df.dropna(subset=[COL_ANIO]).copy()
df_anio = df_anio[(df_anio[COL_ANIO] >= 1950) & (df_anio[COL_ANIO] <= 2024)]
df_anio["Quinquenio"] = (df_anio[COL_ANIO] // 5 * 5).astype(int).astype(str)
quin_cnt = df_anio["Quinquenio"].value_counts().sort_index().reset_index()
quin_cnt.columns = ["Quinquenio", "Predios"]

fig3 = px.bar(
    quin_cnt,
    x="Quinquenio",
    y="Predios",
    color_discrete_sequence=["#1D9E75"],
    labels={"Quinquenio": "Inicio del quinquenio", "Predios": "Número de predios"},
)
fig3.update_traces(marker_line_width=0)
fig3.update_layout(
    height=320,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    bargap=0.15,
)
st.plotly_chart(fig3, use_container_width=True)
st.caption("Pico en 2010–2014 (19,209 predios). Valle notable en 2000–2004. La última barra (2020–2024) está incompleta.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 4. AUTOVALÚO MEDIANO POR NÚMERO DE PISOS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("4 · Autovalúo mediano por número de pisos")

df_pisos = df[(df[COL_PISOS] >= 1) & (df[COL_PISOS] <= 15)].copy()
pisos_med = df_pisos.groupby(COL_PISOS)[COL_AV].median().reset_index()
pisos_med.columns = ["Pisos", "Autovalúo mediano (S/)"]

fig4 = px.line(
    pisos_med,
    x="Pisos",
    y="Autovalúo mediano (S/)",
    markers=True,
    color_discrete_sequence=["#D4537E"],
)
fig4.update_traces(line_width=2.5, marker_size=7)
fig4.update_layout(
    height=320,
    xaxis=dict(tickmode="linear", dtick=1),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig4.update_yaxes(tickprefix="S/ ", tickformat=",.0f")
st.plotly_chart(fig4, use_container_width=True)
st.caption("El autovalúo sube de 1 a 3 pisos y luego se estabiliza. En propiedad horizontal, el valor depende más del área de la unidad que del total del edificio.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 5. DISPERSIÓN — Área construida vs autovalúo
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("5 · Área construida vs autovalúo (muestra 5,000 predios)")

df_scatter = df[
    (df[COL_AREA_C] > 0) & (df[COL_AREA_C] < 1000) & (df[COL_AV] > 0)
].sample(min(5000, len(df)), random_state=42)

fig5 = px.scatter(
    df_scatter,
    x=COL_AREA_C,
    y=COL_AV,
    color=COL_MAT,
    log_y=True,
    opacity=0.4,
    color_discrete_map={
        "Ladrillo":     "#378ADD",
        "Concreto":     "#1D9E75",
        "Adobe":        "#BA7517",
        "Madera u otros": "#888780",
        "No declarado": "#D4537E",
    },
    labels={
        COL_AREA_C: "Área construida (m²)",
        COL_AV: "Autovalúo 2025 (S/)",
        COL_MAT: "Material",
    },
    hover_data=[COL_USO, COL_PISOS],
)
fig5.update_layout(
    height=420,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
)
fig5.update_yaxes(tickprefix="S/ ", tickformat=",.0f")
st.plotly_chart(fig5, use_container_width=True)
st.caption("Correlación alta entre área construida y autovalúo (r = 0.96). El material no altera significativamente la pendiente de la relación.")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 6. PORCENTAJE DE PROPIEDAD
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("6 · Distribución del porcentaje de propiedad")

top_pct = df[COL_PCT_P].value_counts().head(8).reset_index()
top_pct.columns = ["Porcentaje", "Predios"]
top_pct["Porcentaje"] = top_pct["Porcentaje"].apply(lambda x: f"{x:.2f}%")

fig6 = px.bar(
    top_pct,
    x="Porcentaje",
    y="Predios",
    color_discrete_sequence=["#BA7517"],
    labels={"Porcentaje": "% de propiedad declarado", "Predios": "Número de predios"},
)
fig6.update_traces(marker_line_width=0)
fig6.update_layout(
    height=300,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    bargap=0.2,
)
st.plotly_chart(fig6, use_container_width=True)
st.caption("El 64.6% (147,953 predios) declara el 100% de propiedad. El resto son condóminos con fracciones estándar (50%, 25%, 20%).")

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# 7. HEATMAP DE CORRELACIÓN
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("7 · Matriz de correlación entre variables numéricas")

num_cols = {
    COL_AV:     "Autovalúo",
    COL_AREA_C: "Área construida",
    COL_AREA_T: "Área terreno",
    COL_PISOS:  "Pisos",
    COL_PCT_P:  "% propiedad",
}
corr = df[list(num_cols.keys())].rename(columns=num_cols).corr()

fig7 = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1, zmax=1,
    aspect="auto",
)
fig7.update_layout(
    height=380,
    coloraxis_colorbar=dict(title="r"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig7, use_container_width=True)
st.caption("Área construida y autovalúo tienen correlación muy alta (r = 0.96). Número de pisos tiene correlación prácticamente nula con el autovalúo.")

st.divider()
st.caption("Dashboard generado con Streamlit + Plotly · Datos: Predios Cercado de Lima Ene–Mar 2025")
