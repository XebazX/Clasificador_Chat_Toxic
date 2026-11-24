"""Evaluación final de E-06 frente a E-02 (UNA sola vez; ver adenda del plan).
Prueba de Civil Comments: 5 etiquetas, criterio de éxito.
Prueba de Jigsaw: 6 etiquetas, segundo uso, solo descriptivo."""
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

from src.data import load_config
from src.evaluate import ci, last_record, per_label
from src.train import get_scores, git_commit

RESULTS, MODELS = Path("results"), Path("models")
CIVIL_5 = ["toxic", "obscene", "threat", "insult", "identity_hate"]
N_BOOT = 1000


def macro(y, s, p):
    k = y.shape[1]
    auc = np.mean([roc_auc_score(y[:, j], s[:, j]) for j in range(k)])
    f1 = np.mean([f1_score(y[:, j], p[:, j], zero_division=0) for j in range(k)])
    return float(auc), float(f1)


def bootstrap(y, s6, p6, s2, p2, seed):
    rng = np.random.default_rng(seed)
    out = {"auc6": [], "f16": [], "auc2": [], "f12": []}
    for i in range(N_BOOT):
        idx = rng.integers(0, len(y), len(y))
        a6, f6 = macro(y[idx], s6[idx], p6[idx])
        a2, f2 = macro(y[idx], s2[idx], p2[idx])
        out["auc6"].append(a6); out["f16"].append(f6)
        out["auc2"].append(a2); out["f12"].append(f2)
        if (i + 1) % 200 == 0:
            print(f"  bootstrap {i + 1}/{N_BOOT}")
    return {k: np.array(v) for k, v in out.items()}


def evaluar(nombre, carpeta, usar, labels, seed):
    te = pd.read_csv(carpeta / "test.csv")
    texts = te["comment_text"].fillna("")
    idx = [labels.index(e) for e in usar]
    y = te[labels].to_numpy()[:, idx]

    thr6 = np.array(last_record("E-06")["umbrales_val"])[idx]
    thr2 = np.array(last_record("E-02")["umbrales_val"])[idx]
    s6 = get_scores(joblib.load(MODELS / "E-06.joblib"), texts)[:, idx]
    s2 = get_scores(joblib.load(MODELS / "E-02.joblib"), texts)[:, idx]
    p6, p2 = (s6 >= thr6).astype(int), (s2 >= thr2).astype(int)

    t6, t2 = per_label(y, s6, thr6, usar), per_label(y, s2, thr2, usar)
    t6.to_csv(RESULTS / f"E-06_por_etiqueta_{nombre}.csv", index=False)
    t2.to_csv(RESULTS / f"E-02_por_etiqueta_{nombre}.csv", index=False)

    print(f"\nBootstrap {nombre}...")
    bs = bootstrap(y, s6, p6, s2, p2, seed)
    a6, f6 = macro(y, s6, p6)
    a2, f2 = macro(y, s2, p2)
    d_auc, d_f1 = bs["auc6"] - bs["auc2"], bs["f16"] - bs["f12"]

    pd.set_option("display.float_format", "{:.4f}".format)
    print(f"\n=== Prueba {nombre} ({len(te)} comentarios, etiquetas: {usar}) ===")
    print("E-06 por etiqueta:\n", t6.to_string(index=False))
    print("E-02 por etiqueta:\n", t2.to_string(index=False))
    print(f"E-06: ROC-AUC={a6:.4f} {ci(bs['auc6'])} | F1={f6:.4f} {ci(bs['f16'])}")
    print(f"E-02: ROC-AUC={a2:.4f} {ci(bs['auc2'])} | F1={f2:.4f} {ci(bs['f12'])}")
    print(f"Diferencia E-06 - E-02: AUC {a6 - a2:+.4f} {ci(d_auc)} | F1 {f6 - f2:+.4f} {ci(d_f1)}")
    return {"n": len(te), "etiquetas": usar,
            "E-06": {"roc_auc": a6, "f1": f6, "ic95_auc": ci(bs["auc6"]), "ic95_f1": ci(bs["f16"])},
            "E-02": {"roc_auc": a2, "f1": f2, "ic95_auc": ci(bs["auc2"]), "ic95_f1": ci(bs["f12"])},
            "dif_auc": a6 - a2, "ic95_dif_auc": ci(d_auc),
            "dif_f1": f6 - f2, "ic95_dif_f1": ci(d_f1)}


def main(force):
    salida = RESULTS / "test_eval_E-06.json"
    if salida.exists() and not force:
        sys.exit("Ya existe results/test_eval_E-06.json: las pruebas se usan una sola vez "
                 "(--force solo si hay que repetir, y se anota en la bitácora).")
    cfg = load_config()
    labels, seed = cfg["labels"], cfg["seed"]
    civil = evaluar("civil", Path("data/civil"), CIVIL_5, labels, seed)
    jig = evaluar("jigsaw", Path(cfg["paths"]["processed_dir"]), labels, labels, seed)

    criterios = {
        "1_civil_E06_supera_a_E02_en_AUC_y_F1": civil["dif_auc"] > 0 and civil["dif_f1"] > 0,
        "2_ic95_dif_auc_civil_sin_cero": civil["ic95_dif_auc"][0] > 0,
        "3_jigsaw_no_pierde_mas_de_0.005_auc": jig["dif_auc"] >= -0.005}
    print("\nCriterios de éxito de E-06:", criterios)
    salida.write_text(json.dumps(
        {"fecha": datetime.now().isoformat(timespec="seconds"), "commit": git_commit(),
         "civil": civil, "jigsaw_descriptivo": jig, "criterios": criterios},
        indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main("--force" in sys.argv)