"""
Operaciones de datos para ORION (CSV, JSON, Análisis).
"""
import json
import os
import pandas as pd
from registry import register_function


@register_function(
    name="convert_csv_to_json",
    description="Convierte un archivo CSV a formato JSON",
    argument_types={
        "input_path": "str",
        "output_path": "str"
    }
)
def convert_csv_to_json(input_path, output_path):
    """Convierte un archivo CSV a JSON."""
    df = pd.read_csv(input_path)
    data = df.to_dict(orient="records")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return f"{input_path} convertido a JSON en {output_path}"


@register_function(
    name="analyze_data",
    description="Analiza un CSV y genera estadísticas básicas",
    argument_types={"input_path": "str", "output_path": "str"}
)
def analyze_data(input_path, output_path):
    """Analiza un dataset CSV y guarda estadísticas."""
    # Corregir rutas mal formadas
    if input_path.startswith('./'):
        input_path = input_path[2:]
    elif input_path.startswith('.data'):
        input_path = input_path.replace('.data', 'data', 1)

    # Si output_path está vacío o es inválido, generar uno automático
    if not output_path or output_path in ['.', '..', '/']:
        base_name = os.path.basename(input_path).replace('.csv', '')
        output_path = f"output/analisis_{base_name}.json"

    # Asegurar que el directorio output existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df = pd.read_csv(input_path)

    # Análisis automático
    analysis = {
        "total_filas": len(df),
        "total_columnas": len(df.columns),
        "columnas": list(df.columns),
        "tipos_datos": df.dtypes.to_dict(),
        "estadisticas": df.describe().to_dict(),
        "valores_faltantes": df.isnull().sum().to_dict()
    }

    # Guardar análisis
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, default=str)

    return (
        f"Análisis guardado en {output_path}. "
        f"Dataset: {len(df)} filas x {len(df.columns)} columnas"
    )
