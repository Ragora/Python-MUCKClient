"""
    markup.py

    Markup generator.
"""

class Markup(object):
    text = None
    """
        The display text.
    """

    foreground = None
    """
        Foreground color.
    """

    background = None
    """
        Background color.
    """

    bold = False
    """
        Bold text.
    """

    italic = False
    """
        Italic text.
    """

    strikethrough = False
    """
        Strike-through text.
    """

    underline = False
    """
        Underline text.
    """

    link = None
    """
        The URL to link to.
    """

    def generate_markup(self):
        result = self.text

        # The URL should always be the innermost element
        if self.link is not None:
            result = "<a href=\"%s\">%s</a>" % (self.link, result)

        if self.underline is True:
            result = "<u>%s</u>" % result

        if self.strikethrough is True:
            result = "<s>%s</s>" % result

        if self.italic is True:
            result = "<i>%s</i>" % result

        if self.bold is True:
            result = "<b>%s</b>" % result

        # Strap on a span if we need to
        span_properties = None
        if self.foreground is not None:
            span_properties = "foreground=\"%s\" " % self.foreground

        if self.background is not None:
            appended = "background=\"%s\" " % self.background

            if span_properties is not None:
                span_properties += appended
            else:
                span_properties = appended

        if span_properties is not None:
            result = "<span %s>%s</span>" % (span_properties, result)

        return result
