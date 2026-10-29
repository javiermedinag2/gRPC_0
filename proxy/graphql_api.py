import strawberry
from graphql import GraphQLError
from strawberry.types import Info
from typing import NoReturn, TypedDict

from proxy.grpc_gateway import GrpcLibraryGateway, LibraryServiceError
from proxy.models import Book, OperationResult


@strawberry.type
class Libro:
    id: strawberry.ID
    titulo: str
    autor: str
    anio_publicacion: int


@strawberry.input
class LibroInput:
    id: strawberry.ID
    titulo: str
    autor: str
    anio_publicacion: int


@strawberry.type
class ResultadoOperacion:
    id: strawberry.ID
    mensaje: str


class GraphQLContext(TypedDict):
    library: GrpcLibraryGateway


def _graphql_book(book: Book) -> Libro:
    return Libro(
        id=strawberry.ID(book.id),
        titulo=book.titulo,
        autor=book.autor,
        anio_publicacion=book.anio_publicacion,
    )


def _graphql_result(result: OperationResult) -> ResultadoOperacion:
    return ResultadoOperacion(
        id=strawberry.ID(result.id),
        mensaje=result.mensaje,
    )


def _raise_graphql_error(error: Exception) -> NoReturn:
    raise GraphQLError(str(error)) from error


@strawberry.type
class Query:
    @strawberry.field
    def libros(self, info: Info[GraphQLContext, None]) -> list[Libro]:
        try:
            return [_graphql_book(book) for book in info.context["library"].list_books()]
        except (LibraryServiceError, ValueError) as error:
            _raise_graphql_error(error)

    @strawberry.field
    def libro(self, info: Info[GraphQLContext, None], id: strawberry.ID) -> Libro:
        try:
            return _graphql_book(info.context["library"].get_book(str(id)))
        except (LibraryServiceError, ValueError) as error:
            _raise_graphql_error(error)


@strawberry.type
class Mutation:
    @strawberry.mutation(name="agregarLibro")
    def agregar_libro(
        self, info: Info[GraphQLContext, None], input: LibroInput
    ) -> ResultadoOperacion:
        try:
            book = Book(
                id=str(input.id),
                titulo=input.titulo,
                autor=input.autor,
                anio_publicacion=input.anio_publicacion,
            )
            return _graphql_result(info.context["library"].add_book(book))
        except (LibraryServiceError, ValueError) as error:
            _raise_graphql_error(error)

    @strawberry.mutation(name="actualizarLibro")
    def actualizar_libro(
        self, info: Info[GraphQLContext, None], input: LibroInput
    ) -> ResultadoOperacion:
        try:
            book = Book(
                id=str(input.id),
                titulo=input.titulo,
                autor=input.autor,
                anio_publicacion=input.anio_publicacion,
            )
            return _graphql_result(info.context["library"].update_book(book))
        except (LibraryServiceError, ValueError) as error:
            _raise_graphql_error(error)

    @strawberry.mutation(name="eliminarLibro")
    def eliminar_libro(
        self, info: Info[GraphQLContext, None], id: strawberry.ID
    ) -> ResultadoOperacion:
        try:
            return _graphql_result(info.context["library"].delete_book(str(id)))
        except (LibraryServiceError, ValueError) as error:
            _raise_graphql_error(error)


def create_schema():
    return strawberry.Schema(query=Query, mutation=Mutation)
