# Clasificador_Chat_Toxic
Un pequeño proyecto sobre una IA que filtra mensajes ofensivos

# Clasificador de comentarios tóxicos

Clasificador multietiqueta de comentarios en **inglés** que estima la probabilidad de seis tipos de toxicidad (`toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`). Proyecto 28 del taller "100 Proyectos de Machine Learning". Está pensado como **herramienta de apoyo para moderadores humanos**, no como moderador automático.

## Alcance
- **Hace:** recibe un comentario en inglés y devuelve la probabilidad de cada categoría de toxicidad.
- **No hace:** no funciona en otros idiomas, no sanciona ni borra mensajes, no entiende contexto, ironía ni citas, y no garantiza ausencia de sesgo contra grupos de identidad (ver `docs/evaluacion_final.md`).

## Datos
Dataset *Jigsaw Toxic Comment Classification Challenge* . Licencia: CC0 para el conjunto y CC-SA-3.0 de Wikipedia para el texto. **El dataset no está en este repositorio** y debe descargarse (ver más abajo). Ficha completa: `docs/ficha_datos.md`.

## Resultados (conjunto de prueba, 23.891 comentarios, usado una sola vez)
| Modelo | ROC-AUC macro | F1 macro |
|---|---|---|
| E-01 línea base (TF-IDF + regresión logística) | 0,9775 | 0,6034 |
| **E-02 modelo final** (+ `class_weight="balanced"`) | **0,9794** (IC 95 %: 0,9768–0,9817) | **0,6123** |

La mejora de E-02 sobre la base es pequeña: demostrable en ROC-AUC, **no demostrable en F1** (el intervalo de confianza de la diferencia incluye el cero). La etiqueta más débil es `threat` (F1 = 0,43). Detalle completo en `docs/evaluacion_final.md` y `docs/bitacora_experimentos.md`.

## Estructura
```
configs/config.yaml     semilla, rutas, hiperparámetros y definición de experimentos
data/                   datos (no versionados)
docs/                   planteamiento, ficha de datos, referencias, plan de evaluación,
                        bitácora, evaluación final, riesgos y declaración de uso de IA
notebooks/01_eda.ipynb  exploración de datos
results/                métricas, tablas y figuras de los experimentos y la evaluación
src/data.py             limpieza y partición (entrenamiento / validación / prueba)
src/train.py            experimentos E-01 a E-05
src/evaluate.py         evaluación final en prueba (una sola vez)
src/app.py              aplicación web (en desarrollo)
tests/                  pruebas automáticas
requirements.txt        dependencias con versiones fijadas
```

## Requisitos
Python 3.12 y las dependencias de `requirements.txt` (pandas, NumPy, scikit-learn, matplotlib, PyYAML, pytest).

## Instalación y ejecución paso a paso

**1. Clonar e instalar**
```bash
git clone https://github.com/XebazX/Clasificador_Chat_Toxic.git
cd Clasificador_Chat_Toxic
pip install -r requirements.txt
```

**2. Descargar el dataset**
1. Entrar a https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data e iniciar sesión.
2. Aceptar las reglas de la competencia y descargar `train.csv`.
3. Guardarlo como `data/train.csv` (crear la carpeta `data` si no existe). Debe ser un archivo, no una carpeta.

**3. Preparar los datos** (limpieza y partición 70/15/15, semilla 42)
```bash
python -m src.data
```
Debe terminar con `Verificación de no-fuga: OK`. Genera `data/processed/`.

**4. Entrenar los experimentos** (unos 20 minutos en total)
```bash
python -m src.train
```
También se puede correr uno solo, por ejemplo `python -m src.train E-01`. Los experimentos se ejecutan en orden: E-05 usa el valor de `C` que E-04 deja en `results/mejor_C.json`. Guarda los modelos en `models/` y añade un registro por corrida a `results/experiments.jsonl`.

**5. Evaluar en el conjunto de prueba** (unos 5 minutos)
```bash
python -m src.evaluate
```
Se usa **una sola vez**: si `results/test_eval.json` ya existe, el script se detiene (con `--force` se repite, y debe anotarse en la bitácora).

**6. Pruebas automáticas**
```bash
python -m pytest
```

## Ejecución en Google Colab
En una celda nueva:
```python
!git clone https://github.com/XebazX/Clasificador_Chat_Toxic.git
%cd Clasificador_Chat_Toxic
!pip install -r requirements.txt

from google.colab import files
files.upload()            # seleccionar train.csv descargado de Kaggle
!mkdir -p data && mv train.csv data/

!python -m src.data
!python -m src.train
!python -m src.evaluate
```

## Demo en línea
En desarrollo: el enlace se agregará aquí cuando se publique.

## Documentación
- `docs/planteamiento.md`: problema, objetivos y alcance
- `docs/ficha_datos.md`: procedencia, licencia, calidad y preparación de los datos
- `docs/plan_evaluacion.md`: métricas y criterios de éxito (definidos antes de entrenar)
- `docs/bitacora_experimentos.md`: experimentos E-01 a E-05
- `docs/evaluacion_final.md`: resultados en prueba, subgrupos y análisis de errores
- `docs/riesgos_etica.md`: matriz de riesgos y uso responsable
- `docs/declaracion_ia.md`: declaración de uso de herramientas de IA
- `docs/referencias.md`: fuentes consultadas

## Reproducibilidad
Semilla fija (42) en `configs/config.yaml`; versiones fijadas en `requirements.txt`. Los resultados del informe se obtuvieron con la versión del código de este repositorio. Los registros completos (parámetros, commit, umbrales y tiempos) están en `results/experiments.jsonl`. Los modelos entrenados no se versionan por su tamaño.

## Licencia
Código bajo licencia MIT (ver `LICENSE`). El dataset conserva su propia licencia (CC0, con el texto bajo CC-SA-3.0).