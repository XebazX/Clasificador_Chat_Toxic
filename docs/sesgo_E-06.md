# Revisión de sesgo por términos de identidad (E-06)

Script: `src/sesgo_validacion.py`. Resultados completos: `results/sesgo_validacion_E-06.csv`. Se usó **solo la validación** (Jigsaw: 21.470 comentarios sin etiqueta; Civil: 27.464), por lo que no se gastó ninguna prueba. Se mide qué fracción de los comentarios **sin etiqueta** que mencionan cada término (palabra exacta, sin distinguir mayúsculas) el modelo marca igualmente (falsos positivos). Se muestran los términos con al menos 30 comentarios; IC 95 % de Wilson.

## Jigsaw (tasa global de falsos positivos: E-02 1,7 %; E-06 2,1 %)
| Término | n | E-02 | E-06 (IC 95 %) | E-06 / global |
|---|---|---|---|---|
| muslim | 75 | 1,3 % | 13,3 % (7,4–22,8) | 6,4× |
| islam | 68 | 2,9 % | 13,2 % (7,1–23,3) | 6,4× |
| jewish | 98 | 5,1 % | 11,2 % (6,4–19,0) | 5,4× |
| christian | 130 | 0,8 % | 9,2 % (5,4–15,4) | 4,5× |
| gay | 50 | 18,0 % | 38,0 % (25,9–51,8) | 18,4× |
| black | 133 | 3,8 % | 12,8 % (8,1–19,5) | 6,2× |
| white | 150 | 3,3 % | 11,3 % (7,2–17,4) | 5,5× |
| asian* | 34 | 5,9 % | 5,9 % (1,6–19,1) | 2,8× |
| woman | 59 | 5,1 % | 10,2 % (4,7–20,5) | 4,9× |
| women | 103 | 1,9 % | 8,7 % (4,7–15,8) | 4,2× |

## Civil (tasa global de falsos positivos: E-02 2,2 %; E-06 3,9 %)
| Término | n | E-02 | E-06 (IC 95 %) | E-06 / global |
|---|---|---|---|---|
| muslim | 112 | 1,8 % | 24,1 % (17,1–32,8) | 6,2× |
| islam | 67 | 4,5 % | 31,3 % (21,5–43,2) | 8,1× |
| jewish | 47 | 2,1 % | 14,9 % (7,4–27,7) | 3,8× |
| christian | 127 | 0,8 % | 17,3 % (11,7–24,8) | 4,5× |
| gay | 66 | 15,2 % | 36,4 % (25,8–48,4) | 9,4× |
| black | 230 | 7,0 % | 27,4 % (22,0–33,5) | 7,1× |
| white | 453 | 5,5 % | 24,3 % (20,6–28,4) | 6,3× |
| woman* | 208 | 4,3 % | 6,2 % (3,7–10,4) | 1,6× |
| women | 420 | 3,6 % | 10,0 % (7,5–13,2) | 2,6× |
| immigrant* | 45 | 0,0 % | 6,7 % (2,3–17,9) | 1,7× |

\* Su intervalo incluye la tasa global: no se distingue del promedio.
Términos con menos de 30 comentarios (no interpretables): jew, lesbian, transgender, latino, hispanic, immigrant (Jigsaw), atheist, jew, lesbian, transgender, asian, latino, hispanic y atheist (Civil, salvo los ya indicados).

## Lectura
- E-06 marca como tóxicos, sin serlo según la etiqueta, muchos más comentarios que mencionan grupos de identidad que el promedio (entre 3,8 y 9,4 veces en Civil y entre 4,2 y 18,4 veces en Jigsaw para los términos con intervalos que excluyen la tasa global). En Jigsaw, E-02 tenía esa tasa mucho más baja para varios términos (por ejemplo "muslim": 1,3 % frente a 13,3 %), así que **el sesgo aumentó al sumar Civil Comments**.
- "gay" es el término con mayor tasa en las dos fuentes y en los dos modelos.
- En Civil la comparación con E-02 no es equivalente: sus umbrales se ajustaron en Jigsaw y marca poco en general.

## Posibles causas (hipótesis, **no verificadas**)
1. En los comentarios de noticias, las menciones a grupos aparecen a menudo en discusiones hostiles y el modelo asocia el término con toxicidad.
2. El corte de 0,5 sobre la fracción de anotadores deja como "no tóxicos" comentarios que parte de los anotadores sí marcó; parte de estos falsos positivos pueden ser ofensivos de verdad.
3. TF-IDF representa palabras sueltas y no distingue el uso respetuoso del ofensivo.
Verificarlo requiere leer ejemplos de estos falsos positivos y un experimento controlado.

## Límites de esta revisión
- Solo validación, y los umbrales se ajustaron sobre esa misma validación (las tasas son algo optimistas).
- Términos buscados como palabra exacta, sin contexto; un comentario puede mencionar varios.
- Solo se miden falsos positivos; no se midió si el modelo deja pasar más contenido tóxico dirigido a algunos grupos.
- No se probó significancia entre términos, solo intervalos; no se corrigió por comparaciones múltiples.

## Decisión
E-06 se mantiene como modelo final (el sesgo no estaba entre los criterios de éxito fijados de antemano, y E-02 generaliza mal a otro dominio), con estas condiciones: la aplicación advierte este comportamiento, el sistema solo marca para revisión humana y nunca sanciona de forma automática. Mitigarlo (por ejemplo, ponderar muestras o usar las anotaciones de identidad de Civil Comments) queda como trabajo futuro, con un experimento nuevo (E-07) y su propio plan.