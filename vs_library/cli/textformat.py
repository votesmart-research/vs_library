
class TextEmphasis:

    """Directory of sequences that adds emphasis to text when printed on a CLI"""

    END = '\033[0m'
    BOLD = '\033[1m'
    GREYED_OUT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    FLIP = '\033[7m'
    TRANSPARENT = '\033[8m'


class TextColor:

    """Directory of sequences that changes the color of text when printed on a CLI"""

    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    GREY = '\033[37m'
    DARK_GREY = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    VIOLET = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'


class BackgoundColor:

    """Directory of sequences that adds highlight to text when printed on a CLI"""

    BLACK = '\033[40m'
    RED = '\033[41m'
    GREEN = '\033[42m'
    YELLOW = '\033[43m'
    BLUE = '\033[44m'
    MAGENTA = '\033[45m'
    CYAN = '\033[46m'
    GREY = '\033[47m'
    DARK_GREY = '\033[100m'
    BRIGHT_RED = '\033[101m'
    BRIGHT_GREEN = '\033[102m'
    BRIGHT_YELLOW = '\033[103m'
    BRIGHT_BLUE = '\033[104m'
    BRIGHT_MAGENTA = '\033[105m'
    BRIGHT_CYAN = '\033[106m'
    WHITE = '\033[107m'

# Gets the name of each attribute from the classes above
_TEXT_EMPHASIS_PALETTE = [attr for attr in dir(TextEmphasis) if not attr.startswith('__')]
_TEXT_COLOR_PALETTE = [attr for attr in dir(TextColor) if not attr.startswith('__')]
_BACKGROUND_COLOR_PALETTE = [attr for attr in dir(BackgoundColor) if not attr.startswith('__')]


def apply(raw_text, emphases=[None], text_color=None, bg_color=None):

    """
    Applies the listed palette by appending them to the raw text.

    Initial application of text or background color attributes cannot be overwritten or 'mixed'
    
    Parameters
    ----------
    raw_text: string
    
    emphases: array
        can have more than one attribute found in the 'TextEmphasis' class
    
    text_color: string
        can have one attribute found in 'TextColor' class
    
    bg_color: string
        can have one attribute found in 'BackgroundColor' class
    """
    
    formatted = raw_text
    
    def cast(seq):
        nonlocal formatted
        if seq not in formatted:
            if TextEmphasis.END in formatted:
                formatted = seq + formatted
            else:
                formatted =  seq + formatted + TextEmphasis.END

    for emphasis in emphases:
        if emphasis and emphasis.upper() in _TEXT_EMPHASIS_PALETTE:
            cast(vars(TextEmphasis)[emphasis.upper()])
    
    if text_color and text_color.upper() in _TEXT_COLOR_PALETTE:
        cast(vars(TextColor)[text_color.upper()])
    
    if bg_color and bg_color.upper() in _BACKGROUND_COLOR_PALETTE:
        cast(vars(BackgoundColor)[bg_color.upper()])

    return formatted


if __name__ == '__main__':

    def demo(cls):
        only_class_attributes = [attr for attr in dir(cls) if not attr.startswith('__')]

        for attr in only_class_attributes:
            print(vars(cls)[attr] + str(attr) + TextEmphasis.END)

    demo(TextEmphasis)
    print('\n')

    demo(TextColor)
    print('\n')

    demo(BackgoundColor)
    print('\n')
