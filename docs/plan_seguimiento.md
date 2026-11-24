# Plan de uso y seguimiento

## Uso
- **Entrada:** un comentario en inglés de hasta 5.000 caracteres. Vacío o demasiado largo devuelve un mensaje de error claro; si el texto parece no estar en inglés, se avisa.
- **Salida:** probabilidad estimada por categoría y la lista de categorías que superan su umbral (marcado para revisión humana).
- **Límites:** ver `README.md` y la sección "Límites de uso" de la aplicación.

## Costo y latencia
- **Costo:** 0 USD. Modelo en CPU de 4 MB; alojado en Streamlit Community Cloud gratuito.
- **Latencia:** 1,2 ms por comentario en un equipo local (promedio de 100 llamadas a `clasificar`, sin contar la carga del modelo). En la plataforma gratuita puede variar, y si la app está dormida el primer acceso tarda más.

## Seguimiento (criterios propuestos por el equipo, no medidos)
| Qué se vigila | Cómo | Señal de alerta |
|---|---|---|
| Deriva de datos | Comparar la tasa de comentarios marcados por categoría y la longitud de los textos con las de validación | Cambio grande y sostenido |
| Degradación | Etiquetar a mano una muestra mensual de comentarios reales y calcular F1 por etiqueta | F1 macro cae más de 0,05 frente a la prueba |
| Sesgo | Repetir la revisión de falsos positivos por términos de identidad (`src/sesgo_validacion.py`) | Tasa mucho mayor que la general |
| Vocabulario nuevo | Revisar la proporción de palabras fuera del vocabulario del TF-IDF | Aumento sostenido |

## Reentrenamiento
1. Reunir la muestra etiquetada por personas y sumarla al entrenamiento.
2. Repetir `src.data`, `src.train_combined` y `src.calibrate`, con una partición de prueba **nueva**.
3. Registrar el experimento (E-07, ...) con su plan previo y compararlo con E-06.
4. Actualizar el modelo y su versión (visible en la aplicación como `E-0X`).

Frecuencia sugerida: cada 3 meses o cuando se active una alerta.

## Mantenimiento y control de acceso
- Versionado en Git; solo el modelo final está en el repositorio.
- No hay datos de usuarios guardados, por lo que no hay nada que proteger o borrar.