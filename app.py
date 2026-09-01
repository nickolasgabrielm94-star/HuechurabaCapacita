"""
Huechuraba Capacita — Catálogo de capacitaciones del Departamento Laboral
==========================================================================

Reúne en un solo lugar las actividades de las 4 unidades del Departamento
Laboral: Programa Conectadas, Capacitaciones, Oficina de Emprendimiento e
Innovación, y OMIL.

Qué trae:
- Banner con el nombre del catálogo.
- Buscador de texto libre (busca en título y descripción).
- Filtros por Programa, Área de interés, Modalidad y Horario.
- Tarjetas con imagen, info clave y botón directo al formulario.
- Se conecta a un Google Sheet para que cada unidad agregue lo suyo sin
  tocar código (ver PASO 1 más abajo) — igual que el catálogo de Conectadas.

Cómo correrlo en tu computador:
    1. pip install streamlit pandas
    2. streamlit run app.py

Cómo publicarlo gratis (link compartible):
    1. Sube esta carpeta a un repositorio en GitHub.
    2. Entra a https://share.streamlit.io con tu cuenta de GitHub.
    3. Conecta el repositorio, Main file path: app.py, y despliega.
"""

import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# ------------------------------------------------------------------
# PASO 1 — Conecta tu Google Sheet del departamento completo
# ------------------------------------------------------------------
# Columnas exactas que debe tener la primera fila de tu Sheet:
# titulo | programa | area | modalidad | horario | fecha_inicio | cupos |
# descripcion | link_inscripcion | imagen_url
#
# "programa" es la unidad que organiza (Conectadas, Capacitaciones,
# Oficina de Emprendimiento e Innovación, OMIL). "area" sigue siendo el
# tema de interés (Empleo, Emprendimiento, Tecnología, etc.) — se pueden
# repetir áreas entre distintos programas, es normal.
#
# Archivo > Compartir > Publicar en la web > elige la hoja > formato CSV
# > Publicar, y pega el link aquí:

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQmH_C6Na43WrH1ji85l6EzzUZu5532B44ByWwKMR4mGcHLlDKVY6mM-N9r0gPaJA/pub?output=csv"  # <-- pega aquí tu link de "Publicar en la web" (CSV)

IMAGEN_POR_DEFECTO = "https://placehold.co/600x300/2e7d32/white?text=Huechuraba+Capacita"

# Colores por programa, para la etiqueta de cada tarjeta
COLORES_PROGRAMA = {
    "Conectadas": "#2e7d32",
    "Capacitaciones": "#1565c0",
    "Oficina de Emprendimiento e Innovación": "#ef6c00",
    "OMIL": "#6a1b9a",
}

# ------------------------------------------------------------------
# Configuración general de la página
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Huechuraba Capacita",
    page_icon="🎓",
    layout="wide",
)

# ------------------------------------------------------------------
# Banner (con el logo municipal, si está disponible en assets/)
# ------------------------------------------------------------------
def _logo_base64():
    ruta_logo = Path(__file__).parent / "assets" / "logo_huechuraba.png"
    if ruta_logo.exists():
        return base64.b64encode(ruta_logo.read_bytes()).decode()
    return None

_logo_b64 = _logo_base64()
_logo_html = (
    f'<img src="data:image/png;base64,{_logo_b64}" style="height:64px; margin-right:20px;">'
    if _logo_b64 else ""
)

