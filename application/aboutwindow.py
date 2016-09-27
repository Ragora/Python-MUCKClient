"""
    aboutwindow.py

    Python programming for the about window.
"""

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk

class AboutWindow(object):
    window = None

    def __init__(self, application):
        builder = Gtk.Builder()
        builder.add_from_file("ui/About.glade")

        self.window = builder.get_object("AboutWindow")

        builder.connect_signals(self)
        self.window.set_visible(True)
        response = self.window.run()

    def user_response(self, element, event):
        """
            Signal that's called when the user submits a response to the about dialog.
        """

        self.window.destroy()
