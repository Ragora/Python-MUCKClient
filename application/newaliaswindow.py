"""
    newaliaswindow.py


"""

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk

class NewAliasWindow(object):
    """
        Window for creating new aliases in the application.
    """

    def __init__(self, application):
        builder = Gtk.Builder()
        builder.add_from_file("ui/NewAlias.glade")

        self.window = builder.get_object("NewAliasWindow")

        self.entry_server = builder.get_object("EntryServer")
        self.entry_alias = builder.get_object("EntryAlias")
        self.entry_authenticate = builder.get_object("EntryAuthenticate")
        self.application = application

        builder.connect_signals(self)
        self.window.set_visible(True)

    def create_new_alias(self, element):
        server = self.entry_server.get_text()
        alias = self.entry_alias.get_text()
        authenticate = self.entry_authenticate.get_text()

        self.application.add_alias(alias, server, None)
        self.window.destroy()

    def cancel(self, element):
        self.window.destroy()
