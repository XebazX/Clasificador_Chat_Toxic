# Declaración de uso de herramientas de IA

**Estudiante:** Sebastian Suarez Solorzano
**Proyecto:** Clasificador de comentarios tóxicos (proyecto 28), Machine Learning
**Fecha:** 23/11/2026

## Herramientas utilizadas
- **Claude** (Anthropic), asistente conversacional en claude.ai.
- **Git y GitHub:** control de versiones y repositorio del proyecto.
- **Kaggle:** fuente del dataset (Jigsaw Toxic Comment Classification Challenge).
- **Visual Studio Code y Jupyter:** edición del código y del notebook de EDA.
- **Hugging Face Spaces (Gradio):** alojamiento de la aplicación web de demostración.
- 
## Para qué se usó
- Orientación sobre la estructura del repositorio según la rúbrica y el uso de Git y GitHub.
- Borradores de `planteamiento.md`, `glosario.md`, `ficha_datos.md`, `plan_evaluacion.md`, `bitacora_experimentos.md`, `evaluacion_final.md`, `riesgos_etica.md`.
- Borradores de código: `src/data.py`, `src/train.py`, `src/evaluate.py`, `configs/config.yaml`, `tests/test_data.py` y las celdas del notebook de EDA.
- Búsqueda y propuesta de las fuentes de `referencias.md`.
- Ayuda para interpretar resultados y errores de ejecución, y para agrupar los errores del modelo.

## Qué hice yo
- Elegí el proyecto y el dataset, y decidí usar solo modelos clásicos para cumplir el plazo.
- Descargué el dataset desde Kaggle y ejecuté todo el código en mi equipo; los resultados del informe provienen de esas ejecuciones.
- Revisé los casos de etiquetas contradictorias y la muestra manual, y aprobé la decisión de eliminar esos casi-duplicados antes de dividir los datos.
- Leí los comentarios de la muestra manual y de los errores, y revisé los resultados de cada experimento.

## Verificación independiente
- **Código:** ejecuté `python -m src.data`, `src.train`, `src.evaluate`, `src.data_civil`, `src.train_combined`, `src.evaluate_combined`, `src.calibrate` y `src.sesgo_validacion`; las 10 pruebas automáticas pasan; leí cada función y puedo explicarla.
- **Referencias:** abrí cada enlace de `referencias.md` y comprobé título, autores y fechas; la licencia del dataset la confirmé en la pestaña Data de Kaggle.
- **Cifras:** las métricas del informe se copiaron de la salida de mis ejecuciones y de `results/experiments.jsonl` y `results/test_eval.json`.

## Limitaciones de la ayuda de IA
- El análisis de errores y las explicaciones de por qué falla el modelo son hipótesis, no resultados medidos.
- Las propuestas de la IA se revisaron y, cuando fue necesario, se corrigieron. Por ejemplo, la primera versión de `src/train.py` falló en mi equipo por un error de paralelismo y se corrigió con `n_jobs=1`; y una lista numerada de `ficha_datos.md` quedó con un número mal puesto y se arregló.