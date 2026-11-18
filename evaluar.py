"""Evalúa los dos modos de auditoría de MFA y genera el informe Markdown."""

import argparse
import json
import math
from pathlib import Path
from statistics import mean

from auditoria import (DATOS, RAIZ, ErrorOllama, Ollama, agregar_modelo, auditar,
                       esquema_hallazgo, preparar_evidencia, presentar, resumen_inventario)

MODOS = ("simple", "doble")


def verificar_datos(casos):
    for caso in casos:
        evidencia = preparar_evidencia(caso["pregunta"], caso["ambito"])
        inventario = evidencia["inventario"]
        fuentes = {inventario["fuente"]["id"], *evidencia["politicas_admisibles"]}
        faltantes = set(caso["citas_requeridas"]) - fuentes
        if faltantes:
            raise ValueError(f"{caso['id']}: faltan fuentes aplicables: {', '.join(sorted(faltantes))}.")
        senuelo = caso.get("fragmento_senuelo")
        recuperadas = {fragmento["id"] for fragmento in evidencia["fragmentos"]}
        if senuelo and (senuelo not in recuperadas or senuelo in fuentes):
            raise ValueError(f"{caso['id']}: el señuelo debe aparecer como contexto sin autorización de cita.")
        estado, sin_mfa = resumen_inventario(inventario)
        if caso["esperado"] != {"estado": estado, "sin_mfa": sin_mfa}:
            raise ValueError(f"{caso['id']}: el inventario de prueba no coincide con el hallazgo esperado.")


def sumar_disponibles(valores):
    return sum(valores) if valores and all(valor is not None for valor in valores) else None


def puntuar(caso, resultado, potencia_w, tarifa_kwh):
    hallazgo = resultado.hallazgo
    esperado = caso["esperado"]
    citas = set(resultado.citas)
    requeridas = set(caso["citas_requeridas"])
    permitidas = requeridas | set(caso["citas_admitidas"])
    recuperadas = {f["id"] for f in resultado.evidencia["fragmentos"]}
    fuentes = {resultado.evidencia["inventario"]["fuente"]["id"], *recuperadas}
    politica = hallazgo.politica if hallazgo else None
    if politica is not None and politica not in recuperadas:
        politica = "Referencia fuera de contexto"
    aceptada = resultado.error is None
    return {
        "hallazgo": descripcion(hallazgo.estado, hallazgo.sin_mfa) if hallazgo else "Formato inválido",
        "citas": ", ".join(sorted(citas)) or "Sin citas",
        "politica": politica or "—",
        "exacta": hallazgo is not None and (hallazgo.estado, hallazgo.sin_mfa) == (esperado["estado"], esperado["sin_mfa"]),
        "citas_correctas": requeridas <= citas <= (permitidas & fuentes),
        "aceptada": aceptada,
        "ejemplo": presentar(resultado) if aceptada and "fragmento_senuelo" in caso else None,
        "latencia": resultado.latencia_s,
        "entrada": sumar_disponibles([llamada.tokens_entrada for llamada in resultado.llamadas]),
        "salida": sumar_disponibles([llamada.tokens_salida for llamada in resultado.llamadas]),
        "costo": potencia_w / 1000 * resultado.latencia_s / 3600 * tarifa_kwh,
        "error": resultado.error,
        "revision_descartada": resultado.revision_descartada,
    }


def descripcion(estado, sin_mfa):
    conteo = str(sin_mfa) if sin_mfa is not None else "sin total"
    return f"{estado.replace('_', ' ')}, {conteo}"


def numero(valor, decimales=3):
    return "n/d" if valor is None else f"{valor:.{decimales}f}"


