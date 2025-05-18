#!/usr/bin/env python3
from pymongo import MongoClient
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=2)

# Conexión a MongoDB local
client = MongoClient('mongodb://localhost:27017/')
db = client.miProyecto
coleccion = db.misiones

def insertar():
    nombre = input("Nombre de la misión: ")
    es_trip = input("¿Es tripulada? (s/n): ").lower() == 's'
    presupuesto = float(input("Presupuesto USD: "))
    objetivos = [o.strip() for o in input("Objetivos (separados por coma): ").split(",") if o.strip()]
    tipo = input("Carga útil - tipo: ")
    modelo = input("Carga útil - modelo: ")
    serie = int(input("Carga útil - nº de serie: "))
    fecha = datetime.datetime.now()

    documento = {
        "nombre": nombre,
        "esTripulada": es_trip,
        "presupuestoUSD": presupuesto,
        "objetivos": objetivos,
        "fechaLanzamiento": fecha,
        "cargaUtil": {
            "tipo": tipo,
            "modelo": modelo,
            "numeroSerie": serie
        }
    }
    resultado = coleccion.insert_one(documento)
    print("Documento insertado con id:", resultado.inserted_id)

def eliminar():
    modo = input("Eliminar uno o muchos? (1/∞): ")
    campo = input("Campo para filtrar (p.ej. nombre): ")
    valor = input("Valor a buscar: ")

    # Intentar convertir valor a tipo adecuado para búsquedas sencillas
    try:
        valor = int(valor)
    except:
        pass

    filtro = {campo: valor}

    if modo == '1':
        resultado = coleccion.delete_one(filtro)
        if resultado.deleted_count > 0:
            print("Documento eliminado.")
        else:
            print("No se encontró ningún documento que coincida.")
    else:
        resultado = coleccion.delete_many(filtro)
        print(f"Documentos eliminados: {resultado.deleted_count}")

def modificar():
    nombre = input("Nombre de la misión a modificar: ")
    filtro = {"nombre": nombre}
    doc = coleccion.find_one(filtro)
    if not doc:
        print("Misión no encontrada.")
        return

    campo = input("Campo a modificar (nombre, presupuestoUSD): ")
    nuevo = input("Nuevo valor: ")

    # Convertir tipo si es necesario
    if campo == "presupuestoUSD":
        try:
            nuevo = float(nuevo)
        except ValueError:
            print("Valor inválido para presupuesto.")
            return

    resultado = coleccion.update_one(filtro, {"$set": {campo: nuevo}})
    if resultado.modified_count > 0:
        print("Documento modificado.")
    else:
        print("No se modificó ningún documento.")

def consulta_simple():
    print("Misiones tripuladas (limit 5, orden desc):")
    cursor = coleccion.find({"esTripulada": True}).sort("fechaLanzamiento", -1).limit(5)
    for doc in cursor:
        pp.pprint(doc)

def consulta_array():
    print("Misiones con 'Europa' en objetivos:")
    cursor = coleccion.find({"objetivos": "Europa"})
    for doc in cursor:
        pp.pprint(doc)

def consulta_embebido():
    print("Misiones con cargaUtil.tipo == 'Rover':")
    cursor = coleccion.find({"cargaUtil.tipo": "Rover"})
    for doc in cursor:
        pp.pprint(doc)

def consulta_agrupacion():
    print("Total de presupuesto agrupado por esTripulada:")
    pipeline = [
        {"$group": {"_id": "$esTripulada", "totalUSD": {"$sum": "$presupuestoUSD"}}},
        {"$sort": {"totalUSD": -1}}
    ]
    resultado = coleccion.aggregate(pipeline)
    for doc in resultado:
        pp.pprint(doc)

def menu():
    print("""
1. Insertar documento
2. Eliminar documento(s)
3. Modificar documento(s)
4. Consulta simple
5. Consulta con array
6. Consulta con subdocumento embebido
7. Consulta de agregación
8. Salir
""")
    return input("Elige opción: ")

if __name__ == "__main__":
    while True:
        op = menu().strip()
        if op == '1':
            insertar()
        elif op == '2':
            eliminar()
        elif op == '3':
            modificar()
        elif op == '4':
            consulta_simple()
        elif op == '5':
            consulta_array()
        elif op == '6':
            consulta_embebido()
        elif op == '7':
            consulta_agrupacion()
        elif op == '8':
            break
        else:
            print("Opción inválida.")
