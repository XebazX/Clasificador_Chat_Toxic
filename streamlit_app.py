"""Aplicación web (Streamlit): escribe un comentario en inglés y mira qué
tipo de toxicidad detecta el modelo E-06."""
import joblib
import streamlit as st

from src.predict import (MODELO, NOMBRES, RUTA_MODELO, cargar_calibracion,
                         clasificar)

st.set_page_config(page_title="Toxic Scanner", page_icon="⚡")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
.stApp { background: radial-gradient(circle at 15% 0%, #2b0a4a 0%, #0a0a1f 45%, #02030d 100%); }
.neon-title { font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 2.3rem;
  text-align: center; letter-spacing: 2px; margin: 0;
  background: linear-gradient(90deg, #00f0ff, #ff2bd6, #b6ff00);
  -webkit-background-clip: text; background-clip: text; color: transparent;
  filter: drop-shadow(0 0 12px rgba(255, 43, 214, .55)); }
.neon-sub { text-align: center; color: #9fb3ff; margin: .2em 0 1.2em; }
.stTextArea textarea { border: 1px solid #00f0ff; border-radius: 14px; font-size: 1.05rem;
  box-shadow: 0 0 14px rgba(0, 240, 255, .35); }
.stTextArea textarea:focus { border-color: #ff2bd6; box-shadow: 0 0 22px rgba(255, 43, 214, .7); }
.stButton button { background: #0b0f24; color: #00f0ff; border: 1px solid #00f0ff; border-radius: 12px; }
.stButton button:hover { color: #ff2bd6; border-color: #ff2bd6; box-shadow: 0 0 12px rgba(255, 43, 214, .6); }
.banner { padding: 14px 18px; border-radius: 14px; font-size: 1.05rem;
  background: rgba(10, 15, 36, .85); margin: 14px 0; }
.banner.ok { border: 1px solid #b6ff00; box-shadow: 0 0 16px rgba(182, 255, 0, .45); }
.banner.info { border: 1px solid #00f0ff; box-shadow: 0 0 16px rgba(0, 240, 255, .45); }
.banner.alerta { border: 1px solid #ff2bd6; box-shadow: 0 0 18px rgba(255, 43, 214, .65);
  animation: pulso 1.6s ease-in-out infinite; }
@keyframes pulso { 50% { box-shadow: 0 0 32px rgba(255, 43, 214, .95); } }
.panel { border: 1px solid rgba(0, 240, 255, .4); border-radius: 16px; padding: 10px 18px;
  box-shadow: 0 0 18px rgba(0, 240, 255, .2); background: rgba(10, 15, 36, .6); }
.fila { display: flex; align-items: center; gap: 12px; margin: 12px 0; }
.fila span { width: 170px; color: #cfe8ff; }
.fila.marcada span { color: #ff9af0; font-weight: 700; }
.barra { flex: 1; height: 12px; background: #121a3a; border-radius: 8px; overflow: hidden; }
.relleno { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #00f0ff, #ff2bd6);
  box-shadow: 0 0 10px rgba(255, 43, 214, .7); }
.fila b { width: 48px; text-align: right; }
</style>
"""

EJEMPLOS = ["Thanks for your help, I really appreciate it.",
            "Hello bro, how are u today?",
            "You are an idiot.",
            "I will find you and hurt you."]


@st.cache_resource
def cargar():
    return joblib.load(RUTA_MODELO), cargar_calibracion()


def poner(texto: str) -> None:
    st.session_state["texto"] = texto


pipe, calib = cargar()

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(
    '<h1 class="neon-title">TOXIC SCANNER</h1>'
    '<p class="neon-sub">Escribe un comentario <b>en inglés</b> y presiona '
    f'Ctrl+Enter · modelo {MODELO} (TF-IDF + regresión logística) · comentarios anteriores a 2018 de Wikipedia (Jigsaw) y de sitios de noticias (Civil Comments)</p>',
    unsafe_allow_html=True)

st.caption("Prueba con estos ejemplos:")
columnas = st.columns(len(EJEMPLOS))
for i, (col, ej) in enumerate(zip(columnas, EJEMPLOS)):
    col.button(ej if len(ej) <= 24 else ej[:23] + "…", key=f"ej{i}",
               on_click=poner, args=(ej,), use_container_width=True)

texto = st.text_area("Tu comentario", key="texto", height=130,
                     placeholder="Type a comment in English...")

puntajes, marcadas, mensaje = clasificar(texto, pipe, calib["umbrales"], calib)
clase = "info" if puntajes is None else ("alerta" if marcadas else "ok")
st.markdown(f'<div class="banner {clase}">\n\n{mensaje}\n\n</div>',
            unsafe_allow_html=True)

if puntajes:
    filas = "".join(
        f'<div class="fila{" marcada" if e in marcadas else ""}">'
        f'<span>{NOMBRES[e]}</span>'
        f'<div class="barra"><div class="relleno" style="width:{max(p * 100, 1):.1f}%"></div></div>'
        f'<b>{p * 100:.0f}%</b></div>'
        for e, p in sorted(puntajes.items(), key=lambda x: -x[1]))
    st.markdown(f'<div class="panel">{filas}</div>', unsafe_allow_html=True)

with st.expander("Límites de uso"):
    st.markdown(
        "- Solo funciona en **inglés** y entrenado con comentarios anteriores a 2018;"
        "la jerga actual o los chats pueden fallar.\n"
        "- Es una **herramienta de apoyo**: la decisión sobre un comentario o "
        "usuario debe tomarla una persona.\n"
        "- No entiende contexto, ironía ni citas.\n"
        "- **Sesgo conocido:** marca de más comentarios normales que mencionan "
        "religión, raza, género u orientación sexual (por ejemplo, 'muslim', "
        "'black', 'gay'). Nunca uses el resultado para sancionar sin revisión "
        "humana.\n"
        "- Las categorías raras (amenaza, odio hacia un grupo) son menos "
        "fiables.\n"
        "- Los porcentajes son una estimación calibrada con datos de "
        "validación, no una garantía.\n"
        "- Esta aplicación no guarda los textos que escribes; aun así, no "
        "escribas datos personales.")