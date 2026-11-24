# Bitácora de experimentos

Datos: `data/processed/` (70/15/15, semilla 42, 111.490 entrenamiento / 23.891 validación). Validación cruzada de 5 particiones sobre entrenamiento. Todos usan TF-IDF con 50.000 características como máximo y clasificador uno-contra-resto (una salida por etiqueta). El conjunto de prueba no se usó en ningún experimento.
Fecha, commit, parámetros, umbrales y tiempos exactos de cada corrida: `results/experiments.jsonl`. Modelos guardados en `models/E-0X.joblib` (no se versionan en Git por tamaño).

| ID | Qué cambia (una variable) | CV ROC-AUC macro | Val ROC-AUC macro | Val F1 macro | Train ROC-AUC | Tiempo |
|---|---|---|---|---|---|---|
| E-01 | Línea base: 1-gramas + regresión logística (C=1) | 0,9769 ± 0,0012 | 0,9780 | 0,5978 | 0,9898 | 72 s |
| E-02 | + `class_weight="balanced"` | 0,9793 ± 0,0009 | 0,9809 | 0,6101 | 0,9955 | 211 s |
| E-03 | + n-gramas (1,2) | 0,9776 ± 0,0007 | 0,9797 | 0,6031 | 0,9963 | 290 s |
| E-04 | + búsqueda de C en {0,3; 1; 3; 10} | 0,9776 ± 0,0007 | 0,9797 | 0,6031 | 0,9963 | 211 s |
| E-05 | Clasificador LinearSVC (C=1, resto igual a E-04) | 0,9666 ± 0,0018 | 0,9656 | 0,5874 | 0,9992 | 365 s |

## Lectura de los resultados
- **E-01 (línea base):** resultado estable entre particiones (desviación 0,0012). Brecha train−val de 0,012: sobreajuste leve. El F1 macro (0,598) es mucho menor que el AUC porque las etiquetas raras (`threat` 0,30 %, `severe_toxic` 1,00 %, `identity_hate` 0,88 %) bajan el promedio.
- **E-02:** balancear las clases mejoró AUC, F1 y CV. Es el mejor experimento. Brecha train−val 0,015.
- **E-03 (desfavorable):** los n-gramas no mejoraron frente a E-02 (la diferencia está dentro de la variabilidad de la validación cruzada), aumentan el tiempo y el sobreajuste (brecha 0,017).
- **E-04 (sin efecto):** la búsqueda de C (val ROC-AUC: C=0,3 → 0,9783; C=1 → 0,9797; C=3 → 0,9782; C=10 → 0,9729) confirmó C=1, que ya se usaba, por lo que el resultado es idéntico a E-03. C=10 sobreajusta más. El ajuste se hizo solo con validación.
- **E-05 (desfavorable):** LinearSVC fue peor en todas las métricas y sobreajusta más (brecha 0,034).
- **Diagnóstico de sobreajuste:** hay sobreajuste leve en todos (train > validación), más marcado con SVC. No hay subajuste: el AUC es alto en las tres particiones.

## Decisión
Modelo final candidato: **E-02**, elegido con datos de **validación**. Es el mejor en las tres métricas, es más simple que E-03 y más rápido. La evaluación final en prueba se hará **una sola vez** con este modelo y los umbrales ya fijados en validación (ver `plan_evaluacion.md`).

## Limitaciones de esta bitácora
- Cada experimento se corrió una vez con semilla 42; la variabilidad se estima solo con la validación cruzada.
- El F1 macro usa umbrales ajustados sobre la misma validación, por lo que es algo optimista.