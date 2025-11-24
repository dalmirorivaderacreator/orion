# Sistema de Plugins de ORION - Guía para Desarrolladores

## Descripción General

El Sistema de Plugins de ORION proporciona una arquitectura modular para extender la funcionalidad de ORION sin modificar el código core. Los plugins pueden registrar nuevas funciones, agregar capacidades e integrarse con servicios externos.

## Arquitectura

### Componentes Core

- **`PluginBase`**: Clase base abstracta que todos los plugins deben heredar
- **`PluginManager`**: Sistema central de orquestación para el ciclo de vida de plugins
- **Registro de Funciones**: Punto de integración con el sistema de funciones existente de ORION

### Descubrimiento de Plugins

Los plugins se descubren automáticamente desde dos ubicaciones:
1. `core/plugins/` - Plugins integrados que vienen con ORION
2. `~/.orion/plugins/` - Plugins de terceros instalados por el usuario

## Crear un Plugin

### Paso 1: Crear Directorio del Plugin

```bash
mkdir -p core/plugins/mi_plugin
cd core/plugins/mi_plugin
```

### Paso 2: Crear Estructura de Paquete

Crear `__init__.py`:
```python
"""
Mi Plugin para ORION
"""
from core.plugins.mi_plugin.plugin import MiPlugin

__all__ = ['MiPlugin']
```

### Paso 3: Implementar Clase del Plugin

Crear `plugin.py`:
```python
"""
Implementación de Mi Plugin
"""
from core.plugins.plugin_base import PluginBase
from registry import register_function


class MiPlugin(PluginBase):
    """
    Mi plugin personalizado para ORION.
    """

    @property
    def name(self) -> str:
        return "mi_plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Descripción de lo que hace mi plugin"

    @property
    def author(self) -> str:
        return "Tu Nombre"

    @property
    def dependencies(self) -> list:
        """Lista de paquetes Python requeridos"""
        return ["requests", "algun-paquete"]

    def initialize(self) -> bool:
        """
        Inicializa los recursos del plugin.
        Retorna True si fue exitoso, False en caso contrario.
        """
        try:
            # Verificar dependencias
            import requests  # pylint: disable=import-outside-toplevel,unused-import

            # Inicializar recursos
            self.set_config("api_key", "tu-api-key")

            return True
        except ImportError:
            self.error_state = "Dependencias faltantes"
            return False

    def shutdown(self) -> None:
        """Limpia recursos cuando el plugin se descarga."""
        # Cerrar conexiones, guardar estado, etc.

    def register_functions(self) -> None:
        """Registra funciones del plugin con ORION."""

        @register_function(
            name="mi_funcion",
            description="Hace algo útil",
            argument_types={
                "input_path": "str",
                "output_path": "str"
            }
        )
        def mi_funcion(input_path: str, output_path: str) -> str:
            """
            Implementación de la función.

            Args:
                input_path: Ruta del archivo de entrada
                output_path: Ruta del archivo de salida

            Returns:
                Mensaje de estado
            """
            # Tu implementación aquí
            return f"Procesado {input_path} -> {output_path}"
```

### Paso 4: Agregar Dependencias (Opcional)

Crear `requirements.txt`:
```
requests>=2.28.0
algun-paquete>=1.0.0
```

## Ciclo de Vida del Plugin

### Hooks del Ciclo de Vida

1. **`initialize()`**: Llamado una vez cuando el plugin se carga
2. **`on_enable()`**: Llamado cuando el plugin se habilita
3. **`on_disable()`**: Llamado cuando el plugin se deshabilita
4. **`shutdown()`**: Llamado cuando el plugin se descarga

### Flujo del Ciclo de Vida

```
Cargar Plugin → initialize() → register_functions() → on_enable()
                                                          ↓
                                                      [ACTIVO]
                                                          ↓
                                              on_disable() → shutdown()
```

## Referencia de API

### Métodos de PluginBase

#### Configuración
- `get_config(key, default=None)`: Obtener valor de configuración
- `set_config(key, value)`: Establecer valor de configuración

#### Estado
- `get_status()`: Obtener diccionario de estado del plugin
- `enabled`: Propiedad booleana indicando si el plugin está activo
- `loaded`: Propiedad booleana indicando si el plugin está cargado
- `error_state`: String describiendo cualquier condición de error

### Métodos de PluginManager

#### Descubrimiento y Carga
- `discover_plugins()`: Encontrar plugins disponibles
- `load_plugin(name)`: Cargar un plugin específico
- `load_all_plugins()`: Cargar todos los plugins descubiertos
- `unload_plugin(name)`: Descargar un plugin
- `reload_plugin(name)`: Recargar un plugin en caliente

#### Gestión
- `get_plugin(name)`: Obtener instancia del plugin
- `list_plugins()`: Obtener estado de todos los plugins
- `enable_plugin(name)`: Habilitar un plugin
- `disable_plugin(name)`: Deshabilitar un plugin

## Registrar Funciones

Las funciones registradas por plugins se vuelven disponibles automáticamente para el dispatcher LLM de ORION.

### Ejemplo de Registro de Función

