import pandas as pd

from src.data import check_no_leakage, clean, split

LABELS = ["toxic", "insult"]


def _df():
    filas = []
    for i in range(200):
        filas.append({"comment_text": f"comentario {i}",
                      "toxic": int(i % 5 == 0), "insult": int(i % 10 == 0)})
    return pd.DataFrame(filas)


def test_clean_quita_duplicados_y_conflictos():
    df = pd.DataFrame({
        "comment_text": ["Hola  mundo", "hola mundo", "malo", "MALO", "ok"],
        "toxic":        [0, 0, 1, 0, 0],
        "insult":       [0, 0, 0, 0, 0],
    })
    limpio = clean(df, LABELS)
    assert len(limpio) == 2                      # una copia de "hola mundo" + "ok"
    assert "malo" not in set(limpio["norm"])     # grupo con etiquetas contradictorias


def test_split_proporciones_y_sin_fuga():
    df = clean(_df(), LABELS)
    train, val, test = split(df, LABELS, seed=42, val_size=0.15, test_size=0.15)
    assert abs(len(test) / len(df) - 0.15) < 0.02
    assert abs(len(val) / len(df) - 0.15) < 0.02
    check_no_leakage(train, val, test)


def test_split_es_reproducible():
    df = clean(_df(), LABELS)
    a = split(df, LABELS, 42, 0.15, 0.15)[2]["comment_text"].tolist()
    b = split(df, LABELS, 42, 0.15, 0.15)[2]["comment_text"].tolist()
    assert a == b