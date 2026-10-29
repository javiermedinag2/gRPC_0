# Biblioteca gRPC, GraphQL y Android

Proyecto de gestión de libros con tres componentes:

- `servidor/`: servicio gRPC en Python y acceso a MongoDB.
- `proxy/`: API GraphQL Strawberry que traduce consultas y mutaciones a llamadas gRPC.
- `cliente/`: aplicación Android Kotlin con Jetpack Compose para consultar, agregar, editar y eliminar libros.

## Requisitos

- Python 3.10 o posterior.
- MongoDB disponible en la dirección configurada en `servidor/base_de_datos.py`.
- Android Studio con Android SDK 35 y JDK 17.

## Variables de entorno y credenciales

La configuración local se carga desde `.env` en la raíz del proyecto. El archivo está excluido de Git; `.env.example` sirve como plantilla compartible. Si necesitas recrearlo:

```powershell
Copy-Item .env.example .env
```

Configura `MONGO_USERNAME` y `MONGO_PASSWORD` con las credenciales de MongoDB. Déjalas vacías si la instancia local no requiere autenticación. Si las configuras, ambas deben estar presentes; `MONGO_AUTH_SOURCE` debe coincidir con la base de autenticación del usuario. `MONGO_HOST`, `MONGO_PORT` y `MONGO_DATABASE` seleccionan la conexión y la base de datos.

`GRPC_BIND_ADDRESS` configura dónde escucha el servidor gRPC; `GRPC_SERVER_ADDRESS` configura el destino del proxy. `GRAPHQL_HOST` y `GRAPHQL_PORT` configuran el servidor GraphQL. No guardes contraseñas reales en `.env.example` ni las compartas o confirmes en Git.

El proyecto todavía no implementa cuentas ni autenticación de usuarios de la aplicación; estas credenciales son únicamente para la conexión a MongoDB.

## Ejecutar el backend

Instala las dependencias del proxy desde la raíz del proyecto:

```powershell
python -m pip install -r proxy\requirements.txt
```

Inicia MongoDB y luego el servicio gRPC en una terminal:

```powershell
python servidor\server.py
```

El servidor gRPC escucha en `localhost:50051`. En otra terminal, desde la raíz, inicia el proxy:

```powershell
python -m uvicorn proxy.main:app --host 0.0.0.0 --port 8000
```

La API GraphQL queda disponible en `http://localhost:8000/graphql` y el indicador de salud en `http://localhost:8000/health`. Para cambiar la dirección del servicio gRPC, configura `GRPC_SERVER_ADDRESS` antes de iniciar el proxy.

Para ejecutar las pruebas del proxy:

```powershell
python -m unittest discover -s proxy\tests -v
```

El contrato de las operaciones gRPC se define en [`servidor/libros.proto`](servidor/libros.proto). El API expone la consulta `libros`, la consulta `libro(id: ID!)` y las mutaciones `agregarLibro(input: LibroInput!)`, `actualizarLibro(input: LibroInput!)` y `eliminarLibro(id: ID!)`. El input usa `id`, `titulo`, `autor` y `anioPublicacion`.

## Ejecutar la aplicación Android

Abre la carpeta `cliente/` en Android Studio, permite que Gradle sincronice el proyecto y ejecútalo en un emulador Android. La URL GraphQL predeterminada es `http://10.0.2.2:8000/graphql`, la dirección con la que el emulador Android accede al host de desarrollo.

Para compilar desde la terminal usando el wrapper incluido:

```powershell
cd cliente
.\gradlew.bat assembleDebug
```

La URL puede cambiarse al compilar pasando una propiedad Gradle:

```powershell
.\gradlew.bat assembleDebug -PGRAPHQL_URL=http://10.0.2.2:8000/graphql
```

Para un dispositivo físico, configura `GRAPHQL_URL` con la dirección IP del equipo que ejecuta el proxy y permite el acceso al puerto 8000 en la red local. El proxy debe poder alcanzar el servidor gRPC según `GRPC_SERVER_ADDRESS`.

El API local no implementa autenticación y usa HTTP sin cifrado para facilitar las pruebas desde el emulador; no lo expongas a redes públicas sin añadir las protecciones necesarias.

## Ejecutar backend con Docker Compose

Con Docker Desktop iniciado y `.env` configurado, desde la raíz del proyecto:

```powershell
docker compose up --build -d
docker compose ps
```

Compose inicia MongoDB con volumen persistente, espera a que la base de datos esté saludable antes de arrancar gRPC y espera al servicio gRPC antes de iniciar GraphQL. Los endpoints publicados son `localhost:50051` (gRPC), `localhost:8000/graphql` (GraphQL) y `localhost:27017` (MongoDB). Para detener los servicios sin borrar los datos:

```powershell
docker compose down
```

Para borrar también los datos persistidos de MongoDB:

```powershell
docker compose down --volumes
```

Si configuras usuario y contraseña de MongoDB en `.env`, Compose los usa para inicializar MongoDB y para conectar el backend. La base de datos de este Compose usa un volumen separado de cualquier instalación local de MongoDB.

## Diagrama de arquitectura

El diagrama actualizado, su especificación Archify y las evidencias del navegador están en [`arquitectura de software/`](arquitectura%20de%20software/arquitectura-biblioteca.html).
