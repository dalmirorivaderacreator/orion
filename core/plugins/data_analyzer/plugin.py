"""
Data Analyzer Plugin

Provides advanced data analysis and visualization capabilities.
"""

import os
import json
from typing import List
from core.plugins.plugin_base import PluginBase
from registry import register_function


class DataAnalyzerPlugin(PluginBase):
    """
    Plugin for advanced data analysis operations.

    Provides:
    - Chart generation from CSV data
    - Statistical outlier detection
    - Correlation matrix generation

    Note: Requires matplotlib and seaborn for visualizations.
    """

    @property
    def name(self) -> str:
        return "data_analyzer"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Advanced data analysis: charts, outlier detection, correlations"

    @property
    def author(self) -> str:
        return "ORION Team"

    @property
    def dependencies(self) -> List[str]:
        return ["matplotlib", "seaborn"]

    def initialize(self) -> bool:
        """Initialize the data analyzer plugin."""
        # Check if required packages are available
        try:
            import matplotlib  # pylint: disable=import-outside-toplevel,unused-import
            import seaborn  # pylint: disable=import-outside-toplevel,unused-import
            return True
        except ImportError as e:
            self.error_state = f"Missing dependency: {e}"
            # Still return True to allow plugin to load (functions will handle errors)
            return True

    def shutdown(self) -> None:
        """Clean up resources."""

    def register_functions(self) -> None:  # pylint: disable=too-many-statements
        """Register data analysis functions with ORION."""

        @register_function(
            name="generate_chart",
            description="Genera un gráfico a partir de datos CSV",
            argument_types={
                "csv_path": "str",
                "chart_type": "str",
                "output_path": "str"
            }
        )
        def generate_chart(csv_path: str, chart_type: str, output_path: str) -> str:
            """
            Generate a chart from CSV data.

            Args:
                csv_path: Path to CSV file
                chart_type: Type of chart (bar, line, scatter, pie)
                output_path: Path to save the chart image

            Returns:
                Status message
            """
            try:
                # pylint: disable=import-outside-toplevel
                import pandas as pd
                import matplotlib.pyplot as plt

                if not os.path.exists(csv_path):
                    return f"Error: Archivo '{csv_path}' no existe"

                df = pd.read_csv(csv_path)

                # Create output directory
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                # Ensure output has image extension
                if not output_path.endswith(('.png', '.jpg', '.jpeg', '.svg')):
                    output_path += '.png'

                plt.figure(figsize=(10, 6))

                # Generate chart based on type
                if chart_type.lower() == 'bar':
                    df.plot(kind='bar', ax=plt.gca())
                elif chart_type.lower() == 'line':
                    df.plot(kind='line', ax=plt.gca())
                elif chart_type.lower() == 'scatter' and len(df.columns) >= 2:
                    plt.scatter(df.iloc[:, 0], df.iloc[:, 1])
                    plt.xlabel(df.columns[0])
                    plt.ylabel(df.columns[1])
                elif chart_type.lower() == 'pie' and len(df.columns) >= 1:
                    df.iloc[:, 0].value_counts().plot(kind='pie', autopct='%1.1f%%')
                else:
                    msg = f"Error: Tipo de gráfico '{chart_type}' no soportado"
                    return f"{msg} o datos insuficientes"

                plt.title(f'{chart_type.capitalize()} Chart')
                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()

                return f"Gráfico generado: {output_path}"

            except ImportError:
                return "Error: matplotlib no está instalado. Ejecutá: pip install matplotlib"
            except Exception as e:  # pylint: disable=broad-except
                return f"Error al generar gráfico: {str(e)}"

        @register_function(
            name="detect_outliers",
            description="Detecta valores atípicos en una columna usando método IQR",
            argument_types={
                "csv_path": "str",
                "column": "str"
            }
        )
        def detect_outliers(csv_path: str, column: str) -> str:
            """
            Detect outliers in a column using IQR method.

            Args:
                csv_path: Path to CSV file
                column: Column name to analyze

            Returns:
                Report of outliers found
            """
            try:
                # pylint: disable=import-outside-toplevel
                import pandas as pd

                if not os.path.exists(csv_path):
                    return f"Error: Archivo '{csv_path}' no existe"

                df = pd.read_csv(csv_path)

                if column not in df.columns:
                    msg = f"Error: Columna '{column}' no existe."
                    return f"{msg} Columnas disponibles: {list(df.columns)}"

                # Calculate IQR
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1

                # Define outlier bounds
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                # Find outliers
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]

                if len(outliers) == 0:
                    return f"No se detectaron valores atípicos en '{column}'"

                result = (
                    f"Detectados {len(outliers)} valores atípicos en '{column}':\n"
                    f"Rango normal: [{lower_bound:.2f}, {upper_bound:.2f}]\n\n"
                    f"Valores atípicos:\n"
                )

                for idx, row in outliers.head(10).iterrows():
                    result += f"  Fila {idx}: {row[column]}\n"

                if len(outliers) > 10:
                    result += f"\n(Mostrando primeros 10 de {len(outliers)} valores atípicos)"

                return result

            except Exception as e:  # pylint: disable=broad-except
                return f"Error al detectar outliers: {str(e)}"

        @register_function(
            name="correlation_matrix",
            description="Genera una matriz de correlación de todas las columnas numéricas",
            argument_types={
                "csv_path": "str",
                "output_path": "str"
            }
        )
        def correlation_matrix(csv_path: str, output_path: str) -> str:
            """
            Generate a correlation matrix heatmap.

            Args:
                csv_path: Path to CSV file
                output_path: Path to save the correlation matrix

            Returns:
                Status message with correlation info
            """
            try:
                # pylint: disable=import-outside-toplevel
                import pandas as pd

                if not os.path.exists(csv_path):
                    return f"Error: Archivo '{csv_path}' no existe"

                df = pd.read_csv(csv_path)

                # Select only numeric columns
                numeric_df = df.select_dtypes(include=['number'])

                if numeric_df.empty:
                    return "Error: No hay columnas numéricas en el dataset"

                # Calculate correlation matrix
                corr_matrix = numeric_df.corr()

                # Create output directory
                output_dir = os.path.dirname(output_path)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                # Save as JSON
                if not output_path.endswith('.json'):
                    json_path = output_path + '_correlation.json'
                else:
                    json_path = output_path

                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(corr_matrix.to_dict(), f, indent=2)

                # Try to create heatmap if seaborn is available
                try:
                    import matplotlib.pyplot as plt
                    import seaborn as sns

                    plt.figure(figsize=(10, 8))
                    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                               square=True, linewidths=1, cbar_kws={"shrink": 0.8})
                    plt.title('Correlation Matrix')
                    plt.tight_layout()

                    img_path = output_path.replace('.json', '.png')
                    if not img_path.endswith('.png'):
                        img_path += '_correlation.png'

                    plt.savefig(img_path, dpi=300, bbox_inches='tight')
                    plt.close()

                    return (
                        f"Matriz de correlación generada:\n"
                        f"  JSON: {json_path}\n"
                        f"  Imagen: {img_path}\n"
                        f"Columnas analizadas: {list(numeric_df.columns)}"
                    )

                except ImportError:
                    return (
                        f"Matriz de correlación generada: {json_path}\n"
                        f"Columnas analizadas: {list(numeric_df.columns)}\n"
                        f"(Instalá matplotlib y seaborn para generar visualización)"
                    )

            except Exception as e:  # pylint: disable=broad-except
                return f"Error al generar matriz de correlación: {str(e)}"
