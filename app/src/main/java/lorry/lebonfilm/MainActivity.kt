package lorry.lebonfilm

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.LocationSearching
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.tooling.preview.PreviewScreenSizes
import lorry.lebonfilm.ui.theme.LeBonFilmTheme
import androidx.compose.material3.TextField
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.font.FontWeight.Companion.Bold
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            LeBonFilmTheme {
                LeBonFilmApp()
            }
        }
    }
}

@PreviewScreenSizes
@Composable
fun LeBonFilmApp() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.STATIONS) }

    Spacer(modifier = Modifier.height(60.dp))

    NavigationSuiteScaffold(
        navigationSuiteItems = {
            AppDestinations.entries.forEach {
                item(
                    icon = {
                        Icon(
                            imageVector = it.icon,
                            contentDescription = it.label
                        )
                    },
                    label = { Text(it.label) },
                    selected = it == currentDestination,
                    onClick = { currentDestination = it }
                )
            }
        }
    ) {
        Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
            Column(modifier = Modifier.padding(innerPadding)
                    .fillMaxWidth()) {
                Text(
                    text = "PROGRAMMES DE RADIO",
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 25.sp,
                    modifier = Modifier.padding(top = 25.dp, bottom = 10.dp)
                        .align(Alignment.CenterHorizontally)
                )
                currentDestination.content?.invoke(innerPadding)
            }
        }
    }
}

enum class AppDestinations(
    val label: String,
    val icon: ImageVector,
    var content: @Composable ((PaddingValues) -> Unit)? = null
) {
    STATIONS("Stations", Icons.Default.Home,
        { padding: PaddingValues ->





            Greeting(
                name = "Stations",
                modifier = Modifier.padding(padding)
            )
        }),
    AJOUT("Nouvelle", Icons.Default.LocationSearching,
        { padding: PaddingValues ->
            var searchedStation by rememberSaveable { mutableStateOf("") }
            var candidates by rememberSaveable { mutableStateOf(listOf<String>()) }

            Column(
                modifier = Modifier.padding(padding)
            ){
                TextField(
                    value = searchedStation,
                    onValueChange = { searchedStation = it},
                    label = { Text("Rechercher") },
                    placeholder = @Composable { Text("station")},
                )

                Spacer(modifier = Modifier.height(20.dp))

                Text(
                    text = "Candidats",
                    fontWeight = Bold,
                    modifier = Modifier
                )

                Spacer(modifier = Modifier.height(20.dp))

                Column(
                    modifier = Modifier
                ){
                    candidates
                        .take(10)
                        .forEach { candidate ->
                            Text(
                                modifier = Modifier,
                                text = candidate,
                            )
                    }
                }
            }
        })
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "$name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    LeBonFilmTheme {
        Greeting("Android")
    }
}