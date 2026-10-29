package com.example.biblioteca

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                LibraryScreen()
            }
        }
    }
}

@Composable
private fun LibraryScreen(client: GraphQlClient = remember { GraphQlClient() }) {
    val scope = rememberCoroutineScope()
    var books by remember { mutableStateOf(emptyList<Book>()) }
    var selectedId by remember { mutableStateOf<String?>(null) }
    var id by remember { mutableStateOf("") }
    var title by remember { mutableStateOf("") }
    var author by remember { mutableStateOf("") }
    var year by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }
    var feedback by remember { mutableStateOf<String?>(null) }
    var hasError by remember { mutableStateOf(false) }

    fun resetForm() {
        selectedId = null
        id = ""
        title = ""
        author = ""
        year = ""
    }

    fun request(action: suspend () -> Unit) {
        scope.launch {
            loading = true
            feedback = null
            hasError = false
            try {
                action()
            } catch (error: Exception) {
                feedback = error.message ?: "No fue posible completar la operación."
                hasError = true
            } finally {
                loading = false
            }
        }
    }

    fun refreshBooks() {
        request { books = client.listBooks() }
    }

    fun openBook(bookId: String) {
        request {
            val book = client.getBook(bookId)
            selectedId = book.id
            id = book.id
            title = book.titulo
            author = book.autor
            year = book.anioPublicacion.toString()
        }
    }

    fun saveBook() {
        val parsedYear = year.toIntOrNull()
        if (id.isBlank() || title.isBlank() || author.isBlank() || parsedYear == null) {
            feedback = "Completa un ID, título, autor y año válido."
            hasError = true
            return
        }
        val book = Book(id.trim(), title.trim(), author.trim(), parsedYear)
        request {
            feedback = if (selectedId == null) {
                client.addBook(book)
            } else {
                client.updateBook(book)
            }
            books = client.listBooks()
            resetForm()
        }
    }

    fun removeBook(book: Book) {
        request {
            feedback = client.deleteBook(book.id)
            books = client.listBooks()
            if (selectedId == book.id) resetForm()
        }
    }

    LaunchedEffect(Unit) {
        refreshBooks()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("Biblioteca", style = MaterialTheme.typography.headlineMedium)
        Text("Gestiona libros mediante la API GraphQL.")

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Libros (${books.size})", style = MaterialTheme.typography.titleLarge)
            OutlinedButton(onClick = ::refreshBooks, enabled = !loading) {
                Text("Actualizar lista")
            }
        }

        if (loading) {
            CircularProgressIndicator()
        }
        feedback?.let { text ->
            Text(
                text = text,
                color = if (hasError) MaterialTheme.colorScheme.error
                else MaterialTheme.colorScheme.primary
            )
        }

        if (books.isEmpty() && !loading) {
            Text("No hay libros para mostrar.")
        }
        books.forEach { book ->
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(book.titulo, style = MaterialTheme.typography.titleMedium)
                    Text("${book.autor} · ${book.anioPublicacion} · ID ${book.id}")
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        OutlinedButton(onClick = { openBook(book.id) }, enabled = !loading) {
                            Text("Ver / editar")
                        }
                        OutlinedButton(onClick = { removeBook(book) }, enabled = !loading) {
                            Text("Eliminar")
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(4.dp))
        Text(
            if (selectedId == null) "Agregar libro" else "Editar libro",
            style = MaterialTheme.typography.titleLarge
        )
        OutlinedTextField(
            value = id,
            onValueChange = { id = it },
            label = { Text("ID numérico") },
            enabled = selectedId == null && !loading,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = title,
            onValueChange = { title = it },
            label = { Text("Título") },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = author,
            onValueChange = { author = it },
            label = { Text("Autor") },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = year,
            onValueChange = { year = it },
            label = { Text("Año de publicación") },
            enabled = !loading,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = ::saveBook, enabled = !loading) {
                Text(if (selectedId == null) "Agregar" else "Guardar cambios")
            }
            if (selectedId != null) {
                OutlinedButton(onClick = ::resetForm, enabled = !loading) {
                    Text("Cancelar")
                }
            }
        }
    }
}
