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
1. Su **ROC-AUC macro** es mayor que el de la línea base.
2. Su **F1 macro** es mayor que el de la línea base.
3. La mejora sobre la línea base **no queda dentro del intervalo de confianza** del bootstrap (ver sección 5); si queda dentro, se reporta como "sin mejora demostrable".
4. Se reporta honestamente el desempeño de la peor etiqueta, sin esconderlo detrás del promedio.

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