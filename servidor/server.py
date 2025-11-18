from concurrent import futures
import grpc
import libros_pb2
import libros_pb2_grpc
from base_de_datos import buscar_libro_por_id, agregar_libro, listar_libros, eliminar_libro, actualizar_libro   

Libro_a_db = {"id": 0, "title": "", "author": "", "publishedYear": 0}

class LibrosServiceServicer(libros_pb2_grpc.LibrosServiceServicer):
    def ObtenerLibro(self, request, context):
        print("Consulta de libro:")
        print(request)
        libro_response = libros_pb2.LibroResponse()
        libro_bd = buscar_libro_por_id(int(request.id))
        print(libro_bd)
        if libro_bd: # Aquí se usaría libro_bd para llenar la respuesta
            libro_response.libro.id = str(libro_bd["id"])
            libro_response.libro.titulo = libro_bd["title"]
            libro_response.libro.autor = libro_bd["author"]
            libro_response.libro.anio_publicacion = libro_bd["publishedYear"]
            context.set_code(grpc.StatusCode.OK)
            return libro_response
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Libro no encontrado ejemplo')
            return libro_response
    
    def AgregarLibro(self, request, context):
        print("Agregar libro:")
        print(request)
        if request.libro.id is None or request.libro.titulo == "" or request.libro.autor == "":
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Datos del libro no proporcionados')
            return libros_pb2.AgregarLibroResponse()
        else:
            Libro_a_db["id"] = int(request.libro.id)
            Libro_a_db["title"] = request.libro.titulo  
            Libro_a_db["author"] = request.libro.autor
            Libro_a_db["publishedYear"] = request.libro.anio_publicacion
            if agregar_libro(Libro_a_db):
                context.set_code(grpc.StatusCode.OK)
                agregar_response = libros_pb2.AgregarLibroResponse()
                agregar_response.id = request.libro.id
                agregar_response.mensaje = f"Libro '{request.libro.titulo}' agregado exitosamente."
                return agregar_response
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Error al agregar el libro')
                return libros_pb2.AgregarLibroResponse()
            
    def ListarLibros(self, request_iterator, context):
        print("Listar libros:")
        lista_libros = listar_libros()      
        #print(lista_libros)
        libro_response = libros_pb2.LibrosResponse()
        for un_libro in lista_libros:
            libro_response.libros.id = str(un_libro["id"])
            libro_response.libros.titulo = un_libro["title"]
            libro_response.libros.autor = un_libro["author"]
            libro_response.libros.anio_publicacion = un_libro["publishedYear"]
            context.set_code(grpc.StatusCode.OK)
            yield libro_response

    def EliminarLibro(self, request, context):
        print("Eliminar libro:")
        print(request)
        if not request.id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('ID del libro no proporcionado')
            return libros_pb2.EliminarLibroResponse()
        else:
            eliminar_count = eliminar_libro(int(request.id))
            if eliminar_count > 0:
                context.set_code(grpc.StatusCode.OK)
                print(f"Libro con ID {request.id} eliminado.")
                eliminar_response = libros_pb2.EliminarLibroResponse()
                eliminar_response.mensaje = f"Libro con ID {request.id} eliminado exitosamente."
                return eliminar_response
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Libro no encontrado para eliminar')
                return libros_pb2.EliminarLibroResponse()
 
    def ActualizarLibro(self, request, context):
        print("Actualizar libro:")
        print(request)
        if actualizar_libro(int(request.libro.id), {
            "id": int(request.libro.id),
            "title": request.libro.titulo,
            "author": request.libro.autor,
            "publishedYear": request.libro.anio_publicacion
        }):     
            context.set_code(grpc.StatusCode.OK)
            print(f"Libro con ID {request.libro.id} actualizado.")
            actualizar_response = libros_pb2.ActualizarLibroResponse()
            actualizar_response.mensaje = f"Libro con ID {request.libro.id} actualizado exitosamente."
            return actualizar_response
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Libro no encontrado para actualizar')
            return libros_pb2.ActualizarLibroResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    libros_pb2_grpc.add_LibrosServiceServicer_to_server(LibrosServiceServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()