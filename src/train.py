"""Entrenamiento y registro de los experimentos E-01 ... E-05."""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, f1_score,
                             precision_recall_curve, roc_auc_score)
from sklearn.model_selection import KFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from src.data import load_config

RESULTS = Path("results")
MODELS = Path("models")


def build_pipeline(exp: dict, max_features: int, seed: int) -> Pipeline:
    """TF-IDF + clasificador uno-contra-resto (una salida por etiqueta)."""
    tfidf = TfidfVectorizer(ngram_range=tuple(exp["ngram_range"]),
                            max_features=max_features)
    peso = "balanced" if exp["class_weight"] else None
    if exp["model"] == "logreg":
        base = LogisticRegression(C=exp["C"], class_weight=peso,
                                  solver="liblinear", random_state=seed)
    else:
        base = LinearSVC(C=exp["C"], class_weight=peso, random_state=seed)
    return Pipeline([("tfidf", tfidf),
                     ("clf", OneVsRestClassifier(base, n_jobs=1))])


def get_scores(pipe: Pipeline, texts: pd.Series) -> np.ndarray:
    """Probabilidades (regresión logística) o puntajes (LinearSVC)."""
    X = pipe.named_steps["tfidf"].transform(texts)
    clf = pipe.named_steps["clf"]
    if hasattr(clf, "predict_proba"):
        return clf.predict_proba(X)
    return clf.decision_function(X)


def auc_macro(y: np.ndarray, s: np.ndarray) -> float:
    return float(np.mean([roc_auc_score(y[:, j], s[:, j])
                          for j in range(y.shape[1])]))


def best_threshold(y: np.ndarray, s: np.ndarray) -> float:
    """Umbral que maximiza F1 para una etiqueta."""
    p, r, t = precision_recall_curve(y, s)
    f1 = 2 * p[:-1] * r[:-1] / np.clip(p[:-1] + r[:-1], 1e-12, None)
    return float(t[np.argmax(f1)])


def macro_metrics(y: np.ndarray, s: np.ndarray, thresholds=None):
    """ROC-AUC, AP y F1 macro. Si no hay umbrales, se calculan sobre y."""
    k = y.shape[1]
    ap = float(np.mean([average_precision_score(y[:, j], s[:, j])
                        for j in range(k)]))
    if thresholds is None:
        thresholds = [best_threshold(y[:, j], s[:, j]) for j in range(k)]
    f1 = float(np.mean([f1_score(y[:, j], s[:, j] >= thresholds[j])
                        for j in range(k)]))
    return {"roc_auc_macro": auc_macro(y, s), "ap_macro": ap,
            "f1_macro": f1}, thresholds


def cv_auc(exp: dict, texts: pd.Series, y: np.ndarray, cfg: dict):
    """ROC-AUC macro en validación cruzada (el TF-IDF se ajusta por partición)."""
    kf = KFold(n_splits=cfg["cv_folds"], shuffle=True,
               random_state=cfg["seed"])
    aucs = []
    for tr, te in kf.split(texts):
        pipe = build_pipeline(exp, cfg["tfidf"]["max_features"], cfg["seed"])
        pipe.fit(texts.iloc[tr], y[tr])
        aucs.append(auc_macro(y[te], get_scores(pipe, texts.iloc[te])))
    return float(np.mean(aucs)), float(np.std(aucs))


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "desconocido"


def tune_C(exp: dict, data: dict, cfg: dict):
    """Elige C con el conjunto de validación (nunca con la prueba)."""
    candidatos = []
    for c in cfg["c_grid"]:
        pipe = build_pipeline({**exp, "C": c}, cfg["tfidf"]["max_features"],
                              cfg["seed"])
        pipe.fit(data["x_train"], data["y_train"])
        auc = auc_macro(data["y_val"], get_scores(pipe, data["x_val"]))
        candidatos.append({"C": c, "val_roc_auc_macro": auc})
        print(f"  C={c}: ROC-AUC macro en validación = {auc:.4f}")
    mejor = max(candidatos, key=lambda d: d["val_roc_auc_macro"])["C"]
    return mejor, candidatos


def run_experiment(exp: dict, data: dict, cfg: dict, extra: dict) -> None:
    t0 = time.time()
    mf = cfg["tfidf"]["max_features"]
    registro = {
        "id": exp["id"],
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "descripcion": exp["desc"],
        "commit": git_commit(),
        "semilla": cfg["seed"],
        "n_train": len(data["x_train"]),
        "n_val": len(data["x_val"]),
        "params": {"model": exp["model"], "ngram_range": exp["ngram_range"],
                   "class_weight": exp["class_weight"], "C": exp["C"],
                   "max_features": mf},
        **extra,
    }
    media, desv = cv_auc(exp, data["x_train"], data["y_train"], cfg)

    pipe = build_pipeline(exp, mf, cfg["seed"])
    pipe.fit(data["x_train"], data["y_train"])
    train_auc = auc_macro(data["y_train"], get_scores(pipe, data["x_train"]))
    s_val = get_scores(pipe, data["x_val"])
    val_m, umbrales = macro_metrics(data["y_val"], s_val)

    registro.update({
        "cv_roc_auc_macro_media": media,
        "cv_roc_auc_macro_desv": desv,
        "train_roc_auc_macro": train_auc,
        "val": val_m,
        "brecha_auc_train_menos_val": train_auc - val_m["roc_auc_macro"],
        "umbrales_val": umbrales,
        "tiempo_s": round(time.time() - t0, 1),
    })

    MODELS.mkdir(exist_ok=True)
    joblib.dump(pipe, MODELS / f"{exp['id']}.joblib")
    with open(RESULTS / "experiments.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"  CV ROC-AUC macro: {media:.4f} ± {desv:.4f}")
    print(f"  Train ROC-AUC: {train_auc:.4f} | Val ROC-AUC: "
          f"{val_m['roc_auc_macro']:.4f} | Val F1 macro: {val_m['f1_macro']:.4f}")
    print(f"  Tiempo: {registro['tiempo_s']} s")


def main(ids: list) -> None:
    cfg = load_config()
    labels = cfg["labels"]
    carpeta = Path(cfg["paths"]["processed_dir"])
    tr = pd.read_csv(carpeta / "train.csv")
    va = pd.read_csv(carpeta / "val.csv")
    data = {
        "x_train": tr["comment_text"].fillna(""),
        "y_train": tr[labels].to_numpy(),
        "x_val": va["comment_text"].fillna(""),
        "y_val": va[labels].to_numpy(),
    }
    RESULTS.mkdir(exist_ok=True)
    mejor_c = RESULTS / "mejor_C.json"

    for exp in cfg["experiments"]:
        if ids and exp["id"] not in ids:
            continue
        exp = dict(exp)
        extra = {}
        print(f"\n=== {exp['id']}: {exp['desc']} ===")
        if exp["C"] == "tune":
            exp["C"], cand = tune_C(exp, data, cfg)
            extra["busqueda_C"] = cand
            mejor_c.write_text(json.dumps({"C": exp["C"]}))
        elif exp["C"] == "from_E-04":
            exp["C"] = json.loads(mejor_c.read_text())["C"]
        run_experiment(exp, data, cfg, extra)


if __name__ == "__main__":
    main(sys.argv[1:])