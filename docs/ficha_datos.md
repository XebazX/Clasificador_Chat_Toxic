# Ficha de datos

## 1. Identificación
- **Nombre:** Toxic Comment Classification Challenge (Jigsaw / Conversation AI)
- **Fuente:** https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data
- **Fecha de acceso:** 23/11/2026 (descarga manual desde Kaggle; archivo con fecha 18/01/2018)
- **Licencia:** el dataset se publica bajo CC0 y el texto de los comentarios sigue la licencia CC-SA-3.0 de Wikipedia (según la dataset card de Hugging Face, ref. 2). [Confirmar también en la pestaña Data de Kaggle y las reglas de la competencia.]
- **Formato / archivo usado:** CSV, `train.csv`
- **Tamaño:** 159.571 comentarios, 8 columnas, 68.802.655 bytes (68,8 MB)
- **Idioma:** inglés
- **Distribución en el repositorio:** el archivo NO se sube a GitHub (carpeta `data/` en `.gitignore`); se descarga desde Kaggle siguiendo el README.

## 2. Estructura
- **Unidad de análisis:** un comentario de una página de discusión de Wikipedia.
- **Variable de entrada:** `comment_text` (texto libre).
- **Identificador:** `id`.
- **Etiquetas (multietiqueta, valores 0/1):** `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`.
- **Origen de las etiquetas:** anotadores humanos.
- **Datos sensibles:** los comentarios contienen lenguaje ofensivo e insultos hacia grupos. En la muestra revisada apareció una dirección IP dentro de un texto (comentario 146861), por lo que pueden existir otros datos personales incrustados.

## 3. Hallazgos del EDA (`notebooks/01_eda.ipynb`)
| Hallazgo | Resultado |
|---|---|
| Dimensiones | 159.571 filas × 8 columnas |
| Faltantes | 0 en todas las columnas |
| Duplicados exactos en texto | 0 |
| Casi-duplicados (minúsculas y espacios normalizados) | 258 (≈0,16 %) |
| Grupos de casi-duplicados con etiquetas distintas | 41 |
| Comentarios sin ninguna etiqueta | 89,83 % |
| toxic | 15.294 (9,58 %) |
| obscene | 8.449 (5,29 %) |
| insult | 7.877 (4,94 %) |
| severe_toxic | 1.595 (1,00 %) |
| identity_hate | 1.405 (0,88 %) |
| threat | 478 (0,30 %) |
| Longitud (palabras) | media 67,3; mediana 36; mínimo 1; máximo 1.411 |

## 4. Revisión manual de etiquetas
Muestra de 30 comentarios (`random_state=42`):
- Solo 2 tenían alguna etiqueta.
- El 25255 (toxic + identity_hate) coincide con el texto completo, que ataca a un grupo.
- El 146861 (sarcasmo hostil, sin insultos directos) y el 96229 (reclamo agresivo, sin insultos claros) están en 0; es una decisión discutible.
- Con 30 casos solo se pueden señalar posibles inconsistencias, no medir su frecuencia.

## 5. Riesgos identificados
- **Desbalance fuerte:** casi 9 de cada 10 comentarios no tienen etiqueta y `threat` tiene solo 478 ejemplos (unas 32 veces menos que `toxic`). Un modelo que siempre prediga "no tóxico" tendría cerca de 90 % de exactitud, por eso no se usa accuracy como métrica principal.
- **Ruido en las etiquetas:** 41 grupos de casi-duplicados tienen etiquetas distintas entre sí, y hay casos ambiguos en la muestra. El techo de desempeño está limitado por etiquetas subjetivas; algunos "errores" del modelo pueden ser desacuerdos con la anotación.
- **Sesgo de representación:** el texto viene de discusiones de Wikipedia, no de chats ni redes. El modelo puede generalizar mal a otros contextos y asociar menciones de ciertos grupos con toxicidad (ref. 5).
- **Riesgo de fuga:** hay 258 casi-duplicados; si cayeran en entrenamiento y prueba se inflaría el resultado.
- **Privacidad:** posibles datos personales dentro del texto (por ejemplo, direcciones IP). No se publican ejemplos con ellos en los resultados.
- **Textos largos:** son raros los comentarios de más de 1.000 palabras; se definirá un tope de longitud en la preparación.

## 6. Decisiones de preparación (se ejecutan antes de dividir los datos)
1. Eliminar todos los comentarios de los 41 grupos de casi-duplicados con etiquetas contradictorias.
2. En los demás casi-duplicados, conservar una sola copia.
3. Dividir en entrenamiento / validación / prueba con semilla fija, definido en `docs/plan_evaluacion.md`.
4. Ajustar las transformaciones (por ejemplo, TF-IDF) únicamente con el conjunto de entrenamiento.
5. Mantener el conjunto de prueba intacto hasta la evaluación final.
6. No se usa `test.csv` de Kaggle: parte de sus comentarios no fue incluida en la calificación original y sus etiquetas se publicaron después del cierre. La prueba se construye a partir de `train.csv`.

## 7. Resultado de la preparación (`python -m src.data`, semilla 42)
- Filas antes: 159.571 | después de limpiar: 159.272 (quitadas: 299 = 258 casi-duplicados sobrantes + 41 filas extra de grupos con etiquetas contradictorias).
- Entrenamiento: 111.490 filas | validación: 23.891 | prueba: 23.891 (≈70 / 15 / 15 %).
- Comentarios con alguna etiqueta: 10,13 % en las tres particiones (estratificación verificada).
- Verificación automática de no-fuga (ningún texto normalizado en más de una partición): OK.
- Pruebas automáticas (`python -m pytest`): 3 aprobadas.