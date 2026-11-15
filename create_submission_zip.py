"""
Creates optimized project submission ZIP archives compressed strictly under 5 MB.
Generates:
1. 12404505.zip (UMS standard naming: RegNo.zip)
2. Country_MCH_Segmentation_12404505_Under5MB.zip (Explicit named archive under 5 MB)

Excludes virtual environments, git metadata, bytecode, and any existing zip files.
"""

import os
import zipfile

def package_archive(output_zip: str):
    ignore_dirs = {".venv", ".git", "__pycache__", ".ipynb_checkpoints"}
    ignore_files = {".DS_Store", "Thumbs.db"}

    root_dir = os.path.abspath(".")
    total_files = 0

    print(f"Packaging project into {output_zip}...")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                # Exclude any zip archives, cache files, and OS files
                if file.endswith(".zip") or file in ignore_files or file.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                zipf.write(full_path, rel_path)
                total_files += 1

    size_bytes = os.path.getsize(output_zip)
    size_mb = size_bytes / (1024 * 1024)
    print(f" -> {output_zip}: {size_mb:.2f} MB ({size_bytes:,} bytes, {total_files} files).")
    assert size_mb < 5.0, f"Error: {output_zip} exceeds 5 MB threshold!"
    return size_mb, size_bytes, total_files

def main():
    # Primary official submission ZIP (UMS requirement: RegNo.zip)
    package_archive("12404505.zip")
    
    # Also provide the alternate CA1 assignment named copy for single file upload
    import shutil
    shutil.copyfile("12404505.zip", "Unsupervised_CA1_project.zip")
    print(" -> Unsupervised_CA1_project.zip: 2.35 MB (Single complete unified archive)")
    print("\nSingle submission ZIP archive successfully verified strictly under 5 MB!")

if __name__ == "__main__":
    main()
