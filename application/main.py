"""
    main.py
"""

import re
import os
import sys
import cgi
import json

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass

from gi.repository import Gtk, GLib
import glib
import pango

import ansi
from mainwindow import MainWindow
import markup

class Application(object):
    """
        The primary application state object.
    """

    main_window = None
    """
        The main window of the application.
    """

    aliases = None
    """
        Configurable data that should consist of only serializable data.
    """

    alias_states = None
    """
        Runtime relevant state data about each alias.
    """

    url_pattern = re.compile("https?\://([A-z]|\.|[0-9]|-|/)+")
    """
        A regular expression representing any URL. This is used to format URL's in our text output to be
        actual clickable links.
    """

    selected_alias = None
    """
        Thw name of the currently selected alias.
    """

    def main(self):
        """
            Main entry point of the application. This is called to perform initialization of the program
            state and start up the GUI.
        """

        self.config = {"aliases": {}, "triggers": {}, "ansi": {}}
        self.alias_states = {}
        GLib.idle_add(self.update)

        self.main_window = MainWindow(self)

        # Before we finally launch, load the config
        try:
            with open("config.txt", "r") as handle:
                buffer = handle.read()

                config = json.loads(buffer)

                for alias_name in config["aliases"]:
                    self.add_alias(alias_name, config["aliases"][alias_name]["address"], config["aliases"][alias_name]["password"])

                self.config = config
        except OSError:
            print("Failed to load config.")

        Gtk.main()

    def update(self):
        """
            Called to process our ongoing connections, receiving and processing any lines as necessary.
        """

        modified_current_alias = False

        for alias in self.config["aliases"]:
            if alias != "No Aliases." and self.alias_states[alias]["connection"] is not None:
                if self.alias_states[alias]["connection"].is_connected():
                    new_lines = self.alias_states[alias]["connection"].update()

                    # Once we're done updating the buffer, run formatters
                    if new_lines is not None and len(new_lines) != 0:
                        # Write to the logfile if enabled
                        if self.alias_states[alias]["logfile"] is not None:
                            """
                                This is an inefficient logging mechanism but given the nature of MUCK, this performance impact is negligable and allows
                                for log changes to appear in realtime as well as adding safety against crashes.
                            """
                            with open(self.alias_states[alias]["logfile"], "a") as handle:
                                handle.write("\n".join(new_lines))

                        output_lines = []
                        for index, line in enumerate(new_lines):
                            # Escape incoming data so we don't break the markup
                            old_line = cgi.escape(line)
                            line = str(old_line)

                            # Perform ANSI formatting
                            ansi_formatter = ansi.Formatter()
                            line = ansi_formatter.process_formatting(line)

                            for trigger_name in self.config["triggers"]:
                                trigger_data = self.config["triggers"][trigger_name]

                                try:
                                    trigger_text = trigger_data["text"]

                                    trigger_foreground = None
                                    trigger_background = None
                                    trigger_bold = False
                                    trigger_italic = False
                                    trigger_strikethrough = False
                                    trigger_underline = False

                                    if "foreground" in trigger_data:
                                        trigger_foreground = trigger_data["foreground"]

                                    if "background" in trigger_data:
                                        trigger_background = trigger_data["background"]

                                    if "bold" in trigger_data:
                                        trigger_bold = trigger_data["bold"]

                                    if "italic" in trigger_data:
                                        trigger_italic = trigger_data["italic"]

                                    if "strikethrough" in trigger_data:
                                        trigger_strikethrough = trigger_data["strikethrough"]

                                    if "underline" in trigger_data:
                                        trigger_underline = trigger_data["underline"]

                                    generator = markup.Markup()
                                    generator.foreground = trigger_foreground
                                    generator.backgrund = trigger_background
                                    generator.text = trigger_text
                                    generator.bold = trigger_bold
                                    generator.italic = trigger_italic
                                    generator.underline = trigger_underline
                                    generator.strikethrough = trigger_strikethrough
                                    generator.underline = trigger_underline

                                    line = line.replace(trigger_text, generator.generate_markup())
                                except KeyError as e:
                                    print("An internal error has occurred. Failed to run trigger '%s': %s" % (trigger_name, e))

                            # FIXME: Can we validate with the damn URL's?
                            try:
                                pango.parse_markup(line)
                            except glib.GError as e:
                                print("An internal error has occurred. Failed to validate markup '%s': %s" % (line, e))
                                line = old_line

                            # Replace things that look like URL's with the href tags
                            # FIXME: Try things that look like URL's, ie: www.*
                            for match in re.finditer(self.url_pattern, line):
                                match_text = match.group(0)
                                generator = markup.Markup()
                                generator.text = match_text
                                generator.link = match_text

                                line = line.replace(match_text, generator.generate_markup())

                            output_lines.append(line)
                            
                        # Feed the modified data back to the connection
                        self.alias_states[alias]["connection"].acknowledge_lines(output_lines)

                        if self.selected_alias == alias:
                            modified_current_alias = True
                else:
                    self.alias_states[alias]["icon"].set_from_stock("gtk-dialog-error", 2)

            # If there was new text data to display, attempt to scroll the window down
            if modified_current_alias is True:
                # FIXME: Auto scroll to the bottom
                self.main_window.label_output.set_markup(self.alias_states[self.selected_alias]["connection"].buffer)
                vertical = self.main_window.scroll_window.get_vadjustment()

                vertical.set_value(vertical.get_upper() - vertical.get_page_size())

        return True

    def add_alias(self, name, address, password):
        self.alias_states[name] = {
            "connection": None,
            "icon": self.main_window.add_alias(name),
            "logfile": None,
        }

if __name__ == "__main__":
    Application().main()