st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg, #0d47ff, #16215c);
        padding: 28px 36px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
    ">
        {_logo_html}
        <div>
            <h1 style="color: white; margin: 0; font-size: 2.2rem;">🎓 Huechuraba Capacita</h1>
            <p style="color: #dbe4ff; margin: 6px 0 0 0; font-size: 1.05rem;">
                Todas las capacitaciones y actividades del Departamento Laboral —
                Conectadas · Capacitaciones · Oficina de Emprendimiento e Innovación · OMIL
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
@st.cache_data(ttl=600)  # se refresca sola cada 10 minutos
def cargar_capacitaciones():
    fuente = URL_GOOGLE_SHEET.strip() if URL_GOOGLE_SHEET.strip() else "capacitaciones.csv"
    df = pd.read_csv(fuente)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    for col in ("imagen_url", "programa"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    return df

df = cargar_capacitaciones()

if not URL_GOOGLE_SHEET.strip():
    st.info(
        "Estás viendo los datos del archivo capacitaciones.csv local. "
        "Sigue el PASO 1 en el código para conectar el Google Sheet del "
        "departamento y que cada unidad pueda agregar lo suyo.",
        icon="ℹ️",
    )

# ------------------------------------------------------------------
# Buscador
# ------------------------------------------------------------------
busqueda = st.text_input("🔎 Buscar capacitación", placeholder="Ej: chocolatería, comunicación, empleo...")

# ------------------------------------------------------------------
# Filtros (barra lateral)
# ------------------------------------------------------------------
st.sidebar.header("🔍 Filtrar")

programas = st.sidebar.multiselect(
    "Programa",
    options=sorted(df["programa"].dropna().unique()),
    default=sorted(df["programa"].dropna().unique()),
)

areas = st.sidebar.multiselect(
    "Área de interés",
    options=sorted(df["area"].dropna().unique()),
    default=sorted(df["area"].dropna().unique()),
)

modalidades = st.sidebar.multiselect(
    "Modalidad",
    options=sorted(df["modalidad"].dropna().unique()),
    default=sorted(df["modalidad"].dropna().unique()),
)

horarios = st.sidebar.multiselect(
    "Horario",
    options=sorted(df["horario"].dropna().unique()),
    default=sorted(df["horario"].dropna().unique()),
)

df_filtrado = df[
    df["programa"].isin(programas)
    & df["area"].isin(areas)
    & df["modalidad"].isin(modalidades)
    & df["horario"].isin(horarios)
]

if busqueda.strip():
    texto = busqueda.strip().lower()
    df_filtrado = df_filtrado[
        df_filtrado["titulo"].str.lower().str.contains(texto, na=False)
        | df_filtrado["descripcion"].str.lower().str.contains(texto, na=False)
    ]

df_filtrado = df_filtrado.sort_values("fecha_inicio")

st.sidebar.markdown("---")
st.sidebar.metric("Capacitaciones disponibles", len(df_filtrado))

if st.sidebar.button("🔄 Actualizar ahora"):
    st.cache_data.clear()
    st.rerun()

# ------------------------------------------------------------------
# Tarjetas de capacitaciones
# ------------------------------------------------------------------
if df_filtrado.empty:
    st.info("No hay capacitaciones que calcen con la búsqueda o los filtros elegidos. Prueba ampliar la búsqueda.")
else:
    columnas = st.columns(2)  # 2 tarjetas por fila

    for i, (_, curso) in enumerate(df_filtrado.iterrows()):
        with columnas[i % 2]:
            with st.container(border=True):
                imagen = curso["imagen_url"].strip() if curso["imagen_url"].strip() else IMAGEN_POR_DEFECTO
                st.image(imagen, use_container_width=True)

                color_programa = COLORES_PROGRAMA.get(curso["programa"], "#555555")
                st.markdown(
                    f"""<span style="
                        background-color: {color_programa};
                        color: white;
                        padding: 3px 10px;
                        border-radius: 12px;
                        font-size: 0.78rem;
                        font-weight: 600;
                    ">{curso['programa']}</span>""",
                    unsafe_allow_html=True,
                )

                st.subheader(curso["titulo"])
                st.markdown(
                    f"**Área:** {curso['area']} &nbsp;|&nbsp; "
                    f"**Modalidad:** {curso['modalidad']} &nbsp;|&nbsp; "
                    f"**Horario:** {curso['horario']}"
                )
                st.write(curso["descripcion"])

                fecha_txt = (
                    curso["fecha_inicio"].strftime("%d-%m-%Y")
                    if pd.notnull(curso["fecha_inicio"])
                    else "Por confirmar"
                )
                st.markdown(f"📅 Inicio: {fecha_txt} &nbsp;|&nbsp; 👥 Cupos: {curso['cupos']}")

                st.link_button("Inscribirme", curso["link_inscripcion"], use_container_width=True)
