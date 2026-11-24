"""Lógica de predicción compartida por las interfaces (Gradio y Streamlit)."""
import json
import math
from pathlib import Path

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