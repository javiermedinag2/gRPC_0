import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from proxy.graphql_api import GraphQLContext, create_schema
from proxy.grpc_gateway import GrpcLibraryGateway

library = GrpcLibraryGateway()


async def get_context() -> GraphQLContext:
    return {"library": library}


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    library.close()


app = FastAPI(title="API GraphQL de libros", lifespan=lifespan)
app.include_router(
    GraphQLRouter(create_schema(), context_getter=get_context),
    prefix="/graphql",
)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "proxy.main:app",
        host=os.getenv("GRAPHQL_HOST", "0.0.0.0"),
        port=int(os.getenv("GRAPHQL_PORT", "8000")),
    )
