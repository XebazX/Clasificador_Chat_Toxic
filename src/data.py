"""Carga, limpieza y partición del dataset Jigsaw Toxic Comment."""
from pathlib import Path

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split


def load_config(path: str = "configs/config.yaml") -> dict:
    """Lee el archivo de configuración."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(texts: pd.Series) -> pd.Series:
    """Minúsculas y espacios normalizados (para detectar casi-duplicados)."""
    return texts.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()


def clean(df: pd.DataFrame, labels: list) -> pd.DataFrame:
    """Quita grupos de casi-duplicados con etiquetas contradictorias y deja
    una sola copia de los demás casi-duplicados."""
    df = df.copy()
    df["norm"] = normalize_text(df["comment_text"])
    distintas = df.groupby("norm")[labels].transform("nunique").max(axis=1)
    df = df[distintas == 1]
    df = df.drop_duplicates(subset="norm", keep="first")
    return df.reset_index(drop=True)


def split(df: pd.DataFrame, labels: list, seed: int,
          val_size: float, test_size: float):
    """Divide en entrenamiento / validación / prueba, estratificado por
    'tiene alguna etiqueta'."""
    estrato = (df[labels].sum(axis=1) > 0).astype(int)
    train_val, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=estrato)
    val_rel = val_size / (1 - test_size)
    train, val = train_test_split(
        train_val, test_size=val_rel, random_state=seed,
        stratify=estrato.loc[train_val.index])
    return train, val, test


def check_no_leakage(train, val, test) -> None:
    """Verifica que ningún texto normalizado esté en más de una partición."""
    t, v, s = set(train["norm"]), set(val["norm"]), set(test["norm"])
    assert not (t & v), "Fuga: textos repetidos entre entrenamiento y validación"
    assert not (t & s), "Fuga: textos repetidos entre entrenamiento y prueba"
    assert not (v & s), "Fuga: textos repetidos entre validación y prueba"


def main() -> None:
    cfg = load_config()
    labels = cfg["labels"]
    df = pd.read_csv(cfg["paths"]["raw"])
    antes = len(df)

    df = clean(df, labels)
    print(f"Filas antes: {antes} | después de limpiar: {len(df)} "
          f"(quitadas: {antes - len(df)})")

    train, val, test = split(df, labels, cfg["seed"],
                             cfg["split"]["val_size"], cfg["split"]["test_size"])
    check_no_leakage(train, val, test)

    out = Path(cfg["paths"]["processed_dir"])
    out.mkdir(parents=True, exist_ok=True)
    for nombre, parte in [("train", train), ("val", val), ("test", test)]:
        parte.to_csv(out / f"{nombre}.csv", index=False)
        print(f"{nombre}: {len(parte)} filas | "
              f"{(parte[labels].sum(axis=1) > 0).mean():.2%} con alguna etiqueta")
    print("Verificación de no-fuga: OK")


if __name__ == "__main__":
    main()