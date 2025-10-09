# setup.py
import os
import sys
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
# --- add near the bottom of your setup.py (before setup(**setup_kwargs)) ---
import zipfile
import hashlib
import base64
import tempfile
import shutil

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
except Exception:
    _bdist_wheel = None
    
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
    # merge cmdclass
    cmds = {"build_ext": ClangBuildExt}
    if _bdist_wheel is not None:
        cmds["bdist_wheel"] = StripWheel
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
            "cmdclass": cmds, # {"build_ext": ClangBuildExt},
            "package_data": {"": ["*.c", "*.so", "*.pyd"]},
        }
    )
else:
    setup_kwargs.update({"packages": [package_dir], "include_package_data": True})

class StripWheel(_bdist_wheel if _bdist_wheel is not None else object):
    """
    Build the wheel then rewrite it to exclude source files (.py, .pyc, .c, etc.)
    and rebuild the .dist-info/RECORD so the wheel remains valid.
    """
    exclude_suffixes = (".py", ".pyc", ".pyo", ".c", ".h", ".pxd")

    def run(self):
        # Run the normal wheel build if available
        if _bdist_wheel is not None:
            super().run()
        else:
            # fallback: let setuptools create dist/ wheel via other commands
            raise RuntimeError("wheel bdist_wheel not available; install 'wheel' package")

        dist_dir = getattr(self, "dist_dir", "dist")
        # find the newly created wheel(s)
        for fname in os.listdir(dist_dir):
            if not fname.endswith(".whl"):
                continue
            path = os.path.join(dist_dir, fname)
            self._strip_wheel(path)

    def _strip_wheel(self, wheel_path):
        # read original wheel and write new temporary wheel
        tmpfd, tmpname = tempfile.mkstemp(suffix=".whl")
        os.close(tmpfd)

        with zipfile.ZipFile(wheel_path, "r") as zin:
            namelist = zin.namelist()
            # find dist-info directory name (e.g. mypkg-1.0.dist-info/RECORD)
            dist_info_record = next((n for n in namelist if n.endswith(".dist-info/RECORD")), None)
            if dist_info_record is None:
                raise RuntimeError("Could not locate .dist-info/RECORD inside wheel")

            dist_info_dir = dist_info_record.rsplit("/", 1)[0] + "/"

            # Collect files we will keep and compute their hashes & sizes
            kept = []
            for name in namelist:
                if any(name.endswith(suf) for suf in self.exclude_suffixes):
                    # drop excluded suffixes
                    continue
                # also skip RECORD itself — we'll regenerate it
                if name == dist_info_record:
                    continue
                # keep everything else
                kept.append(name)

            # Write kept files into new wheel and compute RECORD entries
            record_lines = []
            with zipfile.ZipFile(tmpname, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for name in kept:
                    data = zin.read(name)
                    zout.writestr(name, data)
                    # compute sha256 base64 (urlsafe, no padding)
                    h = hashlib.sha256(data).digest()
                    b64 = base64.urlsafe_b64encode(h).rstrip(b"=").decode("ascii")
                    size = str(len(data))
                    record_lines.append(f"{name},sha256={b64},{size}")

                # Add the new RECORD file with entries computed above.
                # RECORD itself has an empty hash and size.
                record_content = "\n".join(record_lines + [f"{dist_info_dir}RECORD,,"]).encode("utf-8")
                zout.writestr(dist_info_dir + "RECORD", record_content)

        # replace original wheel with the stripped one
        shutil.move(tmpname, wheel_path)
        print(f"Stripped wheel written: {wheel_path}")

setup(**setup_kwargs)
