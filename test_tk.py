import os
import sys

out = open("C:\\AAAAA_many\\app\\u_URLblock\\test_out.txt", "w")

try:
    out.write(f"sys.executable: {sys.executable}\n")
    tcl_lib = os.path.join(os.path.dirname(sys.executable), "tcl", "tcl8.6")
    tk_lib = os.path.join(os.path.dirname(sys.executable), "tcl", "tk8.6")
    out.write(f"tcl_lib: {tcl_lib} exists: {os.path.exists(tcl_lib)}\n")
    if os.path.exists(tcl_lib):
        os.environ["TCL_LIBRARY"] = tcl_lib
    if os.path.exists(tk_lib):
        os.environ["TK_LIBRARY"] = tk_lib
    out.write(f"os.environ['TCL_LIBRARY']: {os.environ.get('TCL_LIBRARY')}\n")

    import tkinter
    tkinter.Tk()
    out.write("Tkinter initialized successfully!\n")
except Exception as e:
    out.write(f"Error: {e}\n")
finally:
    out.close()
