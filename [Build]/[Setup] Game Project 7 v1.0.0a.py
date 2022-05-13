import cx_Freeze
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

executables = [cx_Freeze.Executable("[Game Project 7] Adventurers of Elrualia v1.0.0a.py")]

cx_Freeze.setup(
    name="Adventurers of Elrualia",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["Data"]}},
    executables=executables,
    version="1.0.0"
)
