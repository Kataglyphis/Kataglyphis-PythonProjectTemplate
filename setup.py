from pathlib import Path
from setuptools import setup, Extension

import os
import sys

CYTHONIZE = os.getenv("CYTHONIZE", False)
if CYTHONIZE:
    from Cython.Build import cythonize


package_dir = "kataglyphispythonpackage"

version = Path("VERSION.txt").read_text().strip()


# List of all Python files in your package
def list_py_files(package_dir):
    py_files = []
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files


# Replace 'your_package' with the actual package directory name
py_files = list_py_files(package_dir)

# Define the extensions
extensions = []
if CYTHONIZE:
    extra_compile_args = []
    extra_link_args = []
    if sys.platform == "win32":
        # Use MSVC-specific optimization flag(s) on Windows
        extra_compile_args = ["/O2"]  # Optimize code
        extra_link_args = []
    else:
        # Use GCC/Clang flags on Unix-like systems
        extra_compile_args = [
            "-O3",
            "-s",
            "-flto",
            "-s",
            "-fvisibility=hidden",
        ]  # Optimize and strip symbols
        extra_link_args = []
    extensions = [
        Extension(
            py_file.replace(os.path.sep, ".")[:-3],
            [py_file],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
        for py_file in py_files
    ]

if CYTHONIZE:
    # Setup script
    setup(
        name=package_dir,
        version=version,
        packages=[],
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "emit_code_comments": False,
                "linetrace": False,
                "embedsignature": False,
                "binding": False,
                "profile": False,
                "annotation_typing": False,
                "initializedcheck": False,
                "warn.undeclared": False,
                "infer_types": False,
            },
        ),
        package_data={"": ["*.c", "*.so", "*.pyd"]},
        zip_safe=False,
    )

else:
    # Setup script
    setup(
        name=package_dir,
        version=version,
        packages=[package_dir],
        include_package_data=True,
        zip_safe=False,
    )
