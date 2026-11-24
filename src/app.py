"""Aplicación web: escribe un comentario en inglés y mira qué tipo de
toxicidad detecta el modelo E-06."""
import json
import math
from pathlib import Path

import gradio as gr
import joblib

MODELO = "E-06"
RUTA_MODELO = Path("models") / f"{MODELO}.joblib"
RUTA_CALIB = Path("models") / f"{MODELO}_calibracion.json"

ETIQUETAS = ["toxic", "severe_toxic", "obscene", "threat", "insult",
             "identity_hate"]
NOMBRES = {
    "toxic": "Tóxico (general)",
    "severe_toxic": "Muy tóxico",
    "obscene": "Obsceno",
    "threat": "Amenaza",
    "insult": "Insulto",
    "identity_hate": "Odio hacia un grupo",
}
MAX_CARACTERES = 5000


def cargar_calibracion() -> dict:
    """Umbrales (sobre el puntaje crudo) y parámetros de calibración."""
    return json.loads(RUTA_CALIB.read_text(encoding="utf-8"))


def calibrar(puntaje: float, a: float, b: float) -> float:
    """Convierte el puntaje crudo en una probabilidad estimada (Platt)."""
    p = min(max(puntaje, 1e-6), 1 - 1e-6)
    z = a * math.log(p / (1 - p)) + b
    return 1 / (1 + math.exp(-z))


def puntuar(texto: str, pipe) -> dict:
    """Puntaje crudo (0 a 1) del modelo para cada etiqueta."""
    X = pipe.named_steps["tfidf"].transform([texto])
    p = pipe.named_steps["clf"].predict_proba(X)[0]
    return {e: float(v) for e, v in zip(ETIQUETAS, p)}


def clasificar(texto, pipe, umbrales, calib=None):
    """Valida la entrada y devuelve (puntajes_mostrados, etiquetas_marcadas,
    mensaje). La decisión usa siempre el puntaje crudo y su umbral; si hay
    calibración, solo cambian los porcentajes que se muestran."""
    if texto is None or not texto.strip():
        return None, [], "Escribe un comentario en inglés para analizarlo."
    if len(texto) > MAX_CARACTERES:
        return None, [], (f"El texto es demasiado largo ({len(texto)} "
                          f"caracteres). El máximo es {MAX_CARACTERES}.")

    crudos = puntuar(texto, pipe)
    marcadas = [e for e, u in zip(ETIQUETAS, umbrales) if crudos[e] >= u]
    if calib:
        mostrados = {e: calibrar(crudos[e], calib["a"][i], calib["b"][i])
                     for i, e in enumerate(ETIQUETAS)}
    else:
        mostrados = crudos

    if marcadas:
        nombres = ", ".join(NOMBRES[e] for e in marcadas)
        mensaje = f"⚠️ **Marcado para revisión humana:** {nombres}"
    else:
        mensaje = ("✅ **Ninguna categoría supera su umbral.** Esto no "
                   "garantiza que el comentario sea inofensivo.")

    no_ascii = sum(1 for c in texto if ord(c) > 127) / len(texto)
    if no_ascii > 0.3:
        mensaje += ("\n\n_Aviso: el texto parece no estar en inglés; el modelo "
                    "solo fue entrenado con inglés y el resultado no es fiable._")
    return mostrados, marcadas, mensaje


def crear_app(pipe, umbrales, calib=None):
    def analizar(texto):
        puntajes, _, mensaje = clasificar(texto, pipe, umbrales, calib)
        if puntajes is None:
            return None, mensaje
        return {NOMBRES[e]: s for e, s in puntajes.items()}, mensaje

    with gr.Blocks(title="Clasificador de comentarios tóxicos") as demo:
        gr.Markdown(
            "# Clasificador de comentarios tóxicos\n"
            "Escribe un comentario **en inglés** y el resultado aparece debajo. "
            f"Modelo `{MODELO}` (TF-IDF + regresión logística), entrenado con "
            "comentarios de Wikipedia (Jigsaw, 2017) y de sitios de noticias "
            "(Civil Comments, 2015-2017).")
        entrada = gr.Textbox(label="Comentario (en inglés)", lines=4,
                             placeholder="Type a comment in English...")
        resumen = gr.Markdown()
        detalle = gr.Label(label="Probabilidad estimada por categoría",
                           num_top_classes=6)
        entrada.change(analizar, entrada, [detalle, resumen],
                       trigger_mode="always_last", show_progress="hidden")
        gr.Examples(
            examples=["Thanks for your help, I really appreciate it.",
                      "Hello bro, how are u today?",
                      "You are an idiot.",
                      "I will find you and hurt you."],
            inputs=entrada)
        gr.Markdown(
            "### Límites de uso\n"
            "- Solo funciona en **inglés** y fue entrenado con comentarios de "
            "2015-2017 (Wikipedia y sitios de noticias); la jerga actual o "
            "los chats pueden fallar.\n"
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
    crear_app(modelo, cfg["umbrales"], cfg).launch()