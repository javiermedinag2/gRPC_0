from pymongo import MongoClient

Cliente = MongoClient('mongodb://root:root@localhost:27050') # Conecta al servidor MongoDB en localhost y puerto 27017
db = Cliente.Escuela # Selecciona la base de datos 'Escuela'
Libros = db.Libros # Selecciona la colección 'Libros'

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
