# setup.py
import os
import sys
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

# Accept several truthy values for CYTHONIZE (so "True", True, "1", "true" all work)
CYTHONIZE_RAW = os.getenv("CYTHONIZE", "0")
CYTHONIZE = str(CYTHONIZE_RAW).strip().lower() in ("1", "true", "yes", "on")

if CYTHONIZE:
    from Cython.Build import cythonize

# Compiler-Umgebung nur plattformabhängig setzen
if sys.platform == "win32":
    os.environ["CC"] = "clang-cl"
    os.environ["CXX"] = "clang-cl"
    os.environ["DISTUTILS_USE_SDK"] = "1"
else:
    # Auf Unix NICHT clang-cl erzwingen
    os.environ.pop("DISTUTILS_USE_SDK", None)
    # Optional: clang bevorzugen, falls nicht explizit gesetzt
    os.environ.setdefault("CC", "clang")
    os.environ.setdefault("CXX", "clang")


class ClangBuildExt(build_ext):
    """Nur unter MSVC den Compiler/Linker auf clang-cl/lld-link umbiegen"""

    def build_extension(self, ext):
        if self.compiler.compiler_type == "msvc":
            original_spawn = self.compiler.spawn

            def clang_spawn(cmd):
                print("I am in clang_spawn")
                if not cmd:
                    return original_spawn(cmd)

                print(cmd[0])
                exe = cmd[0].strip('"')  # remove surrounding quotes if any
                name = os.path.basename(exe).lower()

                if name in {"cl.exe", "cl"}:
                    print("cmd[0] recognized as cl")
                    cmd[0] = "clang-cl"
                    print(f"Using clang-cl compiler: {' '.join(cmd)}")
                elif name in {"link.exe", "link"}:
                    print("cmd[0] recognized as link")
                    cmd[0] = "lld-link.exe"
                    print(f"Using lld-link linker: {' '.join(cmd)}")

                return original_spawn(cmd)

            self.compiler.spawn = clang_spawn

            if hasattr(self.compiler, "cc"):
                self.compiler.cc = "clang-cl"
            if hasattr(self.compiler, "linker_so"):
                self.compiler.linker_so = "clang-cl"
            if hasattr(self.compiler, "linker"):
                self.compiler.linker = "clang-cl"

        super().build_extension(ext)


package_dir = "kataglyphispythonpackage"
version = Path("VERSION.txt").read_text().strip()


def list_py_files(package_dir):
    py_files = []
    for root, dirs, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                py_files.append(os.path.join(root, file))
    return py_files


py_files = list_py_files(package_dir)

extensions = []
if CYTHONIZE:
    if sys.platform == "win32":
        extra_compile_args = ["/O2", "/MD"]
        extra_link_args = ["/OPT:REF", "/OPT:ICF", "/LTCG:OFF"]
    else:
        extra_compile_args = ["-O3", "-flto", "-fvisibility=hidden"]
        extra_link_args = ["-flto"]

    extensions = [
        Extension(
            py_file.replace(os.path.sep, ".")[:-3], # + "_compiled",
            [py_file],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        )
        for py_file in py_files
    ]

setup_kwargs = {"name": package_dir, "version": version, "zip_safe": False}

if CYTHONIZE:
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
            "cmdclass": {"build_ext": ClangBuildExt},
            "package_data": {"": ["*.c", "*.so", "*.pyd"]},
        }
    )
else:
    setup_kwargs.update({"packages": [package_dir], "include_package_data": True})

setup(**setup_kwargs)
