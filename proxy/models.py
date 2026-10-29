from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    id: str
    titulo: str
    autor: str
    anio_publicacion: int


@dataclass(frozen=True)
class OperationResult:
    id: str
    mensaje: str
