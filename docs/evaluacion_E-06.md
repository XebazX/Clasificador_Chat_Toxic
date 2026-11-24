# Evaluación final de E-06 (datos combinados Jigsaw + Civil Comments)

Definida antes de entrenar en la adenda de `plan_evaluacion.md` (24/11/2026). E-06 repite E-02 (TF-IDF 1-gramas + regresión logística, C=1, `class_weight="balanced"`); la única variable que cambia son los datos de entrenamiento: 111.490 filas de Jigsaw + 297.458 de Civil Comments (72,7 % del total; 5 filas quitadas por solaparse con validación o prueba). Los umbrales se ajustaron en una validación mezclada (Jigsaw + Civil). Resultados: `results/test_eval_E-06.json` y tablas `results/E-0*_por_etiqueta_*.csv`. IC 95 %: bootstrap pareado de 1.000 remuestreos.

## 1. Prueba de Civil Comments (29.927 comentarios, 5 etiquetas; criterio de éxito)
`severe_toxic` no se evalúa aquí: tiene 0 positivos en esta prueba.
| Métrica | E-06 | IC 95 % | E-02 | IC 95 % |
|---|---|---|---|---|
| ROC-AUC macro | 0,9545 | [0,9476; 0,9608] | 0,8801 | [0,8688; 0,8910] |
| F1 macro | 0,4724 | [0,4430; 0,4988] | 0,2137 | [0,1892; 0,2399] |

**Diferencia E-06 − E-02:** ROC-AUC +0,0744 (IC 95 % [0,0655; 0,0834]); F1 +0,2586 (IC 95 % [0,2255; 0,2884]).

Por etiqueta (E-06): 
| Etiqueta | Positivos | ROC-AUC | Precisión | Recall | F1 |
|---|---|---|---|---|---|
| toxic | 2.351 | 0,9381 | 0,6228 | 0,6202 | 0,6215 |
| obscene | 150 | 0,9634 | 0,4313 | 0,4600 | 0,4452 |
| threat | 71 | 0,9584 | 0,2941 | 0,2817 | 0,2878 |
| insult | 1.737 | 0,9522 | 0,6048 | 0,6759 | 0,6384 |
| identity_hate | 188 | 0,9603 | 0,3094 | 0,4574 | 0,3691 |

## 2. Prueba de Jigsaw (23.891 comentarios, 6 etiquetas; segundo uso, solo descriptivo)
| Métrica | E-06 | IC 95 % | E-02 | IC 95 % |
|---|---|---|---|---|
| ROC-AUC macro | 0,9805 | [0,9782; 0,9826] | 0,9794 | [0,9768; 0,9817] |
| F1 macro | 0,6171 | [0,5939; 0,6385] | 0,6123 | [0,5870; 0,6357] |

**Diferencia E-06 − E-02:** ROC-AUC +0,0011 (IC 95 % [-0,0005; 0,0028]); F1 +0,0048 (IC 95 % [-0,0120; 0,0227]). Ninguna es demostrable.
Cambios por etiqueta en F1: `threat` 0,43 → 0,51; `severe_toxic` 0,50 → 0,49; `insult` 0,71 → 0,67 (más recall, menos precisión).

## 3. Criterios de éxito (fijados antes de entrenar)
| Criterio | Resultado |
|---|---|
| 1. En la prueba de Civil, E-06 supera a E-02 en AUC y F1 | Cumplido |
| 2. El IC 95 % de la diferencia de AUC en Civil no incluye el cero | Cumplido |
| 3. En la prueba de Jigsaw, E-06 no pierde más de 0,005 de AUC | Cumplido (+0,0011) |

**Decisión:** E-06 reemplaza a E-02 como modelo final. E-02 se conserva en la bitácora como la mejor opción entrenada solo con Jigsaw.

## 4. Lectura y límites
- La mejora en Civil **no significa que más datos siempre ayuden**: E-02 no había visto comentarios de ese dominio. Lo que se demuestra es que un modelo entrenado solo con Wikipedia generaliza mal a comentarios de sitios de noticias (AUC 0,88) y que añadir datos de ese dominio lo corrige.
- **Los umbrales no se transfieren entre dominios.** En Civil, E-02 con sus umbrales de Jigsaw casi no detecta (recall de `threat` 0,03 y de `insult` 0,15), aunque su ROC-AUC es razonable.
- En Jigsaw, E-06 mantiene el desempeño (sin pérdida demostrable), pero tampoco lo mejora de forma demostrable.
- El desempeño absoluto en Civil sigue siendo modesto (F1 macro 0,47; `threat` 0,29; `identity_hate` 0,37; pocos positivos por etiqueta).
- Las etiquetas de Civil se derivaron con un corte de 0,5 sobre la fracción de anotadores. `obscene` está definida de forma distinta (0,54 % de positivos en Civil contra 5,29 % en Jigsaw), lo que introduce ruido de etiqueta.
- Civil Comments son comentarios de sitios de noticias de 2015 a 2017, no chats: no se evaluó con texto informal actual (jerga, abreviaturas).
- El sesgo por términos de identidad se revisó solo en validación (ver docs/sesgo_E-06.md) y empeoró respecto a E-02.
- Un solo entrenamiento sin validación cruzada, con semilla 42.