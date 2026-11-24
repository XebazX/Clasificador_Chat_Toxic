import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from src.app import ETIQUETAS, MAX_CARACTERES, clasificar


def _pipe():
    textos = ["you are an idiot", "thank you very much",
              "i will kill you", "have a nice day"] * 5
    y = np.tile([[1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0],
                 [1, 0, 1, 0, 1, 0], [0, 0, 0, 0, 0, 0]], (5, 1))
    pipe = Pipeline([("tfidf", TfidfVectorizer()),
                     ("clf", OneVsRestClassifier(
                         LogisticRegression(solver="liblinear")))])
    return pipe.fit(textos, y)


def test_entrada_vacia_da_mensaje_claro():
    puntajes, marcadas, mensaje = clasificar("   ", _pipe(), [0.5] * 6)
    assert puntajes is None and marcadas == [] and "Escribe" in mensaje


def test_texto_demasiado_largo_se_rechaza():
    puntajes, _, mensaje = clasificar("a" * (MAX_CARACTERES + 1), _pipe(), [0.5] * 6)
    assert puntajes is None and "demasiado largo" in mensaje


def test_salida_tiene_las_seis_etiquetas_entre_0_y_1():
    puntajes, _, _ = clasificar("you are an idiot", _pipe(), [0.5] * 6)
    assert set(puntajes) == set(ETIQUETAS)
    assert all(0 <= v <= 1 for v in puntajes.values())


def test_umbrales_extremos():
    _, todas, _ = clasificar("you are an idiot", _pipe(), [0.0] * 6)
    _, ninguna, _ = clasificar("you are an idiot", _pipe(), [1.1] * 6)
    assert len(todas) == 6 and ninguna == []


def test_texto_no_ingles_genera_aviso():
    _, _, mensaje = clasificar("你好你好你好你好", _pipe(), [0.5] * 6)
    assert "no estar en inglés" in mensaje