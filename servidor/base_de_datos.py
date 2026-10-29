import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

mongo_username = os.getenv("MONGO_USERNAME", "")
mongo_password = os.getenv("MONGO_PASSWORD", "")
if bool(mongo_username) != bool(mongo_password):
    raise ValueError("Configura MONGO_USERNAME y MONGO_PASSWORD juntos en .env.")

mongo_options = {}
if mongo_username:
    mongo_options = {
        "username": mongo_username,
        "password": mongo_password,
        "authSource": os.getenv("MONGO_AUTH_SOURCE", "admin"),
    }

Cliente = MongoClient(
    host=os.getenv("MONGO_HOST", "localhost"),
    port=int(os.getenv("MONGO_PORT", "27017")),
    **mongo_options,
)
db = Cliente[os.getenv("MONGO_DATABASE", "Escuela")]
Libros = db.Libros


def buscar_libro_por_id(libro_id):
    return Libros.find_one({"id": libro_id})
def agregar_libro(libro):
    print(f"Agregando libro: {libro}")
    return Libros.insert_one(libro).inserted_id
def listar_libros():
    return list(Libros.find())
def eliminar_libro(libro_id):
    return Libros.delete_one({"id": libro_id}).deleted_count
def actualizar_libro(libro_id, nuevo_libro):
    return Libros.update_one({"id": libro_id}, {"$set": nuevo_libro}).modified_count    
