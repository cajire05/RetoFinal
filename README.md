# Auditoría de MFA con Ollama

Prototipo universitario que consulta políticas ficticias y un inventario simulado de cuentas. Audita cuentas activas, presenta los hallazgos con citas y señala si falta evidencia para determinar el cumplimiento o el conteo exacto. Usa Python 3.10 o posterior y la API HTTP local de Ollama. Solo requiere la biblioteca estándar de Python.

- [Diagrama y riesgos del diseño](docs/arquitectura.md)
- [Comparación y resultados esperados de los seis casos](docs/resultados.md)
- [Políticas ficticias](datos/politicas.md), [registro de fuentes autorizadas](datos/fuentes_politicas.json) y [CSV simulado](datos/cuentas.csv)

## Ejecutar una auditoría

Con Ollama instalado y escuchando en `127.0.0.1:11434`, descarga el modelo predeterminado. Si Ollama aún no está en ejecución, inicia `ollama serve` en otra terminal. Consulta la [documentación de la API de chat](https://docs.ollama.com/api/chat) y la [ficha del modelo](https://ollama.com/library/qwen2.5:3b).

```powershell
ollama pull qwen2.5:3b
python auditoria.py --modo simple --ambito finanzas
python auditoria.py --modo doble --ambito finanzas
```

`--modelo` selecciona cualquier modelo local que admita salidas estructuradas. También puedes definir `OLLAMA_MODEL`. El argumento en la línea de comandos tiene prioridad. `--ambito todas` audita el inventario completo. El ámbito se toma del argumento y `--pregunta` proporciona el texto para la búsqueda y el análisis.

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"
python auditoria.py --modo doble --ambito contratistas --pregunta "¿Cuántas cuentas activas de contratistas están sin MFA?"
python auditoria.py --modo simple --ambito "recursos humanos"
```

## Evaluar los dos modos

```powershell
python evaluar.py --solo-datos --salida "docs/verificacion-local.md"
python evaluar.py --modelo qwen2.5:3b --potencia-w 65 --tarifa-kwh 900
```

`--solo-datos` coteja los conteos, la recuperación de las fuentes esperadas y la inclusión del señuelo en el caso de contratistas. La segunda orden realiza un calentamiento y ejecuta los seis casos en ambos modos. Reemplaza `docs/resultados.md` con las tablas por caso y por modo. Usa `--salida` para conservar otro informe. La potencia y la tarifa son supuestos configurables para estimar el costo eléctrico.

Los casos y las respuestas esperadas están en `datos/casos.json`. El informe mide por separado la exactitud del estado y el conteo propuestos, la corrección de las citas trazadas y la aceptación por el validador común. La [primera corrida](docs/resultados-antes.md) queda como referencia para comparar cambios.

## Cómo funciona

- El RAG recupera hasta tres fragmentos por coincidencia de términos. Python comprueba su identidad y huella SHA-256 contra `datos/fuentes_politicas.json` y selecciona las políticas admisibles por función y ámbito. Para registrar una edición aprobada, actualiza la huella del encabezado sin `## `, seguido de un salto LF y el cuerpo con los espacios exteriores eliminados. La nota señuelo se recupera como datos de contexto.
- La herramienta de solo lectura devuelve el agregado de las cuentas activas y su fuente `CSV-MFA`. El esquema exige `null` como total exacto cuando el inventario del ámbito está vacío o tiene estados desconocidos. Python cita la fuente al presentar los datos verificados. El modelo indica la política que fundamenta el hallazgo o la limitación de cobertura.
- En modo `simple` el analista propone el hallazgo. En modo `doble` un revisor usa el mismo modelo para cotejar el borrador con el texto de la política y el inventario original. Si se rechaza la propuesta del revisor, Python puede conservar el borrador después de pasar el mismo validador. El orquestador ejecuta las llamadas directamente, sin MCP.
