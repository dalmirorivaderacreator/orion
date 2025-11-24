"""
File Processor Plugin

Provides batch file operations, duplicate detection, and compression utilities.
"""

import os
import hashlib
import zipfile
from typing import List, Dict
from core.plugins.plugin_base import PluginBase
from registry import register_function


class FileProcessorPlugin(PluginBase):
    """
    Plugin for advanced file processing operations.

    Provides:
    - Batch file renaming with patterns
    - Duplicate file detection using hash comparison
    - File compression to ZIP archives
    """

    @property
    def name(self) -> str:
        return "file_processor"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Advanced file processing: batch rename, duplicate detection, compression"

    @property
    def author(self) -> str:
        return "ORION Team"

    def initialize(self) -> bool:
        """Initialize the file processor plugin."""
        return True

    def shutdown(self) -> None:
        """Clean up resources."""

    def register_functions(self) -> None:
        """Register file processing functions with ORION."""

        @register_function(
            name="batch_rename_files",
            description="Renombra archivos en lote usando patrones",
            argument_types={
                "directory": "str",
                "pattern": "str",
                "replacement": "str"
            }
        )
        def batch_rename_files(directory: str, pattern: str, replacement: str) -> str:
            """
            Rename multiple files matching a pattern.

            Args:
                directory: Directory containing files to rename
                pattern: Pattern to match in filenames
                replacement: Replacement string

            Returns:
                Status message with count of renamed files
            """
            if not os.path.exists(directory):
                return f"Error: Directorio '{directory}' no existe"

            renamed_count = 0
            files = os.listdir(directory)

            for filename in files:
                if pattern in filename:
                    old_path = os.path.join(directory, filename)
                    new_filename = filename.replace(pattern, replacement)
                    new_path = os.path.join(directory, new_filename)

                    # Only rename files, not directories
                    if os.path.isfile(old_path):
                        os.rename(old_path, new_path)
                        renamed_count += 1

            return f"Renombrados {renamed_count} archivos en '{directory}'"

        @register_function(
            name="find_duplicates",
            description="Encuentra archivos duplicados en un directorio usando hash MD5",
            argument_types={"directory": "str"}
        )
        def find_duplicates(directory: str) -> str:
            """
            Find duplicate files by comparing MD5 hashes.

            Args:
                directory: Directory to scan for duplicates

            Returns:
                Report of duplicate files found
            """
            if not os.path.exists(directory):
                return f"Error: Directorio '{directory}' no existe"

            hash_map: Dict[str, List[str]] = {}

            # Calculate hash for each file
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)

                    try:
                        file_hash = _calculate_file_hash(filepath)
                        if file_hash in hash_map:
                            hash_map[file_hash].append(filepath)
                        else:
                            hash_map[file_hash] = [filepath]
                    except (OSError, IOError):
                        continue

            # Find duplicates
            duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

            if not duplicates:
                return f"No se encontraron duplicados en '{directory}'"

            result = f"Encontrados {len(duplicates)} grupos de archivos duplicados:\n"
            for file_hash, paths in duplicates.items():
                result += f"\nHash {file_hash[:8]}...:\n"
                for path in paths:
                    result += f"  - {path}\n"

            return result

        @register_function(
            name="compress_files",
            description="Comprime archivos en un archivo ZIP",
            argument_types={
                "directory": "str",
                "output_archive": "str"
            }
        )
        def compress_files(directory: str, output_archive: str) -> str:
            """
            Compress files into a ZIP archive.

            Args:
                directory: Directory containing files to compress
                output_archive: Path for the output ZIP file

            Returns:
                Status message with archive details
            """
            if not os.path.exists(directory):
                return f"Error: Directorio '{directory}' no existe"

            # Ensure output has .zip extension
            if not output_archive.endswith('.zip'):
                output_archive += '.zip'

            # Create output directory if needed
            output_dir = os.path.dirname(output_archive)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            file_count = 0
            total_size = 0

            with zipfile.ZipFile(output_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(directory):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        arcname = os.path.relpath(filepath, directory)
                        zipf.write(filepath, arcname)
                        file_count += 1
                        total_size += os.path.getsize(filepath)

            archive_size = os.path.getsize(output_archive)
            compression_ratio = (1 - archive_size / total_size) * 100 if total_size > 0 else 0

            return (
                f"Archivo creado: {output_archive}\n"
                f"Archivos comprimidos: {file_count}\n"
                f"Tamaño original: {total_size:,} bytes\n"
                f"Tamaño comprimido: {archive_size:,} bytes\n"
                f"Compresión: {compression_ratio:.1f}%"
            )


def _calculate_file_hash(filepath: str) -> str:
    """
    Calculate MD5 hash of a file.

    Args:
        filepath: Path to the file

    Returns:
        MD5 hash as hexadecimal string
    """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
