# Planteamiento del proyecto

## 1. Resumen (100–180 palabras)
Este proyecto desarrolla un clasificador de comentarios tóxicos para apoyar la moderación de chats y foros en línea. A partir del conjunto de datos Jigsaw Toxic Comment Classification, se entrena un modelo supervisado de procesamiento de lenguaje natural que recibe un comentario en texto y devuelve la probabilidad de que sea tóxico y de que pertenezca a subtipos como amenaza, insulto, obscenidad u odio por identidad. Primero se establece una línea base sencilla con TF-IDF y regresión logística, y luego se comparan variantes para medir si mejoran frente a ella. La evaluación usa métricas adecuadas al desbalance de clases (F1, precisión, recall y ROC-AUC), con análisis por tipo de toxicidad y de errores. El sistema es una herramienta de apoyo con revisión humana, no un moderador automático, y se entrega con una demo, documentación reproducible y un análisis de riesgos éticos.

## 2. Problema
En plataformas con muchos mensajes, los moderadores humanos no alcanzan a revisarlos todos. Se necesita un filtro que marque los comentarios probablemente ofensivos para que una persona los revise primero.

## 3. Usuario y contexto
- **Usuario:** moderador de una comunidad en línea (chat, foro o comentarios).
- **Contexto:** revisión de mensajes en texto, en inglés.
- **Entrada:** un comentario en texto plano.
- **Salida:** probabilidad de toxicidad por categoría (toxic, severe_toxic, obscene, threat, insult, identity_hate) y una marca de "revisar".

## 4. Pregunta del proyecto
¿Un modelo supervisado de texto puede detectar comentarios tóxicos mejor que una línea base simple (TF-IDF + regresión logística), medido con F1 macro y ROC-AUC en un conjunto de prueba no visto?

## 5. Tipo de tarea de ML
Clasificación de texto **multietiqueta** (un comentario puede tener varias etiquetas a la vez). Aprendizaje supervisado.

**Alternativa no-ML:** una lista de palabras prohibidas. Es simple y rápida, pero falla con sarcasmo, insultos sin palabras clave, variaciones de escritura y falsos positivos (ej. "I will kill u soon(si estan en jugando shooter o relacionados)"). Por eso se justifica un modelo que aprenda del contexto.

## 6. Objetivos
**General:** construir y evaluar un clasificador multietiqueta de comentarios tóxicos que supere una línea base simple y sea reproducible.

**Específicos (medibles):**
1. Analizar el dataset y documentar desbalance, duplicados y sesgos (ficha de datos + EDA).
2. Entrenar una línea base (TF-IDF + regresión logística) y reportar sus métricas.
3. Ejecutar mínimo 5 experimentos controlados, cambiando una variable a la vez.
4. Superar la línea base en F1 macro y ROC-AUC en el conjunto de prueba (criterio fijado antes de ver resultados, ver `plan_evaluacion.md`).
5. Entregar una demo funcional con instrucciones de uso y análisis de errores.

## 7. Qué NO resuelve
- No funciona para español ni otros idiomas (el dataset es en inglés).
- No reemplaza al moderador humano ni toma decisiones de sanción.
- No detecta imágenes, audio, ni contexto de conversaciones largas.
- No garantiza ausencia de sesgo contra grupos o dialectos específicos.

## 8. Glosario
Va en `docs/glosario.md`.