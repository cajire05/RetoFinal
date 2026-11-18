# Evaluación de la auditoría de MFA

Se comprobó la recuperación y el conteo de los seis casos. Ollama local completó 12 de 12 auditorías.

La evaluación final del 18 de noviembre de 2026 usó Ollama `0.40.16` y `qwen2.5:3b` en CPU (Q4_K_M, digest `357c53fb659c`). Se verificaron 19 respuestas HTTP 200, incluida la del calentamiento. Ambos modos usaron el mismo modelo, los mismos casos y las mismas fuentes.

## Resultados esperados

| Caso | Ámbito | Hallazgo y cuentas activas sin MFA | Citas requeridas | Citas opcionales | RAG y CSV comprobados |
| --- | --- | --- | --- | --- | --- |
| C1 | todas | incumple, 4 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C2 | finanzas | incumple, 1 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C3 | ti | cumple, 0 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C4 | soporte | incumple, 2 | CSV-MFA, POL-MFA-01 | — | Sí |
| C5 | recursos humanos | evidencia insuficiente, sin total | CSV-MFA, POL-MFA-03 | POL-MFA-01 | Sí |
| C6 | contratistas | incumple, 1 | CSV-MFA, POL-MFA-04 | POL-MFA-01 | Sí, señuelo recuperado |

## Comparación antes y después

El «antes» corresponde a la [primera corrida real](resultados-antes.md). Cada fila resume los seis casos de un modo.

| Versión | Modo | Hallazgos exactos | Citas correctas | Respuestas aceptadas | C6 con señuelo | Latencia media medida (s) | Tokens de entrada / salida reportados | Costo eléctrico total estimado (COP) |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| Antes | simple | 6/6 | 0/6 | 0/6 | Falló | 8.999 | 3902 / 284 | 0.877381 |
| Antes | doble | 6/6 | 0/6 | 0/6 | Falló | 19.446 | 8239 / 535 | 1.896028 |
| Después | simple | 6/6 | 6/6 | 6/6 | Superó | 7.922 | 4003 / 205 | 0.772363 |
| Después | doble | 6/6 | 6/6 | 6/6 | Superó | 19.366 | 8529 / 412 | 1.888181 |

En la evaluación final ambos modos empataron en exactitud, citas y aceptación. El modo doble añadió **11.444 s por caso en promedio**, calculados sobre los seis pares. La diferencia de la primera corrida fue de 10.448 s.

## Mediciones por caso

| Caso | Modo | Hallazgo propuesto | Política seleccionada | Citas trazadas | Exacto | Citas correctas | Aceptada | Latencia medida (s) | Tokens entrada/salida | Costo estimado (COP) |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| C1 | simple | incumple, 4 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 9.727 | 664/34 | 0.158057 |
| C1 | doble | incumple, 4 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 13.723 | 1415/68 | 0.222996 |
| C2 | simple | incumple, 1 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 4.213 | 672/34 | 0.068461 |
| C2 | doble | incumple, 1 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 20.941 | 1431/68 | 0.340297 |
| C3 | simple | cumple, 0 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 17.134 | 668/33 | 0.278422 |
| C3 | doble | cumple, 0 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 19.768 | 1422/66 | 0.321224 |
| C4 | simple | incumple, 2 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 6.007 | 667/34 | 0.097610 |
| C4 | doble | incumple, 2 | POL-MFA-01 | CSV-MFA, POL-MFA-01 | Sí | Sí | Sí | 25.681 | 1421/70 | 0.417311 |
| C5 | simple | evidencia insuficiente, sin total | POL-MFA-03 | CSV-MFA, POL-MFA-03 | Sí | Sí | Sí | 5.730 | 672/36 | 0.093110 |
| C5 | doble | evidencia insuficiente, sin total | POL-MFA-03 | CSV-MFA, POL-MFA-03 | Sí | Sí | Sí | 18.700 | 1433/72 | 0.303883 |
| C6 | simple | incumple, 1 | POL-MFA-04 | CSV-MFA, POL-MFA-04 | Sí | Sí | Sí | 4.720 | 660/34 | 0.076702 |
| C6 | doble | incumple, 1 | POL-MFA-04 | CSV-MFA, POL-MFA-04 | Sí | Sí | Sí | 17.383 | 1407/68 | 0.282469 |

## Caso con señuelo

El fragmento `SENUELO-01` se incluyó en la evidencia de C6. En la primera corrida ambos modos lo citaron. En la evaluación final el registro externo dejó el señuelo fuera de las referencias admisibles.

- **simple**. Superó la prueba. Hallazgo: incumple, 1. Citas: CSV-MFA, POL-MFA-04.
- **doble**. Superó la prueba. Hallazgo: incumple, 1. Citas: CSV-MFA, POL-MFA-04.

### Respuesta válida de esta corrida

```text
Ámbito auditado: contratistas.
El ámbito incumple la política de MFA. [POL-MFA-04]
Cuentas activas sin MFA: 1. [CSV-MFA]
Política [POL-MFA-04] datos/politicas.md, MFA para contratistas.
Inventario [CSV-MFA] datos/cuentas.csv, cuentas activas del ámbito.
```

### Incidencias

- C4, doble. Se conservó el borrador validado. Motivo para descartar la revisión: El estado o el conteo propuesto contradice la evidencia del inventario.

## Método y supuestos

- Exactitud exige el estado y el conteo esperados en el hallazgo propuesto. Las citas trazadas se puntúan con los criterios originales: todas las referencias requeridas, y solo referencias requeridas u opcionales presentes en la evidencia. La aceptación indica que el validador común autorizó publicar la respuesta. C6 exige las tres condiciones.
- El modo doble valida la propuesta del revisor. Si la rechaza, puede entregar el borrador del analista tras validarlo con las mismas reglas. Las incidencias indican cuándo se descartó una revisión.
- Los seis casos sirvieron para diagnosticar y ajustar el flujo antes de la evaluación final. Los resultados describen esos casos y una corrida por versión en este equipo.
- Una llamada de calentamiento queda fuera de las mediciones. Cada caso se ejecuta una vez por modo, alternando el orden. La latencia de pared cubre RAG, lectura del CSV, llamadas al modelo y validación. Las medias usan los casos ejecutados y la diferencia usa casos emparejados.
- Los tokens de entrada (`prompt_eval_count`) y de salida (`eval_count`) se suman por separado. En modo doble se suman las dos llamadas. `n/d` indica que falta el contador en alguna llamada del agregado.
- El costo se estima con una potencia media supuesta del equipo completo de 65 W, una tarifa de ejemplo de 900 COP/kWh y la latencia medida. Fórmula `costo = (W / 1000) × (segundos / 3600) × tarifa`. No se midió potencia. Se excluyen la descarga del modelo y el calentamiento.
