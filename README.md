# ORION v2.1 - Sistema de Ejecución de Lenguaje Natural

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![IA](https://img.shields.io/badge/IA-LLM%20%2B%20DSL-orange)
![Estado](https://img.shields.io/badge/Estado-Production%20Ready-brightgreen)
![CI/CD](https://img.shields.io/badge/CI%2FCD-Passing-success)
![Code Quality](https://img.shields.io/badge/Quality-10%2F10-brightgreen)

🚀 **ORION** es un sistema modular que permite escribir un DSL (lenguaje declarativo simple) para describir tareas de datos y automatización. Un dispatcher interpreta este DSL y ejecuta funciones Python reales, traduciendo instrucciones en lenguaje natural a código ejecutable mediante LLM.

## 🎥 Demo en Vivo

![ORION Web UI Demo](orion_demo.gif)

![Demo Orion](https://github.com/user-attachments/assets/1a4081a4-36b4-4d79-8110-4829aa2f5b55)

## 🌟 Novedades v2.1

- **✅ Web UI Moderna**: Interfaz de chat completa construida con Streamlit.
- **✅ Logging Profesional**: Sistema de logs estructurados en JSON (`logs/orion.log`).
- **✅ CI/CD Robusto**: Pipeline de GitHub Actions con Pylint (Score 10/10).
- **✅ Estructura Mejorada**: Organización modular de funciones y DSL.

## 🏗️ Arquitectura del Sistema

### Estructura de Carpetas

```
orion/
├── .github/
│   └── workflows/          # CI/CD Pipelines
│       └── ci.yml          # Pylint Workflow
├── dsl/                    # Definición del Lenguaje
│   ├── dsl_parser.py       # Parser YAML
│   └── dsl_spec.py         # Especificación del DSL
├── functions/              # Módulos de Funciones
│   ├── __init__.py
│   ├── data_ops.py         # Operaciones de Datos (Pandas)
│   └── file_ops.py         # Operaciones de Archivos
├── logs/                   # Logs del sistema
│   └── orion.log
├── app.py                  # Interfaz Web (Streamlit)
├── main.py                 # CLI Principal
├── runner.py               # Ejecutor de Pipelines YAML
├── llm_client.py           # Cliente LLM (Ollama + Fallback)
├── dispatcher.py           # Ejecutor de Funciones
├── registry.py             # Sistema de Registro
├── logger.py               # Configuración de Logging
└── requirements.txt        # Dependencias
```

## 🚀 Instalación Rápida

### Prerrequisitos

- Python 3.8 o superior
- Ollama instalado y ejecutándose (`ollama serve`)

### Configuración en 3 Pasos

```bash
# 1. Clonar y entrar al directorio
git clone https://github.com/dalmirorivaderacreator/orion
cd orion

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar modelo LLM
ollama pull phi3:mini
```

### requirements.txt

```txt
pandas>=1.3.0
requests>=2.25.0
streamlit>=1.30.0
pyyaml>=6.0
python-dotenv>=0.19.0
typing-extensions>=4.0.0
```

## 🎮 Ejecución

### Opción A: Interfaz Web (Recomendada)

```bash
streamlit run app.py
```
Esto abrirá una interfaz moderna en tu navegador donde puedes chatear con ORION.

### Opción B: Línea de Comandos (CLI)

```bash
# Modo interactivo
python main.py

# Ejecución directa
python main.py "crea una carpeta llamada proyectos"
```

### Opción C: Ejecutar Pipelines YAML

```bash
python runner.py mi_pipeline.yaml
```

## 💡 Ejemplos de Uso

### Ejemplo 1: Gestión de Archivos
**Usuario**: "creá una carpeta llamada pruebas"
**ORION**:
1. LLM detecta intención.
2. Ejecuta `create_folder("pruebas")`.
3. Resultado: "✅ Carpeta creada: pruebas"

### Ejemplo 2: Análisis de Datos
**Usuario**: "descargá dataset iris y analizalo"
**ORION**:
1. Descarga el archivo desde URL.
2. Ejecuta `analyze_data`.
3. Genera reporte JSON en `output/`.

## 🛠️ Características Técnicas

### Logging Estructurado
Cada acción se registra en `logs/orion.log` con formato JSON para fácil auditoría:
```json
{
  "timestamp": "2025-11-21T18:00:00",
  "level": "INFO",
  "message": "Ejecución exitosa",
  "module": "dispatcher",
  "function": "dispatch"
}
```

### Calidad de Código (CI/CD)
El proyecto cuenta con un pipeline de integración continua que asegura:
- **Linting estricto**: Pylint 10.00/10.
- **Cero errores de sintaxis**.
- **Estilo consistente** (PEP 8).

## 📈 Status del Sistema

| Componente | Estado | Versión |
|------------|--------|---------|
| **Core** | ✅ Estable | 2.1 |
| **Web UI** | ✅ Implementado | 1.0 |
| **LLM Client** | ✅ Ollama + Fallback | 2.1 |
| **CI/CD** | ✅ GitHub Actions | 1.0 |
| **Logging** | ✅ JSON Structured | 1.0 |

## 📦 Metadata

- **Versión**: 2.1.0
- **Autor**: Dalmiro Rivadera
- **Licencia**: MIT
- **Repositorio**: https://github.com/dalmirorivaderacreator/orion
- **Última Actualización**: Noviembre 2025

---

**ORION v2.1** - Transformando lenguaje natural en ejecución real.

¿Te sirvió ORION? ¡Dale una ⭐ en GitHub!
