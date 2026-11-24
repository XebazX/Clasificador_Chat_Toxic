# Lista de verificación técnica (Anexo B de la rúbrica)

## Repositorio y código (criterio 10)
- [x] README con objetivo, alcance, requisitos, instalación y ejecución paso a paso.
- [x] Estructura: docs/, notebooks/, src/, tests/, results/, configs/, requirements.txt.
- [x] Dependencias con versiones fijadas; semilla y configuración en `configs/config.yaml`.
- [x] Pruebas automáticas que pasan (`python -m pytest`).
- [x] Sin credenciales: búsqueda de secretos en el historial sin coincidencias.
- [ ] README probado en un entorno limpio (Google Colab).

## Datos y base de conocimiento (criterios 3, 4, 5)
- [x] Ficha de datos completa y licencia verificada (`ficha_datos.md`, secciones 1 y 8).
- [x] Notebook de exploración (`notebooks/01_eda.ipynb`).
- [x] Particiones antes de modelar, transformaciones ajustadas solo con entrenamiento y verificación de no-fuga (`src/data.py`).
- Nota sobre la base de conocimiento: el sistema no consulta documentos; la base es el conjunto etiquetado (Jigsaw + Civil Comments) y su guía de anotación es la de cada fuente.

## Entrenamiento y evaluación (criterios 6, 7, 8, 9)
- [x] Comparación de enfoques y línea base primero (`decisiones_tecnicas.md`).
- [x] Bitácora con 5 experimentos controlados, más E-06, con resultados desfavorables (`bitacora_experimentos.md`).
- [x] Diagnóstico de sobreajuste y registro de tiempos (`results/experiments.jsonl`).
- [x] Modelo final exportado y versionado (`models/E-06.joblib`).
- [x] Plan de evaluación previo y pruebas usadas según lo declarado (`plan_evaluacion.md`, `evaluacion_final.md`, `evaluacion_E-06.md`).
- [x] Métricas por subgrupo, medida de variabilidad y análisis de errores con ejemplos agrupados.
- [ ] Revisión de sesgo por términos de identidad en E-06 (`src/sesgo_validacion.py`).

## Aplicación y entrega (criterios 11, 12, 13)
- [x] Aplicación en línea que carga el modelo: https://toxic-scanner.streamlit.app/
- [x] Entradas validadas, salidas definidas, mensajes claros y límites de uso informados.
- [x] Medición de latencia y costo (`plan_seguimiento.md`: 1,2 ms por comentario; 0 USD).
- [x] Plan de seguimiento (`plan_seguimiento.md`).
- [x] Matriz de riesgos y declaración de uso de IA (`riesgos_etica.md`, `declaracion_ia.md`).
- [ ] Informe final y presentación breve.
- [ ] Sustentación: ensayar la explicación del código, del modelo y de las decisiones.