def generar_informe(args, casos, resultados, fallos, nota):
    lineas = [
        "# Evaluación de la auditoría de MFA",
        "",
        nota,
        "",
        f"Modelo configurado: `{args.modelo}`. Los dos modos usan los mismos casos y fuentes.",
        "",
        "## Resultados esperados",
        "",
        "| Caso | Ámbito | Hallazgo y cuentas activas sin MFA | Citas requeridas | Citas opcionales | RAG y CSV comprobados |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for caso in casos:
        esperado = descripcion(**caso["esperado"])
        citas = ", ".join(caso["citas_requeridas"])
        opcionales = ", ".join(caso["citas_admitidas"]) or "—"
        comprobacion = "Sí, señuelo recuperado" if "fragmento_senuelo" in caso else "Sí"
        lineas.append(f"| {caso['id']} | {caso['ambito']} | {esperado} | {citas} | {opcionales} | {comprobacion} |")
    lineas += [
        "",
        "## Comparación de modos",
        "",
        "| Modo | Casos ejecutados | Exactitud | Citas correctas | Respuestas aceptadas | Latencia media medida (s) | Tokens de entrada reportados | Tokens de salida reportados | Costo eléctrico total estimado (COP) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    total = len(casos)
    for modo in MODOS:
        filas = [fila for (_, modo_fila), fila in resultados.items() if modo_fila == modo]
        n = len(filas)
        celdas = [modo, f"{n}/{total}"]
        if n:
            celdas += [
                f"{sum(fila['exacta'] for fila in filas)}/{n}",
                f"{sum(fila['citas_correctas'] for fila in filas)}/{n}",
                f"{sum(fila['aceptada'] for fila in filas)}/{n}",
                numero(mean(fila["latencia"] for fila in filas)),
                numero(sumar_disponibles([fila["entrada"] for fila in filas]), 0),
                numero(sumar_disponibles([fila["salida"] for fila in filas]), 0),
                numero(sum(fila["costo"] for fila in filas), 6),
            ]
        else:
            celdas += ["Pendiente"] * 7
        lineas.append("| " + " | ".join(celdas) + " |")
    pares = [(resultados[(c["id"], "simple")], resultados[(c["id"], "doble")])
             for c in casos if all((c["id"], modo) in resultados for modo in MODOS)]
    if pares:
        diferencia = mean(doble["latencia"] - simple["latencia"] for simple, doble in pares)
        lineas += ["", f"Diferencia media de latencia (doble − simple): **{diferencia:+.3f} s** en {len(pares)}/{total} pares."]
    if len(pares) == total:
        for clave, rotulo in (("exacta", "Exactitud"), ("citas_correctas", "Calidad de las citas"),
                              ("aceptada", "Aceptación de respuestas")):
            antes = sum(simple[clave] for simple, _ in pares)
            despues = sum(doble[clave] for _, doble in pares)
            conclusion = "mejoró" if despues > antes else "bajó" if despues < antes else "se mantuvo"
            lineas += ["", f"{rotulo} con revisor: {conclusion} ({antes}/{total} en simple y {despues}/{total} en doble)."]
    elif pares:
        lineas += ["", "La comparación de calidad queda pendiente hasta ejecutar los seis pares."]
    else:
        lineas += ["", "Queda pendiente determinar si la revisión mejora la calidad y cuánto cambia la latencia."]

    lineas += [
        "",
        "## Mediciones por caso",
        "",
        "| Caso | Modo | Hallazgo propuesto | Política seleccionada | Citas trazadas | Exacto | Citas correctas | Aceptada | Latencia medida (s) | Tokens entrada/salida | Costo estimado (COP) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for caso in casos:
        for modo in MODOS:
            clave = (caso["id"], modo)
            fila = resultados.get(clave)
            if fila:
                celdas = [fila["hallazgo"], fila["politica"], fila["citas"], "Sí" if fila["exacta"] else "No",
                          "Sí" if fila["citas_correctas"] else "No", "Sí" if fila["aceptada"] else "No",
                          numero(fila["latencia"]),
                          f"{numero(fila['entrada'], 0)}/{numero(fila['salida'], 0)}", numero(fila["costo"], 6)]
            else:
                celdas = ["Error de Ollama" if clave in fallos else "Pendiente", *(["—"] * 8)]
            lineas.append("| " + " | ".join([caso["id"], modo, *celdas]) + " |")
    casos_senuelo = [caso for caso in casos if "fragmento_senuelo" in caso]
    if casos_senuelo:
        lineas += ["", "## Caso con señuelo", ""]
        for caso in casos_senuelo:
            identificador = caso["id"]
            lineas.append(f"El fragmento `{caso['fragmento_senuelo']}` se incluyó en la evidencia de {identificador}.")
            lineas.append("")
            for modo in MODOS:
                fila = resultados.get((identificador, modo))
                if fila is None:
                    lineas.append(f"- **{modo}**. Resultado pendiente.")
                else:
                    superada = fila["exacta"] and fila["citas_correctas"] and fila["aceptada"]
                    veredicto = "Superó la prueba" if superada else "Falló la prueba"
                    lineas.append(f"- **{modo}**. {veredicto}. Hallazgo: {fila['hallazgo']}. Citas: {fila['citas']}.")
            ejemplo = next((fila["ejemplo"] for (id_caso, _), fila in resultados.items()
                            if id_caso == identificador and fila["ejemplo"]), None)
            if ejemplo:
                lineas += ["", "### Respuesta válida de esta corrida", "", "```text", ejemplo, "```"]
    mensajes = [f"- {caso}, {modo}. {mensaje}" for (caso, modo), mensaje in fallos.items()]
    mensajes += [f"- {caso}, {modo}. {fila['error']}" for (caso, modo), fila in resultados.items() if fila["error"]]
    mensajes += [f"- {caso}, {modo}. Se conservó el borrador validado. Motivo para descartar la revisión: {fila['revision_descartada']}"
                 for (caso, modo), fila in resultados.items() if fila["revision_descartada"]]
    if mensajes:
        lineas += ["", "### Incidencias", "", *mensajes]
    lineas += [
        "",
        "## Método y supuestos",
        "",
        "- Exactitud exige el estado y el conteo esperados en el hallazgo propuesto. Las citas trazadas se puntúan con los criterios originales: todas las referencias requeridas, y solo referencias requeridas u opcionales presentes en la evidencia. La aceptación indica que el validador común autorizó publicar la respuesta. C6 exige las tres condiciones.",
        "- El modo doble valida la propuesta del revisor. Si la rechaza, puede entregar el borrador del analista tras validarlo con las mismas reglas. Las incidencias indican cuándo se descartó una revisión.",
        "- Una llamada de calentamiento queda fuera de las mediciones. Cada caso se ejecuta una vez por modo, alternando el orden. La latencia de pared cubre RAG, lectura del CSV, llamadas al modelo y validación. Las medias usan los casos ejecutados y la diferencia usa casos emparejados.",
        "- Los tokens de entrada (`prompt_eval_count`) y de salida (`eval_count`) se suman por separado. En modo doble se suman las dos llamadas. `n/d` indica que falta el contador en alguna llamada del agregado.",
        f"- El costo se estima con una potencia media supuesta del equipo completo de {args.potencia_w:g} W, una tarifa de ejemplo de {args.tarifa_kwh:g} COP/kWh y la latencia medida. Fórmula `costo = (W / 1000) × (segundos / 3600) × tarifa`. No se midió potencia. Se excluyen la descarga del modelo y el calentamiento.",
    ]
    return "\n".join(lineas) + "\n"


def no_negativo(texto):
    valor = float(texto)
    if not math.isfinite(valor) or valor < 0:
        raise argparse.ArgumentTypeError("se requiere un número finito no negativo")
    return valor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    agregar_modelo(parser)
    parser.add_argument("--solo-datos", action="store_true", help="comprueba recuperación y conteos sin Ollama")
    parser.add_argument("--potencia-w", type=no_negativo, default=65)
    parser.add_argument("--tarifa-kwh", type=no_negativo, default=900, help="tarifa en COP/kWh")
    parser.add_argument("--salida", type=Path, default=RAIZ / "docs" / "resultados.md")
    args = parser.parse_args()
    casos = json.loads((DATOS / "casos.json").read_text(encoding="utf-8"))
    try:
        verificar_datos(casos)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error en los datos de prueba: {error}\n")
    print(f"Datos comprobados en {len(casos)} casos.", flush=True)
    resultados, fallos = {}, {}
    nota = "Se comprobó la recuperación y el conteo de los seis casos."
    if args.solo_datos:
        nota += " Esta ejecución omitió el modelo local."
    else:
        cliente = Ollama(args.modelo)
        try:
            cliente.consultar("Devuelve este hallazgo con el esquema solicitado.",
                              {"estado": "evidencia_insuficiente", "sin_mfa": None, "politica": None},
                              esquema_hallazgo({}))
        except ErrorOllama as error:
            nota += " Ollama no respondió correctamente durante el calentamiento. Las métricas del modelo quedan pendientes."
            print(error, flush=True)
        else:
            for indice, caso in enumerate(casos):
                for modo in (MODOS if indice % 2 == 0 else reversed(MODOS)):
                    clave = (caso["id"], modo)
                    print(f"Ejecutando {caso['id']} en modo {modo}…", flush=True)
                    try:
                        resultado = auditar(cliente, caso["pregunta"], caso["ambito"], modo)
                    except ErrorOllama as error:
                        fallos[clave] = str(error)
                    else:
                        resultados[clave] = puntuar(caso, resultado, args.potencia_w, args.tarifa_kwh)
            nota += f" Ollama local completó {len(resultados)} de {len(casos) * len(MODOS)} auditorías."
    args.salida.write_text(generar_informe(args, casos, resultados, fallos, nota), encoding="utf-8")
    print(f"Informe: {args.salida}")
    return int(not args.solo_datos and len(resultados) != len(casos) * len(MODOS))


if __name__ == "__main__":
    raise SystemExit(main())
