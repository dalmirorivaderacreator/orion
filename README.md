ORION - Sistema de Ejecución de Lenguaje Natural

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![IA](https://img.shields.io/badge/IA-LLM%20%2B%20DSL-orange)
![Estado](https://img.shields.io/badge/Estado-Production%20Ready-brightgreen)

🚀 ORION es un sistema modular que permite escribir un DSL (lenguaje declarativo simple) para describir tareas de datos y automatización. Un dispatcher interpreta este DSL y ejecuta funciones Python reales, traduciendo instrucciones en lenguaje natural a código ejecutable mediante LLM.

## 🎥 Demo en Vivo

![ORION Web UI Demo](orion_demo.gif)

![Demo Orion](https://github.com/user-attachments/assets/1a4081a4-36b4-4d79-8110-4829aa2f5b55)


🌟 Flujo Principal

```
Texto HUMANO (español) → LLM (traductor) → DSL JSON → DISPATCHER → FUNCIONES PYTHON → RESULTADO REAL
```

🏗️ Arquitectura del Sistema

Estructura de Carpetas

```
orion/
├── core/                   # Componentes principales del sistema
│   ├── __init__.py
│   ├── registry.py         # Sistema de registro automático
│   ├── dispatcher.py       # Ejecutor de funciones
│   └── llmclient.py        # Cliente LLM (Ollama + fallback)
├── plugins/                # Funciones organizadas por categoría
│   ├── __init__.py
│   ├── dataops.py          # Operaciones con datos
│   ├── fileops.py          # Operaciones con archivos
│   └── webops.py           # Operaciones web
├── data/                   # Datos de ejemplo
│   └── ventas.csv
├── output/                 # Resultados generados
├── tests/                  # Tests automatizados
│   └── test_basic.py
├── main.py                 # CLI principal
└── requirements.txt        # Dependencias
```

🔧 Componentes Detallados

1. Registry.py - Sistema de Registro Automático

```python
_function_registry = {}  # Diccionario global de funciones

def register_function(name, description, argument_types):  # Decorador
def get_available_functions():  # Lista funciones
def get_function(name):  # Obtiene función por nombre
def build_system_prompt():  # Genera prompt para LLM
```

2. Dispatcher.py - Ejecutor Dinámico

```python
def dispatch(function_name: str, arguments: dict):
    # Busca en registry → ejecuta función → maneja errores
```

3. LLMClient.py - Cliente LLM Inteligente

```python
def ask_orion(user_prompt):
    # Intenta con Ollama (phi3:mini) → timeout 30s
    # Si falla → usa mock fallback
    # Parsea y limpia JSON response
```

📋 Funciones Actualmente Registradas

DataOps.py

```python
@register_function(
    name="convert_csv_to_json",
    description="Convierte un archivo CSV a formato JSON",
    argument_types={"input_path": "str", "output_path": "str"}
)

@register_function(
    name="process_data",
    description="Filtra y procesa datos de un CSV",
    argument_types={
        "input_path": "str",
        "output_path": "str",
        "filter_column": "str",
        "filter_value": "str"
    }
)

@register_function(
    name="analyze_data",
    description="Genera análisis estadístico de un dataset",
    argument_types={"input_path": "str", "output_path": "str"}
)
```

FileOps.py

```python
@register_function(
    name="create_folder",
    description="Crea una carpeta nueva",
    argument_types={"path": "str"}
)

@register_function(
    name="list_files",
    description="Lista archivos en una carpeta",
    argument_types={"path": "str"}
)

@register_function(
    name="download_file",
    description="Descarga un archivo desde una URL",
    argument_types={"url": "str", "output_path": "str"}
)
```

🚀 Instalación Rápida

Prerrequisitos

· Python 3.6 o superior
· Ollama instalado y ejecutándose

Configuración en 3 Pasos

```bash
# 1. Clonar y entrar al directorio
git clone https://github.com/dalmirorivaderacreator/orion
cd orion

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar modelo LLM
ollama pull phi3:mini
```

requirements.txt

```txt
pandas>=1.3.0
requests>=2.25.0
python-dotenv>=0.19.0
typing-extensions>=4.0.0
```

⚙️ Configuración

Crea un archivo .env:

```env
ORION_LLM_MODEL=phi3:mini
ORION_TIMEOUT=30
ORION_LOG_LEVEL=INFO
ORION_MAX_RETRIES=3
```

🎮 Ejecución

```bash
# Modo interactivo
python main.py

# Ejecución directa
python main.py "crea una carpeta llamada proyectos"
```

🧪 Tests

```bash
# Ejecutar tests básicos
python -m pytest tests/ -v

# Verificar cobertura
python -m pytest tests/ --cov=orion

# Tests específicos
python tests/test_basic.py
```

💡 Ejemplos de Uso Comprobados

Ejemplo 1: Gestión de Archivos

```
USUARIO: "creá una carpeta llamada pruebas"
LLM: {"CALL": "create_folder", "ARGS": {"path": "pruebas"}}
DISPATCHER: → ejecuta create_folder("pruebas")
RESULTADO: "Carpeta creada: pruebas"
```

Ejemplo 2: Análisis de Datos Complejo

```
USUARIO: "descargá dataset iris y analizalo"
LLM: {
  "CALL": "download_file", 
  "ARGS": {
    "url": "https://raw.githubusercontent.com/.../iris.csv",
    "output_path": "data/iris.csv"
  }
}
→ luego →
{
  "CALL": "analyze_data",
  "ARGS": {
    "input_path": "data/iris.csv", 
    "output_path": "output/analysis.json"
  }
}
RESULTADO: "Análisis completado: 150 filas × 5 columnas"
```

Ejemplo Interactivo

```python
>>> Bienvenido a ORION v2.0
>>> Ingrese su comando: "analiza ventas.csv y crea un reporte"
>>> Procesando: download_file → analyze_data → create_report
>>> Resultado: Reporte generado en output/analysis_20241205.json
```

🛠️ Características de Robustez Implementadas

Manejo de Errores Elegante

```python
def dispatch(function_name: str, arguments: dict):
    # Validación de funciones existentes
    # Validación de argumentos requeridos  
    # Manejo específico por tipo de error
    # Mensajes de error claros para humanos
```

Validación Estricta de JSON

```python
def _validate_and_clean_json(response_text):
    # Limpieza de code blocks
    # Validación de estructura
    # Forzado de formato ORION
    # Fallback seguro a {CALL: null}
```

Fallback Inteligente Contextual

```python
def _smart_fallback(user_prompt):
    # Análisis semántico del prompt
    # Valores por defecto inteligentes
    # Archivos conocidos (data/ventas.csv)
    # Rutas relativas seguras
```

🎨 Principios de Diseño

· Modularidad: Funciones se auto-registran, cero configuración
· Robustez: Funciona con/sin LLM, con/sin funciones específicas
· Escalabilidad: Agregar funciones = decorador + implementación
· UX Natural: Lenguaje humano → resultados reales
· Extensibilidad: Fácil agregar nuevos tipos de operaciones

🚀 Contribuir en 5 Minutos

Agregar Nueva Función

```python
# En plugins/yourops.py
@register_function(
    name="send_email",
    description="Envía un correo electrónico",
    argument_types={"to": "str", "subject": "str", "body": "str"}
)
def send_email(to: str, subject: str, body: str):
    # Tu implementación aquí
    return f"Email enviado a {to}"
```

El sistema detecta automáticamente la nueva función. ¡Ya puedes decir "envía un email a prueba@test.com"!

🔍 Solución de Problemas

Ollama no responde

```bash
# Verificar servicio
ollama list
# Reiniciar servicio
ollama serve
```

Error de importación

```bash
pip install --upgrade pandas requests
```

JSON malformado

El sistema usa fallback automático. Verifique que Ollama esté usando el modelo correcto.

Timeout en LLM

```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags
```

📈 Status del Sistema

· Registry: 6 funciones registradas
· Dispatcher: Ejecución estable
· LLM Client: Ollama + Fallback operativo
· Sistema de Tests: Básico implementado
· Context Manager: En desarrollo
· Web UI: Planeado
· Plugin System: En diseño

🔮 Roadmap

Corto Plazo (1-2 horas)

· Sistema de logging para auditoría
· Variables de contexto entre comandos
· 2-3 funciones más (email, plots, DB)

Medio Plazo (1 día)

· Interface web simple
· Pipelines multi-step
· Templates de flujos comunes

Largo Plazo

· Agente autónomo con memoria
· Plugins de terceros
· Deployment cloud

📊 Estado Actual Comprobado

✅ 5+ funciones registradas y operativas
✅ Validación JSON 100% robusta
✅ Manejo de errores elegante
✅ Fallback inteligente cuando LLM falla
✅ Análisis de datos profesional implementado
✅ Pipeline confiable de extremo a extremo
✅ Sistema de tests básico funcionando

📦 Metadata

· Versión: 2.0.0
· Autor: Dalmiro Rivadera
· Licencia: MIT
· Repositorio: https://github.com/dalmirorivaderacreator/orion
· Última Actualización: Noviembre 2025

---

ORION v2.0 - Transformando lenguaje natural en ejecución real desde 2025.

¿Problemas? Consulta la sección Solución de Problemas o abre un issue en el repositorio.

¿Te sirvió ORION? ¡Dale una ⭐ en GitHub!
