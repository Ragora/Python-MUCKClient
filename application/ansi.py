"""
    ansi.py

    Experimental ANSI formatting engine.
"""

import re

class Formatter(object):
    """
        Experimental ANSI formatter object.
    """

    default_coloring = {
        "red": "red",
        "blue": "blue",
        "green": "green",
        "cyan": "cyan",
        "magenta": "magenta",
        "white": "white",
    }
    """
        The default coloring data to use in this formatter.
    """

    def _handle_reset(format_state):
        """
            Handler for ANSI code 0.
        """

        format_state["background"] = None
        format_state["foreground"] = None
        format_state["strikethrough"] = False
        format_state["underline"] = False
        format_state["italics"] = False
        format_state["bold"] = False

    def _handle_strikethrough_on(format_state):
        """
            Handler for ANSI code 9.
        """

        format_state["strikethrough"] = True

    def _handle_strikethrough_off(format_state):
        """
            Handler for ANSI code 29.
        """

        format_state["strikethrough"] = False

    def _handle_inverse_off(format_state):
        """
            Handler for ANSI code 27.
        """

        format_state["inverse"] = False

    def _handle_inverse_on(format_state):
        """
            Handler for ANSI code 7.
        """

        format_state["inverse"] = True

    def _handle_bold_on(format_state):
        """
            Handler for ANSI code 1.
        """

        format_state["bold"] = True

    def _handle_italics_on(format_state):
        """
            Handler for ANSI code 3.
        """

        format_state["italics"] = True

    def _handle_underline_on(format_state):
        """
            Handler for ANSI code 4.
        """

        format_state["underline"] = True

    def _handle_bold_off(format_state):
        """
            Handler for ANSI code 22.
        """

        format_state["bold"] = False

    def _handle_italics_off(format_state):
        """
            Handler for ANSI code 23.
        """

        format_state["italics"] = False

    def _handle_underline_off(format_state):
        """
            Handler for ANSI code 24.
        """

        format_state["underline"] = False

    def _handle_underline_off(format_state):
        """
            Handler for ANSI code 24.
        """

        format_state["underline"] = False

    def _handle_foreground_black(format_state):
        """
            Handler for ANSI code 30.
        """

        format_state["foreground"] = "black"

    def _handle_foreground_red(format_state):
        """
            Handler for ANSI code 31.
        """

        format_state["foreground"] = "red"

    def _handle_foreground_green(format_state):
        """
            Handler for ANSI code 32.
        """

        format_state["foreground"] = "green"

    def _handle_foreground_yellow(format_state):
        """
            Handler for ANSI code 33.
        """

        format_state["foreground"] = "yellow"

    def _handle_foreground_blue(format_state):
        """
            Handler for ANSI code 34.
        """

        format_state["foreground"] = "blue"

    def _handle_foreground_magenta(format_state):
        """
            Handler for ANSI code 35.
        """

        format_state["foreground"] = "magenta"

    def _handle_foreground_cyan(format_state):
        """
            Handler for ANSI code 36.
        """

        format_state["foreground"] = "cyan"

    def _handle_foreground_white(format_state):
        """
            Handler for ANSI code 37.
        """

        format_state["foreground"] = "white"

    def _handle_foreground_reset(format_state):
        """
            Handler for ANSI code 39.
        """

        format_state["foreground"] = None

    def _handle_background_black(format_state):
        """
            Handler for ANSI code 40.
        """

        format_state["background"] = "black"

    def _handle_background_red(format_state):
        """
            Handler for ANSI code 41.
        """

        format_state["background"] = "red"

    def _handle_background_green(format_state):
        """
            Handler for ANSI code 42.
        """

        format_state["background"] = "green"

    def _handle_background_yellow(format_state):
        """
            Handler for ANSI code 43.
        """

        format_state["background"] = "yellow"

    def _handle_background_blue(format_state):
        """
            Handler for ANSI code 44.
        """

        format_state["background"] = "blue"

    def _handle_background_magenta(format_state):
        """
            Handler for ANSI code 45.
        """

        format_state["background"] = "magenta"

    def _handle_background_cyan(format_state):
        """
            Handler for ANSI code 46.
        """

        format_state["background"] = "cyan"

    def _handle_background_white(format_state):
        """
            Handler for ANSI code 47.
        """

        format_state["background"] = "white"

    def _handle_background_reset(format_state):
        """
            Handler for ANSI code 49.
        """

        format_state["background"] = None

    # All of our ansi handling buddies
    ansi_handlers = {
        # Reset everything
        0: _handle_reset,
        1: _handle_bold_on,
        3: _handle_italics_on,
        4: _handle_underline_on,
        7: _handle_inverse_on,
        9: _handle_strikethrough_on,
        22: _handle_bold_off,
        23: _handle_italics_off,
        24: _handle_underline_off,
        27: _handle_inverse_off,
        29: _handle_strikethrough_off,
        30: _handle_foreground_black,
        31: _handle_foreground_red,
        32: _handle_foreground_green,
        33: _handle_foreground_yellow,
        34: _handle_foreground_blue,
        35: _handle_foreground_magenta,
        36: _handle_foreground_cyan,
        37: _handle_foreground_white,
        39: _handle_foreground_reset,
        40: _handle_background_black,
        41: _handle_background_red,
        42: _handle_background_green,
        43: _handle_background_yellow,
        44: _handle_background_blue,
        45: _handle_background_magenta,
        46: _handle_background_cyan,
        47: _handle_background_white,
        49: _handle_background_reset,
    }

    def process_formatting(self, input_text, coloring=None):
        # We keep track of the format state on a per segment basis
        current_format = {
            # Current background color
            "background": None,
            # Current foreground color
            "foreground": None,

            # Strikethrough enabled?
            "strikethrough": False,
            # Underline enabled?
            "underline": False,
            # Italics enabled?
            "italics": False,
            # Bold enabled?
            "bold": False,

            # Inverse enabled?
            "inverse": False,
        }

        # A list of in-order tuples containing the raw text and the format state
        segments = []
        current_index = 0

        # Use the defaults if not specified.
        if coloring is None:
            coloring = self.default_coloring

        # We process the input text looking for all sequences that look like this:
        ansi_regex = re.compile("\x1b\\[([0-9]+\\;)?[0-9]+m")
        beginning_regex = re.compile("\x1b\\[([0-9]+\\;)?")

        for match in re.finditer(ansi_regex, input_text):
            start_index = match.start()
            end_index = match.end()

            # When we find a good match, we only want the numeric code
            # FIXME: What does the ##; mean?
            ansi_numeric = match.group(0).rstrip("m")
            ansi_numeric = int(re.sub(beginning_regex, "", ansi_numeric))

            # When we have a valid ANSI sequence, we push back the old format state and buffer
            if ansi_numeric in self.ansi_handlers:
                # Grab all of the text affected by the CURRENT formatter and stow it away
                old_text = input_text[current_index:start_index]
                current_index = end_index

                segments.append((old_text, dict(current_format)))

                # The handler writes directly to this current format data
                handler = self.ansi_handlers[ansi_numeric]

                if handler is not None:
                    handler(current_format)
                else:
                    print("*** ANSI warning: Found known ANSI format code %u, but is it not implemented." % ansi_numeric)
            else:
                print("*** ANSI warning: Found unknown ANSI format code %u." % ansi_numeric)

        # Once we hit the end, we grab any remaining text and create a formatter entry for it
        segments.append((input_text[current_index:], current_format))

        # Foreach segment, build a pango text attribute block
        result = ""
        for text_buffer, format_data in segments:
            # FIXME: Build this more programmatically
            if format_data["bold"]:
                text_buffer = "<b>%s</b>" % text_buffer

            if format_data["italics"]:
                text_buffer = "<i>%s</i>" % text_buffer

            if format_data["strikethrough"]:
                text_buffer = "<s>%s</s>" % text_buffer

            if format_data["underline"]:
                text_buffer = "<u>%s</u>" % text_buffer

            foreground_color = format_data["foreground"]
            background_color = format_data["background"]

            # Swap our colors if necessary
            if format_data["inverse"]:
                temporary = foreground_color
                foreground_color = background_color
                background_color = temporary

            # Add a span block if we have colors
            span_body = ""
            if foreground_color is not None:
                span_body += "foreground=\"%s\"" % foreground_color

            if background_color is not None:
                span_body += "background=\"%s\"" % background_color

            if span_body != "":
                text_buffer = "<span %s>%s</span>" % (span_body, text_buffer)

            result += text_buffer

        return result
