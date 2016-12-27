import sys
from Tkinter import Tk
ctext = ""
for f in sys.argv[1:]:
	ctext+=f+" "
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(ctext)
r.destroy()