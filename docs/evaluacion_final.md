# Evaluación final en el conjunto de prueba

Modelo Evaluado: **E-02** (TF-IDF 1-gramas + regresión logística, C=1, `class_weight="balanced"`), elegido con validación. Comparado con la línea base **E-01**. Conjunto de prueba: 23.891 comentarios, usado **una sola vez** (`src/evaluate.py`; resultados en `results/test_eval.json`). Umbrales fijados en validación, sin reajustar. Intervalos: bootstrap pareado de 1.000 remuestreos (IC 95 %).

> **Actualización del 24/11/2026:** este documento evalúa E-02, el mejor modelo entrenado solo con Jigsaw. El **modelo final del proyecto es E-06**; su evaluación está en `evaluacion_E-06.md` y su revisión de sesgo en `sesgo_E-06.md`.

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

Se revisaron 40 falsos negativos y 40 falsos positivos de la etiqueta `toxic` (`results/errores_toxic.csv`, no versionado por contener lenguaje ofensivo y posibles datos personales). Los falsos negativos se ordenaron de menor a mayor puntaje y los falsos positivos de mayor a menor, así que **son los casos más extremos, no una muestra aleatoria**: no permiten estimar con qué frecuencia ocurre cada tipo de error. Se leyeron en detalle 10 de cada tipo.

### Falsos negativos (comentario etiquetado como tóxico que el modelo no marcó)
| Grupo | Descripción | Ejemplo (resumido) | Acción propuesta |
|---|---|---|---|
| A. Etiqueta dudosa | El texto no parece tóxico; el modelo probablemente acierta. | Queja por bots que borran imágenes; mensaje neutro sobre una canción; debate sobre una secta. | Revisar manualmente la anotación; reportar métricas aparte con etiquetas corregidas. |
| B. Hostilidad suave o sarcasmo | Frustración sin insultos explícitos. | "this one stinks", "a JOKE", "Ridiculous". | Fuera del alcance de TF-IDF; probar un modelo contextual (trabajo futuro). |
| C. Insulto diluido en texto largo | Un insulto aislado dentro de un mensaje largo o con formato de plantilla. | Mensaje de bienvenida que comienza con un insulto homofóbico; mensaje con groserías hacia un grupo nacional. | Puntuar por oraciones y tomar el máximo, o añadir n-gramas de caracteres. |

### Falsos positivos (comentario sin etiqueta que el modelo marcó con puntaje ≈ 1,0)
| Grupo | Descripción | Ejemplo (resumido) | Acción propuesta |
|---|---|---|---|
| D. Probable etiqueta faltante | Ataque personal evidente con etiqueta 0. | Insultos a un moderador ("little hitler", "bullying thug", "Idiot"); mensaje de odio hacia un grupo. | Revisar una muestra de falsos positivos de puntaje alto; el "error" puede ser de la anotación. |
| E. Contenido sexual o vandalismo | Texto explícito etiquetado como 0. | Relato sexual en una página de discusión. | Evaluar si el dataset etiqueta esa categoría de forma consistente. |
| F. Cita o mención del lenguaje | El texto cita o enlaza reglas de cortesía o críticas a administradores. | Mensaje que cita las políticas de Wikipedia contra ataques personales. | Falso positivo genuino por palabras clave sin contexto; modelo contextual (trabajo futuro). |

### Lectura
- Una parte importante de los errores revisados **parece originarse en la anotación** (grupos A, D y E), lo que coincide con los 41 grupos de casi-duplicados con etiquetas contradictorias del EDA. Esto limita el rendimiento que se puede esperar y significa que el F1 reportado subestima el desempeño real; sin embargo, esta afirmación **no está medida**: se basa en una lectura de 20 casos extremos.
- Los errores que sí son del modelo (grupos B, C y F) apuntan a su principal límite: representa el texto como bolsa de palabras ponderadas y no entiende contexto, ironía ni citas.
- Una explicación posible, pero **no verificada**, del peor desempeño en comentarios largos es la dilución del insulto dentro de más texto.
- Esta revisión no demuestra causalidad: las explicaciones de cada grupo son hipótesis que habría que probar con experimentos (por ejemplo, puntuar por oraciones y comparar).

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