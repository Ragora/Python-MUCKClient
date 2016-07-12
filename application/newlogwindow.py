"""
    newlogwindow.py


"""

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk

class NewLogWindow(object):
    """
        Window for creating new logs in the application.
    """

    def __init__(self, application, alias):
        builder = Gtk.Builder()
        builder.add_from_file("ui/NewLog.glade")

        self.window = builder.get_object("NewLogWindow")

        self.application = application
        self.alias = alias

        builder.connect_signals(self)
        self.window.set_visible(True)

    def cancel(self, element):
        self.application.main_window.logging_enable.set_active(False)
        self.window.destroy()

    def save(self, element):
        self.application.alias_states[self.alias]["logfile"] = self.window.get_filename()
        self.window.destroy()