```python
from registry import register_function

@register_function(
    name="procesar_datos",
    description="Procesa datos de entrada y genera salida",
    argument_types={
        "input_path": "str",
        "formato": "str",
        "output_path": "str"
    }
)
def procesar_datos(input_path: str, formato: str, output_path: str) -> str:
    """Procesa datos con el formato especificado."""
    # Implementación
    return f"Datos procesados: {output_path}"
```

### Mejores Prácticas

1. **Descripciones Claras**: Usa descripciones en español que expliquen claramente qué hace la función
2. **Type Hints**: Siempre especifica tipos de argumentos en `argument_types`
3. **Manejo de Errores**: Retorna mensajes de error descriptivos, no lances excepciones
4. **Valores de Retorno**: Retorna mensajes de estado legibles para humanos
5. **Manejo de Rutas**: Usa `os.path` para compatibilidad multiplataforma

## Plugins de Ejemplo

### file_processor
Operaciones de archivos en lote, detección de duplicados, compresión.

**Funciones:**
- `batch_rename_files(directory, pattern, replacement)` - Renombrado masivo
- `find_duplicates(directory)` - Detección de duplicados por hash MD5
- `compress_files(directory, output_archive)` - Compresión ZIP con estadísticas

### web_scraper
Web scraping y extracción de contenido.

**Funciones:**
- `scrape_webpage(url, selector)` - Extracción con selectores CSS
- `extract_links(url)` - Descubrimiento de enlaces
- `download_images(url, output_dir)` - Descarga de imágenes

**Dependencias:** `beautifulsoup4`, `lxml`

### data_analyzer
Análisis de datos avanzado y visualización.

**Funciones:**
- `generate_chart(csv_path, chart_type, output_path)` - Gráficos (barras, líneas, dispersión, torta)
- `detect_outliers(csv_path, column)` - Detección de outliers (método IQR)
- `correlation_matrix(csv_path, output_path)` - Matriz de correlación con heatmaps

**Dependencias:** `matplotlib`, `seaborn`

## Probar Tu Plugin

Crear archivo de test en `tests/test_mi_plugin.py`:

```python
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.plugins import PluginManager
from registry import get_function


class TestMiPlugin(unittest.TestCase):
    def setUp(self):
        self.manager = PluginManager()
        self.manager.load_plugin("mi_plugin")

    def test_plugin_cargado(self):
        plugin = self.manager.get_plugin("mi_plugin")
        self.assertIsNotNone(plugin)
        self.assertTrue(plugin.enabled)

    def test_funcion_registrada(self):
        func = get_function("mi_funcion")
        self.assertIsNotNone(func)

    def test_ejecucion_funcion(self):
        func = get_function("mi_funcion")
        result = func['function'](
            input_path="test.txt",
            output_path="output.txt"
        )
        self.assertIn("Procesado", result)


if __name__ == '__main__':
    unittest.main()
```

## Debugging

### Habilitar Logging de Debug

Revisa `logs/orion.log` para mensajes relacionados con plugins:
- Descubrimiento de plugins
- Éxito/fallo de carga
- Registro de funciones
- Errores y excepciones

### Problemas Comunes

**Plugin no descubierto:**
- Asegúrate que `__init__.py` y `plugin.py` existan
- Verifica que el directorio del plugin esté en la ruta de búsqueda

**Plugin falla al cargar:**
- Verifica que `initialize()` retorne `True`
- Confirma que las dependencias estén instaladas
- Revisa los logs para mensajes de error

**Funciones no disponibles:**
- Asegúrate que `register_functions()` sea llamado
- Verifica que los nombres de funciones no entren en conflicto
- Confirma que el decorador `@register_function` se use correctamente

## Distribución

### Empaquetar para Distribución

1. Crear directorio del plugin con todos los archivos
2. Incluir `requirements.txt` para dependencias
3. Agregar `README.md` con instrucciones de uso
4. Empaquetar como ZIP o distribuir vía Git

### Instalación por Usuarios

```bash
# Clonar al directorio de plugins del usuario
cd ~/.orion/plugins
git clone https://github.com/usuario/mi-plugin.git

# Instalar dependencias
cd mi-plugin
pip install -r requirements.txt

# Reiniciar ORION
```

## Temas Avanzados

### Configuración de Plugin

Almacenar configuración persistente:

```python
import json
import os

def initialize(self):
    # Cargar desde archivo de configuración
    config_path = os.path.expanduser("~/.orion/mi_plugin_config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
            for key, value in config.items():
                self.set_config(key, value)
    return True
```

### Comunicación Entre Plugins

Acceder a otros plugins vía PluginManager:

```python
def mi_funcion(self):
    # Obtener instancia del plugin manager
    from core.plugins import PluginManager
    manager = PluginManager()

    # Acceder a otro plugin
    otro_plugin = manager.get_plugin("otro_plugin")
    if otro_plugin and otro_plugin.enabled:
        # Usar funcionalidad del otro plugin
        pass
```

### Hot Reload Durante Desarrollo

```python
# En consola de ORION
>>> from core.plugins import PluginManager
>>> manager = PluginManager()
>>> manager.reload_plugin("mi_plugin")
```

## Soporte

Para preguntas o problemas:
- Revisa los logs: `logs/orion.log`
- Examina los plugins de ejemplo en `core/plugins/`
- Consulta la suite de tests en `tests/test_plugin_system.py`
