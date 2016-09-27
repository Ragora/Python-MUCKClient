"""
    savetextbufferwindow.py

    Python programming implementing the save text buffer window.
"""

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk

class SaveTextBufferWindow(object):
    """
        Window for saving the log buffer of the current alias.
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
        try:
            with open(self.window.get_filename(), "w") as handle:
                handle.write(self.application.main_window.label_output.get_text())
        except IOError as e:
            # FIXME: Throw an error window on this
            pass

        self.window.destroy()
