# Decisiones técnicas

## 1. Tarea y línea base
Clasificación de texto multietiqueta (6 salidas). La **línea base** (E-01: TF-IDF de palabras + regresión logística) se definió y ejecutó **antes** que cualquier modelo más complejo.

## 2. Enfoques comparados
| Enfoque | Ventajas | Límites | Requisitos | Fuente técnica | Estado |
|---|---|---|---|---|---|
| Lista de palabras prohibidas (no ML) | Simple y explicable | Falla con sarcasmo, variaciones de escritura y usos legítimos ("kill this bug") | Lista curada | Criterio propio (`planteamiento.md`) | No implementado |
| TF-IDF + regresión logística | Rápido, interpretable, entrega probabilidades; entrena en minutos en CPU | No entiende contexto ni orden de palabras | scikit-learn, CPU | Ref. 3 (TfidfVectorizer) | Implementado: E-01 a E-04 y E-06 |
| TF-IDF + LinearSVC | Rápido, margen máximo | Sin probabilidades nativas; en nuestros datos sobreajustó más (E-05) | scikit-learn, CPU | Ref. 3 | Implementado: E-05 |
| BERT con ajuste fino | Entiende contexto | Requiere GPU, más tiempo y costo; más difícil de explicar | Modelo preentrenado, GPU | Ref. 4 | No implementado (plazo y recursos) |

## 3. Elección y justificación
Modelo final: **TF-IDF + regresión logística con `class_weight="balanced"`, entrenado con Jigsaw + Civil Comments (E-06)**.
- **Datos:** textos cortos en inglés con etiquetas muy desbalanceadas; el balanceo de clases mejoró AUC y F1 (E-02).
- **Recursos:** todo corre en CPU en pocos minutos y el modelo pesa 4 MB, lo que permite publicarlo gratis.
- **Interpretabilidad:** los coeficientes por palabra se pueden inspeccionar.
- **Objetivo:** herramienta de apoyo con revisión humana, donde ordenar bien (ROC-AUC) y marcar con un umbral por etiqueta bastan.
- **Evidencia:** `bitacora_experimentos.md` (E-01 a E-05) y `evaluacion_E-06.md`. Los n-gramas (E-03), el ajuste de C (E-04) y LinearSVC (E-05) no mejoraron.

## 4. Otras decisiones
- **Umbral por etiqueta**, elegido en validación para maximizar F1 (el umbral 0,5 no sirve con clases tan raras).
- **Sumar Civil Comments (E-06)**, porque E-02 generalizaba mal a otro dominio (AUC 0,88 en Civil).
- **Calibración (Platt) con la validación**, porque `class_weight="balanced"` infla las probabilidades; no cambia las decisiones. Ref. 8.
- **No se usaron modelos preentrenados ni APIs externas.** La ficha de `unitary/toxic-bert` (ref. 6) solo se consultó.

## 5. Licencias de las bibliotecas
| Biblioteca | Licencia |
|---|---|
| scikit-learn, NumPy, pandas, joblib | BSD-3-Clause |
| PyYAML, pytest | MIT |
| matplotlib | Licencia propia basada en PSF |
| Gradio, Streamlit, Hugging Face Datasets | Apache-2.0 |
Datasets: Jigsaw y Civil Comments, CC0 (con el texto de Jigsaw bajo CC-SA-3.0 de Wikipedia). Verificado con `pip show` para Gradio; el resto se verificó en PyPI el 24/11/2026.