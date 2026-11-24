"""Aplicación web: escribe un comentario en inglés y mira qué tipo de
toxicidad detecta el modelo E-06."""
import json
import math
from pathlib import Path

import gradio as gr
import joblib

from src.predict import (ETIQUETAS, MAX_CARACTERES, MODELO, NOMBRES, RUTA_MODELO,
                         calibrar, cargar_calibracion, clasificar, puntuar)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

.gradio-container {
    background: radial-gradient(circle at 15% 0%, #2b0a4a 0%, #0a0a1f 45%, #02030d 100%) !important;
}
.neon-title {
    font-family: 'Orbitron', sans-serif; font-weight: 900; font-size: 2.3rem;
    text-align: center; letter-spacing: 2px; margin: .3em 0 0;
    background: linear-gradient(90deg, #00f0ff, #ff2bd6, #b6ff00);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    filter: drop-shadow(0 0 12px rgba(255, 43, 214, .55));
}
.neon-sub { text-align: center; color: #9fb3ff; margin: .2em 0 1.2em; }
#entrada textarea {
    background: #0b0f24 !important; color: #e8f7ff !important; font-size: 1.05rem;
    border: 1px solid #00f0ff !important; border-radius: 14px !important;
    box-shadow: 0 0 14px rgba(0, 240, 255, .35) !important; transition: all .25s;
}
#entrada textarea:focus {
    border-color: #ff2bd6 !important; box-shadow: 0 0 22px rgba(255, 43, 214, .7) !important;
}
.banner { padding: 14px 18px; border-radius: 14px; font-size: 1.05rem;
          background: rgba(10, 15, 36, .85); color: #e8f7ff; }
.banner.ok { border: 1px solid #b6ff00; box-shadow: 0 0 16px rgba(182, 255, 0, .45); }
.banner.info { border: 1px solid #00f0ff; box-shadow: 0 0 16px rgba(0, 240, 255, .45); }
.banner.alerta { border: 1px solid #ff2bd6; box-shadow: 0 0 18px rgba(255, 43, 214, .65);
                 animation: pulso 1.6s ease-in-out infinite; }
@keyframes pulso { 50% { box-shadow: 0 0 32px rgba(255, 43, 214, .95); } }
#detalle { border: 1px solid rgba(0, 240, 255, .4) !important; border-radius: 16px !important;
           box-shadow: 0 0 18px rgba(0, 240, 255, .2); }
"""

TEMA = gr.themes.Base(
    primary_hue="fuchsia", secondary_hue="cyan", neutral_hue="slate",
    font=[gr.themes.GoogleFont("Space Grotesk"), "system-ui", "sans-serif"],
).set(
    body_background_fill="#02030d", body_background_fill_dark="#02030d",
    background_fill_primary="#0b0f24", background_fill_primary_dark="#0b0f24",
    block_background_fill="#0b0f24", block_background_fill_dark="#0b0f24",
    block_border_color="#1d2a5c", block_border_color_dark="#1d2a5c",
    input_background_fill="#0b0f24", input_background_fill_dark="#0b0f24",
    body_text_color="#e8f7ff", body_text_color_dark="#e8f7ff",
    button_primary_background_fill="linear-gradient(90deg, #00f0ff, #ff2bd6)",
    button_primary_background_fill_hover="linear-gradient(90deg, #ff2bd6, #b6ff00)",
    button_primary_text_color="#02030d",
    stat_background_fill="linear-gradient(90deg, #00f0ff, #ff2bd6)",
)


def crear_app(pipe, umbrales, calib=None):
    def analizar(texto):
        puntajes, marcadas, mensaje = clasificar(texto, pipe, umbrales, calib)
        if puntajes is None:
            clase = "info"
        else:
            clase = "alerta" if marcadas else "ok"
        banner = f'<div class="banner {clase}">\n\n{mensaje}\n\n</div>'
        if puntajes is None:
            return None, banner
        return {NOMBRES[e]: s for e, s in puntajes.items()}, banner

    with gr.Blocks(title="Clasificador de comentarios tóxicos") as demo:
        gr.HTML(
            '<h1 class="neon-title">TOXIC SCANNER</h1>'
            '<p class="neon-sub">Escribe un comentario <b>en inglés</b> y el '
            f'resultado aparece en vivo · modelo <code>{MODELO}</code> '
            '(TF-IDF + regresión logística) ·comentarios anteriores a 2018 de Wikipedia (Jigsaw) y"'
            ' de sitios de noticias (Civil Comments)</p>')
        entrada = gr.Textbox(label="Tu comentario", lines=4, elem_id="entrada",
                             placeholder="Type a comment in English...")
        resumen = gr.Markdown()
        detalle = gr.Label(label="Probabilidad estimada por categoría",
                           num_top_classes=6, elem_id="detalle")
        entrada.change(analizar, entrada, [detalle, resumen],
                       trigger_mode="always_last", show_progress="hidden")
        gr.Examples(
            examples=["Thanks for your help, I really appreciate it.",
                      "Hello bro, how are u today?",
                      "You are an idiot.",
                      "I will find you and hurt you."],
            inputs=entrada, label="Prueba con estos ejemplos")
        with gr.Accordion("Límites de uso", open=False):
            gr.Markdown(
                "- Solo funciona en **inglés** y entrenado con comentarios anteriores a 2018;"
                "la jerga actual o los chats pueden fallar.\n"
                "- Es una **herramienta de apoyo**: la decisión sobre un comentario "
                "o usuario debe tomarla una persona.\n"
                "- No entiende contexto, ironía ni citas, y puede marcar de más "
                "comentarios que mencionan ciertos grupos.\n"
                "- Las categorías raras (amenaza, odio hacia un grupo) son menos "
                "fiables.\n"
                "- Los porcentajes son una estimación calibrada con datos de "
                "validación, no una garantía.\n"
                "- Esta aplicación no guarda los textos que escribes; aun así, "
                "no escribas datos personales.")
    return demo


if __name__ == "__main__":
    modelo = joblib.load(RUTA_MODELO)
    cfg = cargar_calibracion()
    crear_app(modelo, cfg["umbrales"], cfg).launch(theme=TEMA, css=CSS)