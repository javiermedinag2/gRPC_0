package com.example.biblioteca

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

data class Book(
    val id: String,
    val titulo: String,
    val autor: String,
    val anioPublicacion: Int
)

class GraphQlClient(private val endpoint: String = BuildConfig.GRAPHQL_URL) {
    suspend fun listBooks(): List<Book> = withContext(Dispatchers.IO) {
        val data = execute(
            "query { libros { id titulo autor anioPublicacion } }"
        )
        val books = data.getJSONArray("libros")
        (0 until books.length()).map { index -> books.getJSONObject(index).toBook() }
    }

    suspend fun getBook(id: String): Book = withContext(Dispatchers.IO) {
        val variables = JSONObject().put("id", id)
        val data = execute(
            "query GetBook(\$id: ID!) { libro(id: \$id) { id titulo autor anioPublicacion } }",
            variables
        )
        data.getJSONObject("libro").toBook()
    }

    suspend fun addBook(book: Book): String = withContext(Dispatchers.IO) {
        val data = execute(
            "mutation AddBook(\$input: LibroInput!) { " +
                "agregarLibro(input: \$input) { id mensaje } }",
            JSONObject().put("input", book.toInput())
        )
        data.getJSONObject("agregarLibro").getString("mensaje")
    }

    suspend fun updateBook(book: Book): String = withContext(Dispatchers.IO) {
        val data = execute(
            "mutation UpdateBook(\$input: LibroInput!) { " +
                "actualizarLibro(input: \$input) { id mensaje } }",
            JSONObject().put("input", book.toInput())
        )
        data.getJSONObject("actualizarLibro").getString("mensaje")
    }

    suspend fun deleteBook(id: String): String = withContext(Dispatchers.IO) {
        val data = execute(
            "mutation DeleteBook(\$id: ID!) { eliminarLibro(id: \$id) { id mensaje } }",
            JSONObject().put("id", id)
        )
        data.getJSONObject("eliminarLibro").getString("mensaje")
    }

    private fun execute(query: String, variables: JSONObject = JSONObject()): JSONObject {
        val connection = URL(endpoint).openConnection() as HttpURLConnection
        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = 5_000
            connection.readTimeout = 5_000
            connection.doOutput = true
            connection.setRequestProperty("Content-Type", "application/json")
            val payload = JSONObject()
                .put("query", query)
                .put("variables", variables)
                .toString()
            connection.outputStream.use { output ->
                output.write(payload.toByteArray(Charsets.UTF_8))
            }

            val status = connection.responseCode
            val responseStream = if (status in 200..299) {
                connection.inputStream
            } else {
                connection.errorStream
            }
            val responseBody = responseStream?.bufferedReader()?.use { it.readText() }.orEmpty()
            if (status !in 200..299) {
                throw IOException("El API GraphQL respondió HTTP $status: $responseBody")
            }

            val response = try {
                JSONObject(responseBody)
            } catch (error: Exception) {
                throw IOException("El API GraphQL devolvió una respuesta inválida.", error)
            }
            val errors = response.optJSONArray("errors")
            if (errors != null && errors.length() > 0) {
                throw IOException(errors.toGraphQlMessage())
            }
            return response.optJSONObject("data")
                ?: throw IOException("El API GraphQL no devolvió datos.")
        } finally {
            connection.disconnect()
        }
    }

    private fun Book.toInput(): JSONObject = JSONObject()
        .put("id", id)
        .put("titulo", titulo)
        .put("autor", autor)
        .put("anioPublicacion", anioPublicacion)

    private fun JSONObject.toBook(): Book = Book(
        id = getString("id"),
        titulo = getString("titulo"),
        autor = getString("autor"),
        anioPublicacion = getInt("anioPublicacion")
    )

    private fun JSONArray.toGraphQlMessage(): String =
        (0 until length()).mapNotNull { index ->
            optJSONObject(index)?.optString("message")?.takeIf(String::isNotBlank)
        }.joinToString(separator = "\n")
            .ifBlank { "El API GraphQL informó un error." }
}
