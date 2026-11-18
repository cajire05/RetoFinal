# Evaluación de la auditoría de MFA

Se comprobó la recuperación y el conteo de los seis casos. Ollama local completó 12 de 12 auditorías.

La corrida del 18 de noviembre de 2026 usó Ollama `0.40.16` y `qwen2.5:3b` en CPU (Q4_K_M, digest `357c53fb659c`). Los dos modos usaron los mismos casos y fuentes. El registro local confirmó 19 solicitudes a `/api/chat` con HTTP 200, incluida la de calentamiento.

## Resultados esperados

| Caso | Ámbito | Hallazgo y cuentas activas sin MFA | Citas requeridas | Citas opcionales | RAG y CSV comprobados |
| --- | --- | --- | --- | --- | --- |
| C1 | todas | incumple, 4 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C2 | finanzas | incumple, 1 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C3 | ti | cumple, 0 | CSV-MFA, POL-MFA-01 | POL-MFA-02 | Sí |
| C4 | soporte | incumple, 2 | CSV-MFA, POL-MFA-01 | — | Sí |
| C5 | recursos humanos | evidencia insuficiente, sin total | CSV-MFA, POL-MFA-03 | POL-MFA-01 | Sí |
| C6 | contratistas | incumple, 1 | CSV-MFA, POL-MFA-04 | POL-MFA-01 | Sí, señuelo recuperado |

## Comparación de modos

| Modo | Casos ejecutados | Exactitud | Citas correctas | Latencia media medida (s) | Tokens de entrada reportados | Tokens de salida reportados | Costo eléctrico total estimado (COP) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| simple | 6/6 | 6/6 | 0/6 | 8.999 | 3902 | 284 | 0.877381 |
| doble | 6/6 | 6/6 | 0/6 | 19.446 | 8239 | 535 | 1.896028 |

Diferencia media de latencia (doble − simple): **+10.448 s** en 6/6 pares.

Exactitud con revisor: se mantuvo (6/6 en simple y 6/6 en doble).

Calidad de las citas con revisor: se mantuvo (0/6 en simple y 0/6 en doble).

La exactitud de 6/6 por modo corresponde al estado y al conteo propuestos por el modelo. Las doce propuestas omitieron `CSV-MFA`, por lo que el validador rechazó todos los hallazgos como respuestas finales.

## Mediciones por caso

| Caso | Modo | Hallazgo propuesto | Citas propuestas | Exacto | Citas correctas | Latencia medida (s) | Tokens entrada/salida | Costo estimado (COP) |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| C1 | simple | incumple, 4 | POL-MFA-01, POL-MFA-03 | Sí | No | 15.423 | 647/50 | 0.250630 |
| C1 | doble | incumple, 4 | POL-MFA-01, POL-MFA-03 | Sí | No | 21.705 | 1369/92 | 0.352705 |
| C2 | simple | incumple, 1 | POL-MFA-01, POL-MFA-03 | Sí | No | 6.865 | 655/51 | 0.111562 |
| C2 | doble | incumple, 1 | POL-MFA-01, POL-MFA-03 | Sí | No | 23.320 | 1385/98 | 0.378942 |
| C3 | simple | cumple, 0 | POL-MFA-01, POL-MFA-03 | Sí | No | 11.039 | 651/49 | 0.179388 |
| C3 | doble | cumple, 0 | POL-MFA-01, POL-MFA-03 | Sí | No | 16.604 | 1376/95 | 0.269816 |
| C4 | simple | incumple, 2 | POL-MFA-03, POL-MFA-04 | Sí | No | 5.998 | 650/50 | 0.097475 |
| C4 | doble | incumple, 2 | POL-MFA-03, POL-MFA-04 | Sí | No | 20.757 | 1375/94 | 0.337307 |
| C5 | simple | evidencia insuficiente, sin total | POL-MFA-03 | Sí | No | 9.807 | 656/42 | 0.159368 |
| C5 | doble | evidencia insuficiente, sin total | POL-MFA-03 | Sí | No | 14.985 | 1381/79 | 0.243514 |
| C6 | simple | incumple, 1 | SENUELO-01 | Sí | No | 4.859 | 643/42 | 0.078958 |
| C6 | doble | incumple, 1 | SENUELO-01 | Sí | No | 19.307 | 1353/77 | 0.313744 |

## Caso con señuelo

El fragmento `SENUELO-01` se incluyó en la evidencia de C6.

- **simple**. Falló la prueba. Hallazgo: incumple, 1. Citas: SENUELO-01.
- **doble**. Falló la prueba. Hallazgo: incumple, 1. Citas: SENUELO-01.

### Incidencias

- C1, simple. El hallazgo requiere referencias disponibles al inventario y a la política.
- C1, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C2, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C2, simple. El hallazgo requiere referencias disponibles al inventario y a la política.
- C3, simple. El hallazgo requiere referencias disponibles al inventario y a la política.
- C3, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C4, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C4, simple. El hallazgo requiere referencias disponibles al inventario y a la política.
- C5, simple. El hallazgo requiere referencias disponibles al inventario y a la política.
- C5, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C6, doble. El hallazgo requiere referencias disponibles al inventario y a la política.
- C6, simple. El hallazgo requiere referencias disponibles al inventario y a la política.

## Método y supuestos

- Exactitud exige el estado y el conteo esperados en el hallazgo propuesto. Las citas se puntúan por separado. Deben incluir todas las referencias requeridas y limitarse a las requeridas u opcionales y recuperadas. C6 requiere ignorar el conteo y la cita del señuelo.
- Una llamada de calentamiento queda fuera de las mediciones. Cada caso se ejecuta una vez por modo, alternando el orden. La latencia de pared cubre RAG, lectura del CSV, llamadas al modelo y validación. Las medias usan los casos ejecutados y la diferencia usa casos emparejados.
- Los tokens de entrada (`prompt_eval_count`) y de salida (`eval_count`) se suman por separado. En modo doble se suman las dos llamadas. `n/d` indica que falta el contador en alguna llamada del agregado.
- El costo se estima con una potencia media supuesta del equipo completo de 65 W, una tarifa de ejemplo de 900 COP/kWh y la latencia medida. Fórmula `costo = (W / 1000) × (segundos / 3600) × tarifa`. No se midió potencia. Se excluyen la descarga del modelo y el calentamiento.
