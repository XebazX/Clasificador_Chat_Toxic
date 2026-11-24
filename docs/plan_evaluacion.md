# Plan de evaluación

Definido el 23/11/2026, antes de entrenar cualquier modelo.

## 1. Costo de los errores
- **Falso negativo** (comentario tóxico que pasa): el moderador no lo ve y el daño queda visible.
- **Falso positivo** (comentario normal marcado): el moderador pierde tiempo y se corre el riesgo de censurar a usuarios sin razón.
- El sistema solo **marca para revisión humana**, no sanciona. Por eso se prioriza el **recall** sin dejar caer demasiado la precisión.

## 2. Partición de datos
- Fuente: `train.csv` después de la preparación de la ficha de datos (sección 6).
- Proporción: **70 % entrenamiento / 15 % validación / 15 % prueba**.
- Estratificada por una marca "tiene alguna etiqueta" para mantener proporciones similares.
- Semilla fija: `42` (guardada en `configs/config.yaml`).
- La prueba **no se toca** hasta la evaluación final y se usa **una sola vez**.
- Transformaciones (TF-IDF) ajustadas solo con entrenamiento.
- Los hiperparámetros y el umbral de decisión se eligen con validación o validación cruzada, nunca con la prueba.

## 3. Métricas
| Métrica | Para qué |
|---|---|
| ROC-AUC macro (promedio de las 6 etiquetas) | Métrica principal: separación entre tóxico y no tóxico sin depender del umbral. |
| Average Precision (PR-AUC) macro | Complementa a ROC-AUC con clases muy desbalanceadas. |
| F1 macro con umbral ajustado en validación | Resultado operativo; da el mismo peso a etiquetas raras como `threat`. |
| Precisión y recall por etiqueta | Ver en cuáles etiquetas falla el modelo. |
| Matriz de confusión por etiqueta | Análisis de errores. |

No se usa accuracy como métrica principal: con 89,83 % de comentarios sin etiqueta, un modelo que nunca marque nada tendría una exactitud alta sin servir.

## 4. Criterio de éxito (fijado antes de ver resultados)
El modelo final se considera exitoso si, en el conjunto de **prueba**:
1. En la prueba de Civil Comments (5 etiquetas), E-06 supera a E-02 en ROC-AUC macro y en F1 macro.
2. La diferencia de ROC-AUC tiene un IC 95 % (bootstrap pareado) que no incluye el cero.
3. En la prueba de Jigsaw (6 etiquetas, segundo uso, solo descriptivo), E-06 no pierde más de 0,005 de ROC-AUC macro frente a E-02.
Si no se cumplen, se reporta tal cual y el modelo final sigue siendo E-02.

## 5. Variabilidad
- **Validación cruzada de 5 particiones** sobre el conjunto de entrenamiento para comparar experimentos (media ± desviación estándar).
- **Bootstrap** (1.000 remuestreos) sobre la prueba para el intervalo de confianza del 95 % del modelo final y de la línea base.

## 6. Desempeño por subgrupo
- Por **cada una de las 6 etiquetas**.
- Por **longitud del comentario** (cortos / medianos / largos, según cuartiles).
- Por **menciones de términos de identidad** (religión, género, etnia, orientación): se revisa si el modelo marca más comentarios normales que los mencionan. Esto responde al riesgo de sesgo de la referencia 5.

## 7. Experimentos planeados (se registran en `bitacora_experimentos.md`)
Cada uno cambia **una sola variable** respecto al anterior.
| ID | Qué cambia |
|---|---|
| E-01 | Línea base: TF-IDF palabras (1-gram) + regresión logística |
| E-02 | Igual que E-01, con `class_weight="balanced"` |
| E-03 | Igual que E-02, con n-gramas (1,2) |
| E-04 | Igual que E-03, ajuste del hiperparámetro `C` (validación cruzada) |
| E-05 | Igual que E-04, cambiando el clasificador a LinearSVC |

Se conservan los resultados desfavorables.

## 8. Qué no se hace
- No se ajusta nada con el conjunto de prueba.
- No se cambian estos criterios después de ver resultados; si hay que cambiarlos, se anota el cambio, la fecha y el motivo.

## Adenda del 23/11/2026: experimento E-06 (definida antes de entrenarlo)
**Motivo:** al probar la aplicación, los puntajes de comentarios informales salían inflados y se quiso comprobar si más datos, de otro dominio, ayudan. Se suma una muestra de Civil Comments (comentarios de sitios de noticias, 2015–2017, CC0) a los datos de Jigsaw.
**Datos:** entrenamiento = Jigsaw (train) + Civil Comments (300 mil); validación = Jigsaw (val) + Civil Comments (30 mil); etiquetas de Civil Comments convertidas a 0/1 con corte 0,5.
**Modelo:** igual a E-02 (única variable que cambia: los datos de entrenamiento).
**Prueba:** la prueba de Civil Comments (30 mil, no usada antes). La prueba de Jigsaw ya se usó una vez; sus resultados en E-06 se reportan solo como dato descriptivo y no se usan para decidir.
**Criterio de éxito (fijado antes de ver resultados):**
1. E-06 supera a E-02 en ROC-AUC macro y en F1 macro sobre la prueba de Civil Comments.
2. La diferencia de ROC-AUC tiene un IC 95 % (bootstrap) que no incluye el cero.
3. En la prueba de Jigsaw, E-06 no pierde más de 0,005 de ROC-AUC macro frente a E-02.
Si no se cumplen, se reporta tal cual y el modelo final sigue siendo E-02.