from pathlib import Path
import os
import sys

# Set environment variables to use clang-cl
os.environ["CC"] = "clang-cl"
os.environ["CXX"] = "clang-cl"
os.environ["DISTUTILS_USE_SDK"] = "1"  # Use SDK compiler on Windows

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

CYTHONIZE = os.getenv("CYTHONIZE", False)
if CYTHONIZE:
    from Cython.Build import cythonize


class ClangBuildExt(build_ext):
    """Custom build_ext command to force clang-cl usage for both compiler and linker"""

    def build_extension(self, ext):
        # Override the compiler to use clang-cl
        if self.compiler.compiler_type == "msvc":
            # Store original spawn method
            original_spawn = self.compiler.spawn

            def clang_spawn(cmd):
                # Replace cl.exe with clang-cl (compiler)
                if cmd and (cmd[0] == "cl.exe" or cmd[0] == "cl"):
                    cmd[0] = "clang-cl"
                    print(f"Using clang-cl compiler: {' '.join(cmd)}")
                # Replace link.exe with clang-cl (linker)
                elif cmd and (cmd[0] == "link.exe" or cmd[0] == "link"):
                    # Use clang-cl for linking with appropriate flags
                    cmd[0] = "lld-link.exe"
                    # Convert MSVC linker flags to clang-cl compatible ones
                    print(f"Using clang-cl linker: {' '.join(cmd)}")
                return original_spawn(cmd)

            # Replace spawn method
            self.compiler.spawn = clang_spawn

            # Override compiler and linker executables
            if hasattr(self.compiler, "cc"):
                self.compiler.cc = "clang-cl"
            if hasattr(self.compiler, "linker_so"):
                self.compiler.linker_so = "clang-cl"
            if hasattr(self.compiler, "linker"):
                self.compiler.linker = "clang-cl"

        # Call parent build_extension
        super().build_extension(ext)


package_dir = "kataglyphispythonpackage"
version = Path("VERSION.txt").read_text().strip()


def list_py_files(package_dir):
    """List all Python files in the package, excluding __init__.py and special files"""
    py_files = []
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                py_files.append(os.path.join(root, file))
    return py_files


# Get all Python files
py_files = list_py_files(package_dir)

# Define the extensions
extensions = []
if CYTHONIZE:
    extra_compile_args = []
    extra_link_args = []

    if sys.platform == "win32":
        # clang-cl compatible MSVC-style flags
        extra_compile_args = [
            "/O2",  # Optimize for speed
            "/MD",  # Use multithreaded DLL runtime
            # Remove /GL as it might not work well with clang-cl linker
        ]
        extra_link_args = [
            "/OPT:REF",  # Remove unreferenced functions
            "/OPT:ICF",  # Identical COMDAT folding
            "/LTCG:OFF",  # Disable link-time code generation for clang-cl
        ]
    else:
        # GCC/Clang flags for Unix-like systems
        extra_compile_args = [
            "-O3",
            "-flto",
            "-fvisibility=hidden",
        ]
        extra_link_args = ["-flto"]

    # Create extensions - avoid naming conflicts with original modules
    extensions = [
        Extension(
            py_file.replace(os.path.sep, ".")[:-3] + "_compiled",  # Add suffix
            [py_file],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
        for py_file in py_files
    ]

# Setup configuration
setup_kwargs = {
    "name": package_dir,
    "version": version,
    "zip_safe": False,
}

if CYTHONIZE:
    # Cythonized build
    setup_kwargs.update(
        {
            "ext_modules": cythonize(
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
            "cmdclass": {"build_ext": ClangBuildExt},  # Use custom build command
            "package_data": {"": ["*.c", "*.so", "*.pyd"]},
        }
    )
else:
    # Regular Python package
    setup_kwargs.update(
        {
            "packages": [package_dir],
            "include_package_data": True,
        }
    )

setup(**setup_kwargs)
