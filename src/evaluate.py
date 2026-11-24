"""Evaluación final en el conjunto de prueba (se ejecuta UNA sola vez)."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             f1_score, precision_score, recall_score,
                             roc_auc_score)

from src.data import load_config
from src.train import get_scores, git_commit

RESULTS = Path("results")
MODELS = Path("models")
FINAL, BASE = "E-02", "E-01"
N_BOOT = 1000
TERMINOS = ["muslim", "islam", "jewish", "jew", "christian", "gay", "lesbian",
            "transgender", "black", "white", "asian", "latino", "hispanic",
            "woman", "women", "immigrant", "atheist"]


def last_record(exp_id: str) -> dict:
    """Último registro de un experimento en experiments.jsonl."""
    with open(RESULTS / "experiments.jsonl", encoding="utf-8") as f:
        regs = [json.loads(linea) for linea in f]
    return [r for r in regs if r["id"] == exp_id][-1]


def per_label(y, s, thr, labels) -> pd.DataFrame:
    pred = (s >= thr).astype(int)
    filas = []
    for j, e in enumerate(labels):
        filas.append({
            "etiqueta": e,
            "n_positivos": int(y[:, j].sum()),
            "roc_auc": roc_auc_score(y[:, j], s[:, j]),
            "ap": average_precision_score(y[:, j], s[:, j]),
            "precision": precision_score(y[:, j], pred[:, j], zero_division=0),
            "recall": recall_score(y[:, j], pred[:, j], zero_division=0),
            "f1": f1_score(y[:, j], pred[:, j], zero_division=0),
            "umbral": float(thr[j]),
        })
    return pd.DataFrame(filas)


def bootstrap(y, s_f, p_f, s_b, p_b, seed: int) -> dict:
    """Bootstrap pareado: mismas muestras para el modelo final y la base."""
    rng = np.random.default_rng(seed)
    k = y.shape[1]
    res = {"auc_f": [], "auc_b": [], "f1_f": [], "f1_b": []}
    for i in range(N_BOOT):
        idx = rng.integers(0, len(y), len(y))
        yb = y[idx]
        res["auc_f"].append(np.mean([roc_auc_score(yb[:, j], s_f[idx, j]) for j in range(k)]))
        res["auc_b"].append(np.mean([roc_auc_score(yb[:, j], s_b[idx, j]) for j in range(k)]))
        res["f1_f"].append(np.mean([f1_score(yb[:, j], p_f[idx, j], zero_division=0) for j in range(k)]))
        res["f1_b"].append(np.mean([f1_score(yb[:, j], p_b[idx, j], zero_division=0) for j in range(k)]))
        if (i + 1) % 100 == 0:
            print(f"  bootstrap {i + 1}/{N_BOOT}")
    return {k_: np.array(v) for k_, v in res.items()}


def ci(x: np.ndarray) -> list:
    return [float(v) for v in np.percentile(x, [2.5, 97.5])]


def subgrupo_longitud(texts, y, p, s, labels, cortes) -> pd.DataFrame:
    """Desempeño en la etiqueta 'toxic' según la longitud del comentario."""
    j = labels.index("toxic")
    n_pal = texts.str.split().str.len().to_numpy()
    grupo = pd.cut(n_pal, [-np.inf, *cortes, np.inf],
                   labels=["corto", "mediano-corto", "mediano-largo", "largo"])
    filas = []
    for g in grupo.categories:
        m = np.asarray(grupo == g)
        filas.append({"grupo": g, "n": int(m.sum()),
                      "toxic_positivos": int(y[m, j].sum()),
                      "precision": precision_score(y[m, j], p[m, j], zero_division=0),
                      "recall": recall_score(y[m, j], p[m, j], zero_division=0),
                      "f1": f1_score(y[m, j], p[m, j], zero_division=0)})
    return pd.DataFrame(filas)


def subgrupo_identidad(texts, y, p) -> pd.DataFrame:
    """Tasa de falsos positivos en comentarios SIN etiquetas que mencionan
    términos de identidad, frente al resto de comentarios sin etiquetas."""
    sin_etiqueta = y.sum(axis=1) == 0
    marcado = p.any(axis=1)
    filas = [{"termino": "(todos sin etiqueta)", "n": int(sin_etiqueta.sum()),
              "tasa_falsos_positivos": float(marcado[sin_etiqueta].mean())}]
    for t in TERMINOS:
        m = texts.str.contains(rf"\b{t}\b", case=False, regex=True).to_numpy() & sin_etiqueta
        if m.sum() > 0:
            filas.append({"termino": t, "n": int(m.sum()),
                          "tasa_falsos_positivos": float(marcado[m].mean())})
    return pd.DataFrame(filas)


def figura_matrices(y, p, labels) -> None:
    fig, ejes = plt.subplots(2, 3, figsize=(12, 7))
    for j, ax in enumerate(ejes.ravel()):
        cm = confusion_matrix(y[:, j], p[:, j])
        ax.imshow(cm, cmap="Blues")
        ax.set_title(labels[j])
        ax.set_xlabel("Predicho (0 = no, 1 = sí)")
        ax.set_ylabel("Real (0 = no, 1 = sí)")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        for a in range(2):
            for b in range(2):
                ax.text(b, a, f"{cm[a, b]}", ha="center", va="center",
                        color="red" if cm[a, b] > cm.max() / 2 else "black")
    fig.suptitle(f"Matrices de confusión por etiqueta, {FINAL} (prueba, número de comentarios)")
    fig.tight_layout()
    fig.savefig(RESULTS / "matrices_confusion.png", dpi=150)


def main(force: bool) -> None:
    cfg = load_config()
    labels = cfg["labels"]
    salida = RESULTS / "test_eval.json"
    if salida.exists() and not force:
        sys.exit("Ya existe results/test_eval.json: la prueba se usa una sola vez. "
                 "Si de verdad hay que repetirla, usa --force y anótalo en la bitácora.")

    carpeta = Path(cfg["paths"]["processed_dir"])
    te = pd.read_csv(carpeta / "test.csv")
    tr = pd.read_csv(carpeta / "train.csv", usecols=["comment_text"])
    texts = te["comment_text"].fillna("")
    y = te[labels].to_numpy()

    thr_f = np.array(last_record(FINAL)["umbrales_val"])
    thr_b = np.array(last_record(BASE)["umbrales_val"])
    s_f = get_scores(joblib.load(MODELS / f"{FINAL}.joblib"), texts)
    s_b = get_scores(joblib.load(MODELS / f"{BASE}.joblib"), texts)
    p_f = (s_f >= thr_f).astype(int)
    p_b = (s_b >= thr_b).astype(int)

    tabla_f = per_label(y, s_f, thr_f, labels)
    tabla_b = per_label(y, s_b, thr_b, labels)
    macro_f = {"roc_auc_macro": tabla_f["roc_auc"].mean(),
               "ap_macro": tabla_f["ap"].mean(), "f1_macro": tabla_f["f1"].mean()}
    macro_b = {"roc_auc_macro": tabla_b["roc_auc"].mean(),
               "ap_macro": tabla_b["ap"].mean(), "f1_macro": tabla_b["f1"].mean()}

    print("Bootstrap (puede tardar varios minutos)...")
    bs = bootstrap(y, s_f, p_f, s_b, p_b, cfg["seed"])
    d_auc, d_f1 = bs["auc_f"] - bs["auc_b"], bs["f1_f"] - bs["f1_b"]

    resumen = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "commit": git_commit(), "modelo_final": FINAL, "base": BASE,
        "n_prueba": len(te), "n_bootstrap": N_BOOT,
        "final": {**macro_f, "ic95_roc_auc": ci(bs["auc_f"]), "ic95_f1": ci(bs["f1_f"])},
        "base_metricas": {**macro_b, "ic95_roc_auc": ci(bs["auc_b"]), "ic95_f1": ci(bs["f1_b"])},
        "diferencia_final_menos_base": {
            "roc_auc": float(macro_f["roc_auc_macro"] - macro_b["roc_auc_macro"]),
            "ic95_roc_auc": ci(d_auc),
            "f1": float(macro_f["f1_macro"] - macro_b["f1_macro"]),
            "ic95_f1": ci(d_f1)},
    }
    c1 = resumen["diferencia_final_menos_base"]["roc_auc"] > 0
    c2 = resumen["diferencia_final_menos_base"]["f1"] > 0
    c3 = ci(d_auc)[0] > 0 and ci(d_f1)[0] > 0
    resumen["criterios"] = {"1_auc_mayor": c1, "2_f1_mayor": c2,
                            "3_mejora_fuera_del_ic_de_cero": bool(c3)}

    RESULTS.mkdir(exist_ok=True)
    tabla_f.to_csv(RESULTS / "metricas_por_etiqueta_E-02.csv", index=False)
    tabla_b.to_csv(RESULTS / "metricas_por_etiqueta_E-01.csv", index=False)
    cortes = tr["comment_text"].fillna("").str.split().str.len().quantile([.25, .5, .75]).tolist()
    sub_long = subgrupo_longitud(texts, y, p_f, s_f, labels, cortes)
    sub_id = subgrupo_identidad(texts, y, p_f)
    sub_long.to_csv(RESULTS / "subgrupo_longitud.csv", index=False)
    sub_id.to_csv(RESULTS / "subgrupo_identidad.csv", index=False)
    figura_matrices(y, p_f, labels)

    # Errores de la etiqueta 'toxic' (contienen texto ofensivo y posibles datos
    # personales: NO se suben a Git, ver .gitignore)
    j = labels.index("toxic")
    err = te[["id", "comment_text"]].copy()
    err["comment_text"] = err["comment_text"].str.slice(0, 300)
    err["score_toxic"] = s_f[:, j]
    fn = err[(y[:, j] == 1) & (p_f[:, j] == 0)].sort_values("score_toxic").head(40).assign(tipo="falso_negativo")
    fp = err[(y[:, j] == 0) & (p_f[:, j] == 1)].sort_values("score_toxic", ascending=False).head(40).assign(tipo="falso_positivo")
    pd.concat([fn, fp]).to_csv(RESULTS / "errores_toxic.csv", index=False)

    salida.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")

    pd.set_option("display.float_format", "{:.4f}".format)
    print(f"\n=== {FINAL} en prueba ({len(te)} comentarios) ===")
    print(tabla_f.to_string(index=False))
    print(f"\nMacro {FINAL}: {macro_f}")
    print(f"Macro {BASE}: {macro_b}")
    print("IC95% ROC-AUC final:", resumen["final"]["ic95_roc_auc"], "| F1:", resumen["final"]["ic95_f1"])
    print("Diferencia (final - base):", resumen["diferencia_final_menos_base"])
    print("Criterios de éxito:", resumen["criterios"])
    print("\nPor longitud (etiqueta toxic), cortes de palabras:", cortes)
    print(sub_long.to_string(index=False))
    print("\nFalsos positivos en comentarios sin etiqueta que mencionan términos de identidad:")
    print(sub_id.to_string(index=False))


if __name__ == "__main__":
    main("--force" in sys.argv)