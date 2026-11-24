# Ficha de la base de conocimiento (Anexo A de la rúbrica)

El sistema no consulta documentos en tiempo de ejecución. Su base de conocimiento es el **conjunto de comentarios etiquetados** con el que se entrena y evalúa (Jigsaw + Civil Comments).

| Elemento | Registro | Evidencia |
|---|---|---|
| **Inventario y procedencia** | Jigsaw Toxic Comment Classification Challenge (Jigsaw / Conversation AI, Kaggle; archivo con fecha 18/01/2018, consultado el 23/11/2026) y Civil Comments (Google / Jigsaw, Hugging Face, consultado el 24/11/2026). Licencias: CC0 (el texto de Jigsaw sigue CC-SA-3.0). **Cobertura:** comentarios en inglés de páginas de discusión de Wikipedia y de sitios de noticias, 2015-2017. **Huecos:** sin chats ni jerga actual, sin otros idiomas, pocos positivos en `threat`, `identity_hate` y `severe_toxic`. | `ficha_datos.md` (secciones 1 y 8), `referencias.md` (refs. 1, 2 y 7) |
| **Esquema y metadatos** | CSV con `id`, `comment_text` y 6 etiquetas 0/1. En la preparación se agregan `norm` (texto normalizado) y `fuente` (jigsaw o civil). | `ficha_datos.md` (sección 2), `src/data.py`, `src/data_civil.py` |
| **Curación y calidad** | Normalización de texto, eliminación de 41 grupos de casi-duplicados con etiquetas contradictorias (299 filas quitadas en total) y una sola copia de los demás casi-duplicados. Muestra manual de 30 comentarios. **Anotación:** Jigsaw, por personas, con etiquetas binarias; Civil, fracción de anotadores convertida a 0/1 con corte 0,5. **Acuerdo entre anotadores:** no se midió (Jigsaw solo trae la etiqueta final). | `ficha_datos.md` (secciones 3 a 8) |
| **Construcción reproducible** | `python -m src.data` y `python -m src.data_civil` reconstruyen todo desde las fuentes, con semilla 42. | `README.md`, `configs/config.yaml` |
| **Cómo se emplea** | Entrenamiento: Jigsaw (111.490 filas) + Civil (297.458). Validación: elegir umbrales y calibrar. Prueba: solo evaluación final. Representación: TF-IDF de palabras, 50.000 características. | `decisiones_tecnicas.md`, `bitacora_experimentos.md` |
| **Evaluación del uso** | Conjuntos de prueba definidos antes de ver resultados. Métricas por etiqueta y por subgrupo. Comparación con la línea base (E-01) y entre modelos con y sin los datos de Civil (E-02 contra E-06). | `plan_evaluacion.md`, `evaluacion_final.md`, `evaluacion_E-06.md`, `sesgo_E-06.md` |
| **Seguridad y privacidad** | Los comentarios contienen lenguaje ofensivo y pueden incluir datos personales (se encontró una dirección IP). Los datos no se redistribuyen; el repositorio solo incluye el modelo final. No hay recuperación de documentos, por lo que no aplica la prueba con documentos hostiles. | `riesgos_etica.md` |
| **Mantenimiento** | Versionado en Git; los cambios de datos se registran en la bitácora y en la adenda del plan. Versión del modelo en la aplicación (`E-06`). Los datos de E-06 son: Jigsaw (archivo de 2018) + muestra de Civil (semilla 42, acceso 24/11/2026). Plan de actualización y criterio para reentrenar en `plan_seguimiento.md`. | `plan_seguimiento.md` |

## Señales de alerta (A.2)
- Mezcla de prueba con ajuste: no. Las particiones se definieron antes de modelar y se verifica la no-fuga.
- Consultas de evaluación definidas después de ver resultados: no. Los criterios están en `plan_evaluacion.md`, con fecha.
- Contenido con licencia restrictiva redistribuido: no. Los datos no están en el repositorio.