import cx_Freeze
import sys
import os

AUTHOR = "Kazuto Mori"
base = None

os.environ["TCL_LIBRARY"] = "E:/Programming/Python/Python35/tcl/tcl8.6"
os.environ["TK_LIBRARY"] = "E:/Programming/Python\Python35/tcl/tk8.6"
if sys.platform == "win32":
	base = "Win32GUI"

exe = cx_Freeze.Executable(
	script="breakout.py",
	base=base,
	icon="./image/icon.ico"
	)

cx_Freeze.setup(
	name = "BreakOut",
	options = {"build_exe":{"packages":["pygame"],"include_files":["image/","sound/","__init__.py"]}},
	version = "1.0",
	author = AUTHOR,
	description = "No description",
	executables = [exe]
)
