import os
import sys
from pathlib import Path

import grpc
from google.protobuf.empty_pb2 import Empty

SERVER_DIRECTORY = Path(__file__).resolve().parents[1] / "servidor"
if str(SERVER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SERVER_DIRECTORY))

import libros_pb2
import libros_pb2_grpc

from proxy.models import Book, OperationResult


class LibraryServiceError(Exception):
    pass


class GrpcLibraryGateway:
    def __init__(self, address=None, stub=None):
        self._channel = None
        if stub is None:
            target = address or os.getenv("GRPC_SERVER_ADDRESS", "127.0.0.1:50051")
            self._channel = grpc.insecure_channel(target)
            self._stub = libros_pb2_grpc.LibrosServiceStub(self._channel)
        else:
            self._stub = stub

    def close(self):
        if self._channel is not None:
            self._channel.close()

    def list_books(self):
        try:
            responses = self._stub.ListarLibros(Empty(), timeout=5)
            return [self._from_proto(response.libros) for response in responses]
        except grpc.RpcError as error:
            raise self._service_error(error) from error

    def get_book(self, book_id):
        request = libros_pb2.LibroRequest(id=self._validated_id(book_id))
        try:
            response = self._stub.ObtenerLibro(request, timeout=5)
            return self._from_proto(response.libro)
        except grpc.RpcError as error:
            raise self._service_error(error) from error

    def add_book(self, book):
        request = libros_pb2.AgregarLibroRequest(libro=self._to_proto(book))
        try:
            response = self._stub.AgregarLibro(request, timeout=5)
            return OperationResult(id=response.id, mensaje=response.mensaje)
        except grpc.RpcError as error:
            raise self._service_error(error) from error

    def update_book(self, book):
        request = libros_pb2.ActualizarLibroRequest(libro=self._to_proto(book))
        try:
            response = self._stub.ActualizarLibro(request, timeout=5)
            return OperationResult(id=book.id, mensaje=response.mensaje)
        except grpc.RpcError as error:
            raise self._service_error(error) from error

    def delete_book(self, book_id):
        validated_id = self._validated_id(book_id)
        request = libros_pb2.LibroRequest(id=validated_id)
        try:
            response = self._stub.EliminarLibro(request, timeout=5)
            return OperationResult(id=validated_id, mensaje=response.mensaje)
        except grpc.RpcError as error:
            raise self._service_error(error) from error

    @staticmethod
    def _validated_id(book_id):
        try:
            value = int(book_id)
        except (TypeError, ValueError) as error:
            raise ValueError("El ID del libro debe ser un entero.") from error
        if value < 0:
            raise ValueError("El ID del libro no puede ser negativo.")
        return str(value)

    @classmethod
    def _to_proto(cls, book):
        return libros_pb2.Libro(
            id=cls._validated_id(book.id),
            titulo=book.titulo.strip(),
            autor=book.autor.strip(),
            anio_publicacion=book.anio_publicacion,
        )

    @staticmethod
    def _from_proto(book):
        return Book(
            id=book.id,
            titulo=book.titulo,
            autor=book.autor,
            anio_publicacion=book.anio_publicacion,
        )

    @staticmethod
    def _service_error(error):
        code = error.code()
        details = error.details() or "El servidor gRPC no pudo completar la operación."
        return LibraryServiceError(f"{code.name}: {details}")
