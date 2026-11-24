# Evaluación final en el conjunto de prueba

Modelo final: **E-02** (TF-IDF 1-gramas + regresión logística, C=1, `class_weight="balanced"`), elegido con validación. Comparado con la línea base **E-01**. Conjunto de prueba: 23.891 comentarios, usado **una sola vez** (`src/evaluate.py`; resultados en `results/test_eval.json`). Umbrales fijados en validación, sin reajustar. Intervalos: bootstrap pareado de 1.000 remuestreos (IC 95 %).

## 1. Resultados globales (macro, promedio de 6 etiquetas)
| Métrica | E-02 (final) | IC 95 % | E-01 (base) |
|---|---|---|---|
| ROC-AUC macro | 0,9794 | [0,9768; 0,9817] | 0,9775 |
| Average Precision macro | 0,6366 | n/d | 0,6274 |
| F1 macro | 0,6123 | [0,5870; 0,6357] | 0,6034 |

**Diferencia final − base:** ROC-AUC +0,0019 (IC 95 % [0,0010; 0,0029]); F1 +0,0089 (IC 95 % [-0,0060; 0,0236]).

## 2. Criterios de éxito (definidos en `plan_evaluacion.md` antes de entrenar)
| Criterio | Resultado |
|---|---|
| 1. ROC-AUC macro mayor que la base | Cumplido |
| 2. F1 macro mayor que la base | Cumplido |
| 3. Mejora fuera del IC del bootstrap | **Parcial**: demostrable en ROC-AUC; **no demostrable en F1** (el IC incluye el cero) |
| 4. Reportar la peor etiqueta | `threat`, F1 = 0,43 |

**Conclusión:** E-02 mejora ligeramente la capacidad de separar comentarios tóxicos de no tóxicos (ROC-AUC) frente a la línea base, pero no se puede afirmar que mejore el F1 macro. La ganancia práctica sobre el modelo más simple es pequeña.

## 3. Resultados por etiqueta (E-02)
| Etiqueta | Positivos en prueba | ROC-AUC | AP | Precisión | Recall | F1 |
|---|---|---|---|---|---|---|
| toxic | 2.279 | 0,9705 | 0,8575 | 0,7871 | 0,7477 | 0,7669 |
| severe_toxic | 240 | 0,9875 | 0,4630 | 0,4253 | 0,6167 | 0,5034 |
| obscene | 1.256 | 0,9838 | 0,8700 | 0,8100 | 0,7842 | 0,7969 |
| threat | 66 | 0,9870 | 0,4287 | 0,5217 | 0,3636 | 0,4286 |
| insult | 1.193 | 0,9745 | 0,7552 | 0,7021 | 0,7091 | 0,7056 |
| identity_hate | 196 | 0,9731 | 0,4453 | 0,4917 | 0,4541 | 0,4721 |

El ROC-AUC es alto en todas, pero la precisión y el recall caen en las etiquetas raras (`threat`, `identity_hate`, `severe_toxic`): el modelo ordena bien, pero con tan pocos ejemplos es difícil fijar un umbral confiable. Matrices de confusión: `results/matrices_confusion.png`.

## 4. Subgrupos
**Longitud del comentario (etiqueta `toxic`; cortes por cuartiles de entrenamiento: 17, 36 y 75 palabras)**
| Grupo | n | Toxic positivos | Precisión | Recall | F1 |
|---|---|---|---|---|---|
| Corto | 6.176 | 939 | 0,835 | 0,830 | 0,832 |
| Mediano-corto | 5.880 | 569 | 0,791 | 0,731 | 0,760 |
| Mediano-largo | 5.869 | 440 | 0,775 | 0,666 | 0,716 |
| Largo | 5.966 | 331 | 0,659 | 0,653 | 0,656 |

El desempeño baja con la longitud. Posible explicación (no verificada): en textos largos el contenido ofensivo pesa menos dentro de la representación TF-IDF.

**Falsos positivos en comentarios sin etiqueta que mencionan términos de identidad** (se cuenta como marcado si alguna etiqueta supera su umbral)
| Término | n | Tasa de falsos positivos |
|---|---|---|
| (todos sin etiqueta) | 21.470 | 1,82 % |
| gay | 59 | **20,34 %** |
| lesbian | 7 | 14,29 % |
| jew | 24 | 8,33 % |
| women | 85 | 7,06 % |
| woman | 56 | 5,36 % |
| christian | 97 | 4,12 % |
| muslim | 56 | 3,57 % |
| jewish | 102 | 2,94 % |
| white | 146 | 2,74 % |
| black | 138 | 1,45 % |
| islam, asian, latino, hispanic, immigrant, atheist, transgender | 1–55 | 0 % (n pequeño en la mayoría) |

Los comentarios que mencionan "gay" se marcan unas 11 veces más que el promedio de comentarios sin etiqueta. Los grupos son pequeños (n entre 1 y 146) y no se probó significancia estadística, así que es una señal de sesgo que hay que vigilar, no una medición exacta. Parte puede deberse a etiquetas ruidosas del dataset. Implicación de uso: no debe usarse para sancionar automáticamente.

## 5. Análisis de errores
[Completar tras revisar `results/errores_toxic.csv`: agrupar falsos negativos y falsos positivos por tipo, con 2 o 3 ejemplos cortos de cada grupo, sin datos personales.]

## 6. Amenazas a la validez
- Una sola partición de prueba y una sola semilla.
- Etiquetas subjetivas (41 grupos de casi-duplicados con etiquetas contradictorias en el EDA).
- Los datos son comentarios de Wikipedia, en inglés y de 2017 o antes; no representan chats actuales.
- Los umbrales de las etiquetas raras se ajustaron con pocos ejemplos en validación.
- Los términos de identidad se buscaron por palabra exacta, sin contexto.

## 7. Casos en los que no debe usarse
- Sanción automática de usuarios o borrado de mensajes sin revisión humana.
- Otros idiomas distintos al inglés.
- Comentarios con sarcasmo, ironía o amenazas sin palabras ofensivas explícitas.
- Contextos donde se discuta legítimamente sobre grupos de identidad (por ejemplo, textos informativos o de apoyo).