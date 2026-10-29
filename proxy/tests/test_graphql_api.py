import unittest
from unittest.mock import Mock

import grpc
from proxy.graphql_api import create_schema
from proxy.grpc_gateway import GrpcLibraryGateway, LibraryServiceError
from proxy.models import Book, OperationResult
import libros_pb2


class FakeLibraryGateway:
    def list_books(self):
        return [Book("7", "Dune", "Frank Herbert", 1965)]

    def get_book(self, book_id):
        return Book(book_id, "Dune", "Frank Herbert", 1965)

    def add_book(self, book):
        return OperationResult(book.id, "Libro agregado")

    def update_book(self, book):
        return OperationResult(book.id, "Libro actualizado")

    def delete_book(self, book_id):
        return OperationResult(book_id, "Libro eliminado")


class GraphQLApiTests(unittest.TestCase):
    def setUp(self):
        self.schema = create_schema()
        self.context = {"library": FakeLibraryGateway()}

    def execute(self, query, variables=None):
        return self.schema.execute_sync(
            query,
            variable_values=variables,
            context_value=self.context,
        )

    def test_lists_books(self):
        result = self.execute(
            "{ libros { id titulo autor anioPublicacion } }"
        )

        self.assertIsNone(result.errors)
        self.assertEqual(
            result.data["libros"],
            [
                {
                    "id": "7",
                    "titulo": "Dune",
                    "autor": "Frank Herbert",
                    "anioPublicacion": 1965,
                }
            ],
        )

    def test_gets_book_by_id(self):
        result = self.execute(
            'query($id: ID!) { libro(id: $id) { id titulo } }',
            {"id": "7"},
        )

        self.assertIsNone(result.errors)
        self.assertEqual(result.data["libro"], {"id": "7", "titulo": "Dune"})

    def test_add_update_and_delete_mutations(self):
        input_book = {
            "id": "8",
            "titulo": "Foundation",
            "autor": "Isaac Asimov",
            "anioPublicacion": 1951,
        }
        added = self.execute(
            "mutation($input: LibroInput!) { "
            "agregarLibro(input: $input) { id mensaje } }",
            {"input": input_book},
        )
        updated = self.execute(
            "mutation($input: LibroInput!) { "
            "actualizarLibro(input: $input) { id mensaje } }",
            {"input": input_book},
        )
        deleted = self.execute(
            "mutation($id: ID!) { eliminarLibro(id: $id) { id mensaje } }",
            {"id": "8"},
        )

        self.assertIsNone(added.errors)
        self.assertEqual(added.data["agregarLibro"]["id"], "8")
        self.assertIsNone(updated.errors)
        self.assertEqual(updated.data["actualizarLibro"]["mensaje"], "Libro actualizado")
        self.assertIsNone(deleted.errors)
        self.assertEqual(deleted.data["eliminarLibro"]["mensaje"], "Libro eliminado")

    def test_reports_gateway_errors_to_graphql_client(self):
        class FailingGateway(FakeLibraryGateway):
            def get_book(self, book_id):
                raise LibraryServiceError("NOT_FOUND: Libro no encontrado")

        self.context["library"] = FailingGateway()
        result = self.execute('query { libro(id: "404") { id } }')

        self.assertIsNotNone(result.errors)
        self.assertIn("NOT_FOUND: Libro no encontrado", result.errors[0].message)


class GrpcGatewayTests(unittest.TestCase):
    def setUp(self):
        self.stub = Mock()
        self.gateway = GrpcLibraryGateway(stub=self.stub)

    def test_lists_books_from_streaming_response(self):
        self.stub.ListarLibros.return_value = [
            libros_pb2.LibrosResponse(
                libros=libros_pb2.Libro(
                    id="7",
                    titulo="Dune",
                    autor="Frank Herbert",
                    anio_publicacion=1965,
                )
            )
        ]

        self.assertEqual(
            self.gateway.list_books(),
            [Book("7", "Dune", "Frank Herbert", 1965)],
        )

    def test_create_and_update_send_proto_book_fields(self):
        book = Book("8", " Foundation ", " Isaac Asimov ", 1951)
        self.stub.AgregarLibro.return_value = libros_pb2.AgregarLibroResponse(
            id="8", mensaje="Libro agregado"
        )
        self.stub.ActualizarLibro.return_value = libros_pb2.ActualizarLibroResponse(
            mensaje="Libro actualizado"
        )

        self.assertEqual(
            self.gateway.add_book(book),
            OperationResult("8", "Libro agregado"),
        )
        self.assertEqual(
            self.stub.AgregarLibro.call_args.args[0].libro,
            libros_pb2.Libro(
                id="8",
                titulo="Foundation",
                autor="Isaac Asimov",
                anio_publicacion=1951,
            ),
        )
        self.assertEqual(
            self.gateway.update_book(book),
            OperationResult("8", "Libro actualizado"),
        )

    def test_converts_grpc_errors_and_rejects_non_numeric_ids(self):
        class NotFoundError(grpc.RpcError):
            def code(self):
                return grpc.StatusCode.NOT_FOUND

            def details(self):
                return "Libro no encontrado"

        self.stub.ObtenerLibro.side_effect = NotFoundError()
        with self.assertRaisesRegex(LibraryServiceError, "NOT_FOUND"):
            self.gateway.get_book("404")
        with self.assertRaisesRegex(ValueError, "entero"):
            self.gateway.delete_book("abc")


if __name__ == "__main__":
    unittest.main()
