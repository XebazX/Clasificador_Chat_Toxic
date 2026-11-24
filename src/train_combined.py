"""E-06: igual que E-02 (TF-IDF 1-gramas + regresión logística, C=1,
class_weight balanced); la única variable que cambia son los datos de
entrenamiento: Jigsaw + Civil Comments. Usa solo entrenamiento y validación."""
import json
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

from src.data import load_config
from src.evaluate import last_record
from src.train import best_threshold, build_pipeline, get_scores, git_commit

RESULTS, MODELS = Path("results"), Path("models")
EXP = {"id": "E-06", "model": "logreg", "ngram_range": [1, 1],
       "class_weight": True, "C": 1.0,
       "desc": "E-02 con datos Jigsaw + Civil Comments (única variable)"}
CIVIL_5 = ["toxic", "obscene", "threat", "insult", "identity_hate"]


def cargar(carpeta: Path, nombre: str, fuente: str, labels: list) -> pd.DataFrame:
    df = pd.read_csv(carpeta / f"{nombre}.csv")
    df["fuente"] = fuente
    return df[["comment_text", "norm", "fuente"] + labels]


def metricas(y, s, thr, labels, usar) -> dict:
    idx = [labels.index(e) for e in usar]
    return {
        "roc_auc_macro": float(np.mean([roc_auc_score(y[:, j], s[:, j]) for j in idx])),
        "ap_macro": float(np.mean([average_precision_score(y[:, j], s[:, j]) for j in idx])),
        "f1_macro": float(np.mean([f1_score(y[:, j], s[:, j] >= thr[j]) for j in idx])),
    }


def main() -> None:
    cfg = load_config()
    labels, seed = cfg["labels"], cfg["seed"]
    jig, civ = Path(cfg["paths"]["processed_dir"]), Path("data/civil")

    tr = pd.concat([cargar(jig, "train", "jigsaw", labels),
                    cargar(civ, "train", "civil", labels)], ignore_index=True)
    val = pd.concat([cargar(jig, "val", "jigsaw", labels),
                     cargar(civ, "val", "civil", labels)], ignore_index=True)
    test_norms = set(cargar(jig, "test", "jigsaw", labels)["norm"]) | \
                 set(cargar(civ, "test", "civil", labels)["norm"])

    # Ningún texto de entrenamiento en validación o prueba (de ninguna fuente)
    prohibidos = set(val["norm"]) | test_norms
    n0 = len(tr)
    tr = tr[~tr["norm"].isin(prohibidos)].reset_index(drop=True)
    print(f"Entrenamiento: {len(tr)} filas (quitadas por solaparse: {n0 - len(tr)}) | "
          f"Civil = {(tr['fuente'] == 'civil').mean():.1%}")

    t0 = time.time()
    pipe = build_pipeline(EXP, cfg["tfidf"]["max_features"], seed)
    pipe.fit(tr["comment_text"].fillna(""), tr[labels].to_numpy())
    print(f"Entrenado en {time.time() - t0:.0f} s")

    y_val = val[labels].to_numpy()
    s_val = get_scores(pipe, val["comment_text"].fillna(""))
    umbrales = [best_threshold(y_val[:, j], s_val[:, j]) for j in range(len(labels))]

    # E-02 como referencia, con sus propios umbrales (ajustados en validación de Jigsaw)
    e02 = joblib.load(MODELS / "E-02.joblib")
    s_e02 = get_scores(e02, val["comment_text"].fillna(""))
    thr_e02 = last_record("E-02")["umbrales_val"]

    res = {}
    for fuente, usar in [("jigsaw", labels), ("civil", CIVIL_5)]:
        m = (val["fuente"] == fuente).to_numpy()
        res[fuente] = {"E-06": metricas(y_val[m], s_val[m], umbrales, labels, usar),
                       "E-02": metricas(y_val[m], s_e02[m], thr_e02, labels, usar)}
        print(f"\nValidación {fuente} ({m.sum()} comentarios, {len(usar)} etiquetas):")
        for k in ("E-02", "E-06"):
            print(f"  {k}: " + " | ".join(f"{a}={b:.4f}" for a, b in res[fuente][k].items()))

    MODELS.mkdir(exist_ok=True)
    joblib.dump(pipe, MODELS / "E-06.joblib")
    reg = {"id": "E-06", "fecha": datetime.now().isoformat(timespec="seconds"),
           "descripcion": EXP["desc"], "commit": git_commit(), "semilla": seed,
           "n_train": len(tr), "n_val": len(val),
           "params": {k: EXP[k] for k in ("model", "ngram_range", "class_weight", "C")}
                     | {"max_features": cfg["tfidf"]["max_features"]},
           "val_por_fuente": res, "umbrales_val": umbrales,
           "tiempo_s": round(time.time() - t0, 1)}
    with open(RESULTS / "experiments.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()