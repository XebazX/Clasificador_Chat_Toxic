"""Revisión de sesgo por términos de identidad en E-06 (y E-02 como referencia).
Usa SOLO validación (Jigsaw + Civil); no toca las pruebas."""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.data import load_config
from src.evaluate import TERMINOS, last_record
from src.train import get_scores

RESULTS, MODELS = Path("results"), Path("models")
MIN_N = 30  # con menos comentarios la tasa no es interpretable


def wilson(k: int, n: int, z: float = 1.96):
    """Intervalo de confianza del 95 % para una proporción."""
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    mitad = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return centro - mitad, centro + mitad


def main() -> None:
    cfg = load_config()
    labels = cfg["labels"]
    fuentes = {"jigsaw": Path(cfg["paths"]["processed_dir"]) / "val.csv",
               "civil": Path("data/civil/val.csv")}
    modelos = {m: (joblib.load(MODELS / f"{m}.joblib"),
                   np.array(last_record(m)["umbrales_val"]))
               for m in ("E-02", "E-06")}

    filas = []
    for fuente, ruta in fuentes.items():
        df = pd.read_csv(ruta)
        textos = df["comment_text"].fillna("")
        sin = (df[labels].sum(axis=1) == 0).to_numpy()
        marcado = {m: (get_scores(p, textos) >= thr).any(axis=1)
                   for m, (p, thr) in modelos.items()}
        grupos = [("(todos sin etiqueta)", sin)] + [
            (t, textos.str.contains(rf"\b{t}\b", case=False, regex=True)
             .to_numpy() & sin) for t in TERMINOS]
        for nombre, mascara in grupos:
            n = int(mascara.sum())
            if n == 0:
                continue
            fila = {"fuente": fuente, "termino": nombre, "n": n,
                    "interpretable": n >= MIN_N}
            for m in modelos:
                k = int(marcado[m][mascara].sum())
                bajo, alto = wilson(k, n)
                fila[f"{m}_tasa"] = k / n
                fila[f"{m}_ic_bajo"], fila[f"{m}_ic_alto"] = bajo, alto
            filas.append(fila)

    out = pd.DataFrame(filas)
    for m in modelos:
        base = out[out.termino == "(todos sin etiqueta)"].set_index("fuente")[f"{m}_tasa"]
        out[f"{m}_veces_global"] = out.apply(
            lambda r: r[f"{m}_tasa"] / base[r["fuente"]]
            if base[r["fuente"]] > 0 else np.nan, axis=1)

    RESULTS.mkdir(exist_ok=True)
    out.to_csv(RESULTS / "sesgo_validacion_E-06.csv", index=False)
    columnas = ["fuente", "termino", "n", "interpretable", "E-02_tasa",
                "E-06_tasa", "E-06_ic_bajo", "E-06_ic_alto", "E-06_veces_global"]
    print("Comentarios SIN etiqueta que el modelo marca (falsos positivos), "
          "por término de identidad. Solo validación.\n")
    print(out[columnas].to_string(index=False, float_format="{:.3f}".format))


if __name__ == "__main__":
    main()