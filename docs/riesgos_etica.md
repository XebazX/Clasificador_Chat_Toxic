# Riesgos, ética y uso responsable

Se basan en lo medido en este proyecto, no en supuestos generales. Modelo final: E-06.

## Matriz de riesgos
| # | Riesgo | Evidencia | Mitigación aplicada | Riesgo residual |
|---|---|---|---|---|
| 1 | **Sesgo contra grupos de identidad** | Con E-02 en Jigsaw, los comentarios sin etiqueta que mencionan "gay" se marcaron el 20,3 % de las veces (n = 59), contra 1,8 % en el total sin etiqueta. **No se midió con E-06.** | Medido y documentado para E-02; la app declara que no debe usarse para sancionar de forma automática. | Alto. No se corrigió y falta medirlo en E-06. |
| 2 | **Error desigual entre etiquetas** | En Civil, F1 de `threat` 0,29 e `identity_hate` 0,37, contra 0,62 de `toxic`. | Se reporta por etiqueta; la app avisa que las categorías raras son menos fiables. | Alto en etiquetas raras. |
| 3 | **Ruido en las etiquetas** | 41 grupos de casi-duplicados con etiquetas contradictorias en Jigsaw; `obscene` definida distinto en Civil. | Se eliminaron los grupos contradictorios antes de dividir; documentado. | Medio. |
| 4 | **Datos personales en el texto** | Una dirección IP en un comentario de la muestra. | Los errores revisados no se versionan (`results/errores_*.csv`); el análisis oculta las IP; los datos no están en el repositorio. | Medio. No se buscaron todos. |
| 5 | **Fuga de datos** | 258 casi-duplicados en Jigsaw. | Limpieza previa, partición con semilla, verificación de no-fuga y prueba usada una sola vez (el script se niega a repetirla). | Bajo. |
| 6 | **Uso indebido o censura** | El modelo puede marcar de más ciertas menciones y no entiende contexto. | Herramienta de apoyo con **revisión humana obligatoria**; no sanciona ni borra. | Medio. |
| 7 | **Cambio de dominio** | E-02 pasó de AUC 0,979 en Jigsaw a 0,880 en Civil. | Se entrenó E-06 con ambos dominios; se declara el alcance (inglés, 2015-2017). | Medio. No se evaluó con chats actuales ni jerga. |
| 8 | **Licencias** | Jigsaw: CC0 con texto CC-SA-3.0; Civil: CC0. | Los datos no se redistribuyen; el repositorio solo incluye el modelo final (4 MB). | Bajo. |
| 9 | **Contenido ofensivo** | Los datos y los errores contienen lenguaje ofensivo. | Los documentos resumen los ejemplos sin reproducir insultos. | Bajo. |
| 10 | **Credenciales publicadas** | Se usaron GitHub y Streamlit Community Cloud. | No hay claves ni tokens en el repositorio; `.gitignore` protege `.env`, `*.key` y `.streamlit/secrets.toml`; el inicio de sesión de GitHub fue por navegador. Verificación de abajo. | Bajo. |
| 11 | **Salidas que parecen más seguras de lo que son** | Una probabilidad alta no equivale a certeza; la calibración no se evaluó en prueba. | La app muestra los límites de uso, recomienda revisión humana y avisa si el texto no parece inglés. | Medio. |
| 12 | **Servicio de terceros** | La demo corre en Streamlit Community Cloud. | La app no guarda los textos escritos; se pide no escribir datos personales. No se controla el registro de la plataforma. | Bajo a medio. |

## Minimización de datos y supervisión humana
- Se usa solo `comment_text` y las etiquetas; el identificador solo sirve de llave.
- La aplicación no guarda los textos que se escriben.
- Toda decisión sobre un usuario o comentario debe tomarla una persona. El sistema es solo educativo.

## Verificación de secretos
```cmd
git log -p | findstr /i /c:"ghp_" /c:"hf_" /c:"api_key" /c:"password"
```
Resultado: sin coincidencias de claves o tokens.