package lorry.radiosonde

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.LocationSearching
import androidx.compose.material.icons.filled.Search
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
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.tooling.preview.PreviewScreenSizes
import lorry.radiosonde.ui.theme.RadioSondeTheme
import androidx.compose.material3.Icon

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RadioSondeTheme {
                RadioSondeApp()
            }
        }
    }
}

@PreviewScreenSizes
@Composable
fun RadioSondeApp() {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.STATIONS) }

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
            currentDestination.content?.invoke(innerPadding)
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
            Greeting(
                name = "Ajout",
                modifier = Modifier.padding(padding)
            )
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
    RadioSondeTheme {
        Greeting("Android")
    }
}