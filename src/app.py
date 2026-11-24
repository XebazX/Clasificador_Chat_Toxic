"""Aplicación web: escribe un comentario en inglés y mira qué tipo de
toxicidad detecta el modelo E-02."""
import json
from pathlib import Path

import gradio as gr
import joblib

MODELO = "E-02"
RUTA_MODELO = Path("models") / f"{MODELO}.joblib"
RUTA_UMBRALES = Path("models") / f"{MODELO}_umbrales.json"
RUTA_REGISTRO = Path("results") / "experiments.jsonl"

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


def cargar_umbrales() -> list:
    """Umbrales fijados en validación (mismo orden que ETIQUETAS)."""
    if RUTA_UMBRALES.exists():
        return json.loads(RUTA_UMBRALES.read_text(encoding="utf-8"))["umbrales"]
    with open(RUTA_REGISTRO, encoding="utf-8") as f:
        registros = [json.loads(linea) for linea in f]
    return [r for r in registros if r["id"] == MODELO][-1]["umbrales_val"]


def puntuar(texto: str, pipe) -> dict:
    """Puntaje (0 a 1) del modelo para cada etiqueta."""
    X = pipe.named_steps["tfidf"].transform([texto])
    p = pipe.named_steps["clf"].predict_proba(X)[0]
    return {e: float(v) for e, v in zip(ETIQUETAS, p)}


def clasificar(texto, pipe, umbrales):
    """Valida la entrada y devuelve (puntajes, etiquetas_marcadas, mensaje).
    Si la entrada no es válida, puntajes es None."""
    if texto is None or not texto.strip():
        return None, [], "Escribe un comentario en inglés para analizarlo."
    if len(texto) > MAX_CARACTERES:
        return None, [], (f"El texto es demasiado largo ({len(texto)} "
                          f"caracteres). El máximo es {MAX_CARACTERES}.")

    puntajes = puntuar(texto, pipe)
    marcadas = [e for e, u in zip(ETIQUETAS, umbrales) if puntajes[e] >= u]

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
    return puntajes, marcadas, mensaje


def crear_app(pipe, umbrales):
    def analizar(texto):
        puntajes, _, mensaje = clasificar(texto, pipe, umbrales)
        if puntajes is None:
            return None, mensaje
        return {NOMBRES[e]: s for e, s in puntajes.items()}, mensaje

    with gr.Blocks(title="Clasificador de comentarios tóxicos") as demo:
        gr.Markdown(
            "# Clasificador de comentarios tóxicos\n"
            "Escribe un comentario **en inglés** y el resultado aparece debajo. "
            f"Modelo `{MODELO}` (TF-IDF + regresión logística), entrenado con "
            "el dataset Jigsaw Toxic Comment (Wikipedia, 2017).")
        entrada = gr.Textbox(label="Comentario (en inglés)", lines=4,
                             placeholder="Type a comment in English...")
        resumen = gr.Markdown()
        detalle = gr.Label(label="Puntaje por categoría (0 a 1)",
                           num_top_classes=6)
        entrada.change(analizar, entrada, [detalle, resumen],
                       trigger_mode="always_last", show_progress="hidden")
        gr.Examples(
            examples=["Thanks for your help, I really appreciate it.",
                      "You are an idiot.",
                      "I will find you and hurt you."],
            inputs=entrada)
        gr.Markdown(
            "### Límites de uso\n"
            "- Solo funciona en **inglés** y fue entrenado con comentarios de "
            "Wikipedia; en otros contextos puede fallar.\n"
            "- Es una **herramienta de apoyo**: la decisión sobre un comentario "
            "o usuario debe tomarla una persona.\n"
            "- No entiende contexto, ironía ni citas, y puede marcar de más "
            "comentarios que mencionan ciertos grupos (ver `docs/evaluacion_final.md`).\n"
            "- Las categorías raras (amenaza, odio hacia un grupo) son menos "
            "fiables.\n"
            "- El puntaje no es una probabilidad calibrada.\n"
            "- Esta aplicación no guarda los textos que escribes; aun así, "
            "no escribas datos personales.")
    return demo


if __name__ == "__main__":
    modelo = joblib.load(RUTA_MODELO)
    crear_app(modelo, cargar_umbrales()).launch()