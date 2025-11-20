# dsl_spec.py
"""
Especificación formal del DSL de Orion v0.1
"""

ALLOWED_SOURCES = {"csv", "json", "parquet"}
ALLOWED_OUTPUTS = {"csv", "json", "parquet"}

ALLOWED_OPERATIONS = {
    "drop_na",
    "convert_type",
    "filter",
    "rename_column",
    "select_columns",
    "aggregate",
}

TYPE_CASTS = {"int", "float", "str", "bool"}
