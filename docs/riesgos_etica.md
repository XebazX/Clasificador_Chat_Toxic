# Riesgos, ética y uso responsable

Los riesgos se basan en lo que se midió en este proyecto (EDA y evaluación en prueba), no en supuestos generales.

## Matriz de riesgos
| # | Riesgo | Evidencia en el proyecto | Mitigación aplicada | Riesgo residual |
|---|---|---|---|---|
| 1 | **Sesgo contra grupos de identidad** | En prueba, los comentarios sin etiqueta que mencionan "gay" se marcaron el 20,3 % de las veces (n = 59), frente a 1,8 % en el total sin etiqueta (`results/subgrupo_identidad.csv`). | Se midió y se documentó en `evaluacion_final.md`; se declara que no debe usarse para sancionar de forma automática. | Alto. No se corrigió el modelo; los grupos son pequeños y no se probó significancia. |
| 2 | **Error desigual entre etiquetas** | F1 de `threat` = 0,43 y `identity_hate` = 0,47, contra 0,77 de `toxic`. | Se reporta por etiqueta y se declara la peor; el aviso de la app indica que las categorías raras son menos fiables. | Alto en etiquetas raras. |
| 3 | **Ruido y subjetividad en las etiquetas** | 41 grupos de casi-duplicados con etiquetas contradictorias; varios "errores" revisados parecen fallas de anotación. | Se eliminaron esos grupos antes de dividir; se documentó en la ficha de datos y en el análisis de errores. | Medio. El ruido restante no se cuantificó. |
| 4 | **Datos personales en el texto** | Se encontró una dirección IP dentro de un comentario de la muestra. | No se publican ejemplos con datos personales; los errores revisados se guardan en `results/errores_toxic.csv`, excluido de Git; en el análisis se taparon las IP. | Medio. No se buscaron todos los datos personales del dataset. |
| 5 | **Fuga de datos** | 258 casi-duplicados en el dataset. | Limpieza previa, partición estratificada con semilla fija, verificación automática de no-fuga y prueba usada una sola vez (el script se niega a repetirla). | Bajo. |
| 6 | **Uso indebido / censura** | El modelo puede marcar de más ciertas menciones (riesgo 1) y no entiende contexto (citas, ironía). | Se declara como herramienta de apoyo con **revisión humana obligatoria**; no sanciona ni borra. | Medio, depende de quien lo use. |
| 7 | **Generalización fuera de dominio** | Entrenado con discusiones de Wikipedia en inglés. | Se declara el alcance (inglés, un solo dominio) en el README y en la app. | Medio. |
| 8 | **Licencia y redistribución del dataset** | CC0 para el conjunto; el texto sigue CC-SA-3.0 de Wikipedia. | El dataset no se sube al repositorio; se descarga desde Kaggle. | Bajo. |
| 9 | **Exposición a contenido ofensivo** | Los datos y los errores contienen lenguaje ofensivo. | El informe resume los ejemplos sin reproducir insultos. | Bajo. |
| 10 | **Credenciales publicadas** | Se usó GitHub (y se usará Hugging Face). | `.gitignore` con `.env` y `*.key`; ningún token se guarda en el repositorio.| Bajo. |
| 11 | **Salidas que parecen más seguras de lo que son** | Una probabilidad alta no equivale a certeza. | La app muestra un aviso de límites de uso y recomienda revisión humana.| Medio. |

## Minimización de datos y supervisión humana
- Se usa solo `comment_text` y las 6 etiquetas; el identificador se mantiene solo como llave.
- La app no guarda los textos que se escriben. [Confirmar cuando exista la app.]
- Toda decisión sobre un usuario o comentario debe tomarla una persona. El sistema es solo educativo.

## Verificación de secretos
Antes de entregar se buscó en el historial de Git que no hubiera claves ni tokens:
```cmd
git log -p | findstr /i "ghp_ hf_ api_key password secret"
```
