from concurrent import futures
import time

import grpc
import libros_pb2
import libros_pb2_grpc

#temporal para probar las conexiones
libro_ejemplo = {
    "id": "1",
    "titulo": "Cien Años de Soledad",
    "autor": "Gabriel García Márquez",
    "anio_publicacion": 1967
}

class LibrosServiceServicer(libros_pb2_grpc.LibrosServiceServicer):
    def ObtenerLibro(self, request, context):
        print("Consulta de libro:")
        print(request)
        libro_response = libros_pb2.LibroResponse()

        libro_response.libro.id = libro_ejemplo["id"]
        libro_response.libro.titulo = libro_ejemplo["titulo"]
        libro_response.libro.autor = libro_ejemplo["autor"]
        libro_response.libro.anio_publicacion = libro_ejemplo["anio_publicacion"]
                
        return libro_response
    
    def AgregarLibro(self, request, context):
        print("Agregar libro:")
        print(request)

        agregar_response = libros_pb2.AgregarLibroResponse()
        #agregar_response.success = True
        #agregar_response.status_code = 201
        agregar_response.id = request.libro.id
        agregar_response.mensaje = f"Libro '{request.libro.titulo}' agregado exitosamente."
        return agregar_response

    def ListarLibros(self, request_iterator, context):
        print("Listar libros:")
        lista_libros = [
            {"id": "1", "titulo": "Cien Años de Soledad", "autor": "Gabriel García Márquez", "anio_publicacion": 1967},
            {"id": "2", "titulo": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "anio_publicacion": 1605},
            {"id": "3", "titulo": "La Sombra del Viento", "autor": "Carlos Ruiz Zafón", "anio_publicacion": 2001},
        ]
        libro_response = libros_pb2.LibrosResponse()
        for un_libro in lista_libros:
            libro_response.libros.id = un_libro["id"]
            libro_response.libros.titulo = un_libro["titulo"]
            libro_response.libros.autor = un_libro["autor"]
            libro_response.libros.anio_publicacion = un_libro["anio_publicacion"]
            #libro_response.status_code = 200
            yield libro_response

    def EliminarLibro(self, request, context):
        print("Eliminar libro:")
        print(request)

        eliminar_response = libros_pb2.EliminarLibroResponse()
        #eliminar_response.success = True
        #eliminar_response.status_code = 410
        eliminar_response.mensaje = f"Libro con ID {request.id} eliminado exitosamente."
        return eliminar_response
    
    def ActualizarLibro(self, request, context):
        print("Actualizar libro:")
        print(request)

        actualizar_response = libros_pb2.ActualizarLibroResponse()
        #actualizar_response.success = True
        #actualizar_response.status_code = 200
        actualizar_response.mensaje = f"Libro con ID {request.libro.id} actualizado exitosamente."
        return actualizar_response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    libros_pb2_grpc.add_LibrosServiceServicer_to_server(LibrosServiceServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()