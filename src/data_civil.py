"""Descarga una muestra de Civil Comments y la deja con las 6 etiquetas del
proyecto (corte 0,5 sobre la fracción de anotadores)."""
from pathlib import Path

import pandas as pd
from datasets import load_dataset

from src.data import clean, load_config

MAPEO = {"toxic": "toxicity", "severe_toxic": "severe_toxicity",
         "obscene": "obscene", "threat": "threat", "insult": "insult",
         "identity_hate": "identity_attack"}
CORTE = 0.5
TAMANOS = {"train": 300_000, "validation": 30_000, "test": 30_000}
SALIDA = Path("data/civil")


def preparar(split: str, n: int, labels: list, seed: int) -> pd.DataFrame:
    df = load_dataset("google/civil_comments", split=split).to_pandas()
    df = df.sample(n=min(n, len(df)), random_state=seed)
    out = pd.DataFrame({
        "id": [f"cc_{split}_{i}" for i in df.index],
        "comment_text": df["text"].fillna("").values})
    for e in labels:
        out[e] = (df[MAPEO[e]].values >= CORTE).astype(int)
    out = clean(out, labels)          # mismas reglas que con Jigsaw
    out["fuente"] = "civil"
    return out


def main() -> None:
    cfg = load_config()
    labels, seed = cfg["labels"], cfg["seed"]
    partes = {s: preparar(s, n, labels, seed) for s, n in TAMANOS.items()}

    # Ningún texto de entrenamiento puede aparecer en validación o prueba
    otros = set(partes["validation"]["norm"]) | set(partes["test"]["norm"])
    partes["train"] = partes["train"][~partes["train"]["norm"].isin(otros)]

    SALIDA.mkdir(parents=True, exist_ok=True)
    for split, nombre in [("train", "train"), ("validation", "val"), ("test", "test")]:
        df = partes[split]
        df.to_csv(SALIDA / f"{nombre}.csv", index=False)
        print(f"\n{nombre}: {len(df)} filas | "
              f"{(df[labels].sum(axis=1) > 0).mean():.2%} con alguna etiqueta")
        print(df[labels].sum().to_string())


if __name__ == "__main__":
    main()