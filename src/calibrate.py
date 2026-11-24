"""Calibra por etiqueta los puntajes de E-06 (escalado de Platt) usando SOLO
la validación (Jigsaw + Civil). No toca las pruebas ni cambia las decisiones."""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.data import load_config
from src.evaluate import last_record
from src.train import get_scores

MODELO = "E-06"
SALIDA = Path("models") / f"{MODELO}_calibracion.json"


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def sigmoide(z):
    return 1 / (1 + np.exp(-z))


def main() -> None:
    cfg = load_config()
    labels = cfg["labels"]
    val = pd.concat(
        [pd.read_csv(Path(cfg["paths"]["processed_dir"]) / "val.csv"),
         pd.read_csv("data/civil/val.csv")], ignore_index=True)
    pipe = joblib.load(Path("models") / f"{MODELO}.joblib")
    s = get_scores(pipe, val["comment_text"].fillna(""))
    y = val[labels].to_numpy()
    umbrales = last_record(MODELO)["umbrales_val"]

    a, b = [], []
    print(f"{'etiqueta':14} {'tasa real':>10} {'puntaje medio crudo':>20} "
          f"{'prob. media calibrada':>22} {'umbral calibrado':>17}")
    for j, e in enumerate(labels):
        m = LogisticRegression(C=1e6).fit(logit(s[:, j]).reshape(-1, 1), y[:, j])
        aj, bj = float(m.coef_[0][0]), float(m.intercept_[0])
        assert aj > 0, f"Pendiente no positiva en {e}: cambiaría el orden"
        a.append(aj)
        b.append(bj)
        cal = sigmoide(aj * logit(s[:, j]) + bj)
        thr_cal = float(sigmoide(aj * logit(np.array(umbrales[j])) + bj))
        print(f"{e:14} {y[:, j].mean():10.4f} {s[:, j].mean():20.4f} "
              f"{cal.mean():22.4f} {thr_cal:17.4f}")

    SALIDA.write_text(json.dumps(
        {"modelo": MODELO, "umbrales": umbrales, "a": a, "b": b,
         "nota": "Platt por etiqueta ajustado con validación Jigsaw + Civil"},
        indent=2), encoding="utf-8")
    print(f"\nGuardado en {SALIDA}")


if __name__ == "__main__":
    main()