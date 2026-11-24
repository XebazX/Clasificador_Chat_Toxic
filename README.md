# Clasificador de comentarios tóxicos

Clasificador multietiqueta de comentarios en **inglés** que estima la probabilidad de seis tipos de toxicidad (`toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`). Proyecto 28 del taller "100 Proyectos de Machine Learning". Es una **herramienta de apoyo para moderadores humanos**, no un moderador automático.

## Demo en línea
**https://toxic-scanner.streamlit.app/**

Escribe un comentario en inglés y presiona Ctrl+Enter: la página muestra la probabilidad de cada categoría y si queda marcado para revisión humana. Usa el modelo final (E-06). La aplicación no guarda los textos que se escriben; aun así, no escribas datos personales. Si la página está dormida por falta de uso, al abrirla tarda un momento en despertar.

## Alcance
- **Hace:** recibe un comentario en inglés y devuelve la probabilidad de cada categoría de toxicidad.
- **No hace:** no funciona en otros idiomas, no sanciona ni borra mensajes, no entiende contexto, ironía ni citas, y no garantiza ausencia de sesgo (ver `docs/evaluacion_final.md`). Los datos son de 2015 a 2017: la jerga actual puede fallar.

## Datos
- **Jigsaw Toxic Comment Classification Challenge** (comentarios de Wikipedia). CC0 para el conjunto y CC-SA-3.0 para el texto. Se descarga manualmente de Kaggle.
- **Civil Comments** (comentarios de sitios de noticias, 2015-2017, CC0), usado desde Hugging Face (`google/civil_comments`) para el modelo E-06. Se descarga automáticamente.

Ningún dato se incluye en este repositorio. Fichas: `docs/ficha_datos.md`.

## Resultados (conjuntos de prueba)
| Modelo | Prueba Jigsaw: ROC-AUC / F1 macro | Prueba Civil (5 etiquetas): ROC-AUC / F1 macro |
|---|---|---|
| E-01 línea base (TF-IDF + regresión logística) | 0,9775 / 0,6034 | no evaluado |
| E-02 (+ `class_weight="balanced"`), solo Jigsaw | 0,9794 / 0,6123 | 0,8801 / 0,2137 |
| **E-06 modelo final** (E-02 + datos de Civil Comments) | 0,9805 / 0,6171 | **0,9545 / 0,4724** |

- E-02 era el mejor modelo entrenado solo con Jigsaw, pero **generaliza mal a otro dominio** (AUC 0,88 en Civil). E-06 lo corrige y en Jigsaw no pierde nada (la diferencia no es demostrable).
- El desempeño absoluto en Civil es modesto (F1 de `threat` 0,29; `identity_hate` 0,37). `severe_toxic` solo se evalúa en Jigsaw.
- La prueba de Jigsaw se usó dos veces (E-02 y E-06); la segunda es solo descriptiva.
- Detalle: `docs/evaluacion_final.md`, `docs/evaluacion_E-06.md`, `docs/bitacora_experimentos.md`.

## Estructura
```
.streamlit/config.toml     tema de la aplicación
configs/config.yaml        semilla, rutas, hiperparámetros y experimentos
data/                      datos (no versionados)
docs/                      documentación (ver abajo)
models/                    solo el modelo final E-06 y su calibración
notebooks/01_eda.ipynb     exploración de datos
results/                   métricas, tablas y figuras
src/data.py                limpieza y partición de Jigsaw
src/data_civil.py          descarga y preparación de Civil Comments
src/train.py               experimentos E-01 a E-05
src/evaluate.py            evaluación final de E-02 (una sola vez)
src/train_combined.py      experimento E-06 (Jigsaw + Civil Comments)
src/evaluate_combined.py   evaluación final de E-06 (una sola vez)
src/calibrate.py           calibración de probabilidades con la validación
src/predict.py             lógica de predicción compartida
src/app.py                 interfaz Gradio (local)
streamlit_app.py           aplicación web publicada (Streamlit)
tests/                     pruebas automáticas
requirements.txt           dependencias con versiones fijadas
```

## Instalación y ejecución paso a paso
Requiere Python 3.12.

**1. Clonar e instalar**
```bash
git clone https://github.com/XebazX/Clasificador_Chat_Toxic.git
cd Clasificador_Chat_Toxic
pip install -r requirements.txt
```

**2. Descargar Jigsaw:** entrar a https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data, aceptar las reglas, descargar `train.csv` y guardarlo como `data/train.csv` (debe ser un archivo, no una carpeta).

**3. Jigsaw: preparar, entrenar y evaluar** (unos 30 minutos)
```bash
python -m src.data            # limpieza y partición 70/15/15 (semilla 42)
python -m src.train           # experimentos E-01 a E-05
python -m src.evaluate        # evaluación final de E-02 (una sola vez)
```

**4. Civil Comments y modelo final** (descarga unos 415 MB)
```bash
python -m src.data_civil         # muestra de Civil Comments
python -m src.train_combined     # entrena E-06
python -m src.evaluate_combined  # evaluación final de E-06 (una sola vez)
python -m src.calibrate          # calibración de los puntajes
```
Las evaluaciones se detienen si su archivo de resultados ya existe (con `--force` se repiten, y debe anotarse en la bitácora).

**5. Pruebas y aplicación en local**
```bash
python -m pytest
python -m streamlit run streamlit_app.py
```

## Ejecución en Google Colab
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
!python -m src.data_civil
!python -m src.train_combined
!python -m src.evaluate_combined
!python -m src.calibrate
```

## Documentación (`docs/`)
`planteamiento.md` · `referencias.md` · `ficha_datos.md` · `decisiones_tecnicas.md` · `plan_evaluacion.md` (con la adenda de E-06) · `bitacora_experimentos.md` · `evaluacion_final.md` · `evaluacion_E-06.md` · `plan_seguimiento.md` · `riesgos_etica.md` · `declaracion_ia.md` · `glosario.md` · `lista_verificacion.md`

## Reproducibilidad
Semilla fija (42) en `configs/config.yaml` y versiones fijadas en `requirements.txt`. Los registros completos de cada experimento (parámetros, commit, umbrales, tiempos) están en `results/experiments.jsonl`. Solo el modelo final (4 MB) se versiona, para el despliegue; los demás modelos no.

## Licencia
Código bajo licencia MIT (ver `LICENSE`). Los datasets conservan sus propias licencias.