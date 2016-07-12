"""
    aboutwindow.py

    
"""

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk

class AboutWindow(object):
    def __init__(self, application):
        builder = Gtk.Builder()
        builder.add_from_file("ui/About.glade")

        window = builder.get_object("AboutWindow")

        builder.connect_signals(self)
        window.set_visible(True)
