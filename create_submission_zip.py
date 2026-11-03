"""
Creates the final submission zip file named 12404505.zip
Excludes virtual environments, git metadata, and temporary cache files.
"""

import os
import zipfile

def create_zip(output_zip="12404505.zip"):
    ignore_dirs = {".venv", ".git", "__pycache__", ".ipynb_checkpoints"}
    ignore_files = {"12404505.zip", ".DS_Store", "Thumbs.db"}

    root_dir = os.path.abspath(".")
    total_files = 0

    print(f"Packaging project into {output_zip}...")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in place to prune ignored folders
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file in ignore_files or file.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                zipf.write(full_path, rel_path)
                total_files += 1

    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"Successfully created {output_zip} ({zip_size_mb:.2f} MB, {total_files} files packaged).")

if __name__ == "__main__":
    create_zip()
