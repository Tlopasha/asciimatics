from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from builtins import object
from builtins import range
from future.utils import with_metaclass
import time
from abc import ABCMeta, abstractmethod
import copy
import sys
import signal
from asciimatics.event import KeyboardEvent, MouseEvent
from .exceptions import ResizeScreenError


class Screen(with_metaclass(ABCMeta, object)):
    """
    Class to track basic state of the screen.  This constructs the necessary
    resources to allow us to do the ASCII animations.

    This is an abstract class that will build the correct concrete class for
    you when you call :py:meth:`.wrapper`.

    It is still permitted to call the class methods - e.g.
    :py:meth:`.from_curses` or :py:meth:`.from_blessed`, however these are
    deprecated and may be removed in future major releases.

    Note that you need to define the required height for your screen buffer.
    This is important if you plan on using any Effects that will scroll the
    screen vertically (e.g. Scroll).  It must be big enough to handle the
    full scrolling of your selected Effect.
    """

    #: Attribute styles supported by Screen formatting functions
    A_BOLD = 1
    A_NORMAL = 2
    A_REVERSE = 3
    A_UNDERLINE = 4

    #: Standard colours supported by Screen formatting functions
    COLOUR_BLACK = 0
    COLOUR_RED = 1
    COLOUR_GREEN = 2
    COLOUR_YELLOW = 3
    COLOUR_BLUE = 4
    COLOUR_MAGENTA = 5
    COLOUR_CYAN = 6
    COLOUR_WHITE = 7

    #: Standard extended key codes.    
    KEY_ESCAPE = -1
    KEY_F1 = -2
    KEY_F2 = -3
    KEY_F3 = -4
    KEY_F4 = -5
    KEY_F5 = -6
    KEY_F6 = -7
    KEY_F7 = -8
    KEY_F8 = -9
    KEY_F9 = -10
    KEY_F10 = -11
    KEY_F11 = -12
    KEY_F12 = -13
    KEY_F13 = -14
    KEY_F14 = -15
    KEY_F15 = -16
    KEY_F16 = -17
    KEY_F17 = -18
    KEY_F18 = -19
    KEY_F19 = -20
    KEY_F20 = -21
    KEY_F21 = -22
    KEY_F22 = -23
    KEY_F23 = -24
    KEY_F24 = -25
    KEY_PRINT_SCREEN = -100
    KEY_INSERT = -101
    KEY_DELETE = -102
    KEY_HOME = -200
    KEY_END = -201
    KEY_LEFT = -203
    KEY_UP = -204
    KEY_RIGHT = -205
    KEY_DOWN = -206
    KEY_PAGE_UP = -207
    KEY_PAGE_DOWN = -208
    KEY_BACK = -300
    KEY_TAB = -301
    KEY_NUMPAD0 = -400
    KEY_NUMPAD1 = -401
    KEY_NUMPAD2 = -402
    KEY_NUMPAD3 = -403
    KEY_NUMPAD4 = -404
    KEY_NUMPAD5 = -405
    KEY_NUMPAD6 = -406
    KEY_NUMPAD7 = -407
    KEY_NUMPAD8 = -408
    KEY_NUMPAD9 = -409
    KEY_MULTIPLY = -410
    KEY_ADD = -411
    KEY_SUBTRACT = -412
    KEY_DECIMAL = -413
    KEY_DIVIDE = -414
    KEY_CAPS_LOCK = -500
    KEY_NUM_LOCK = -501
    KEY_SCROLL_LOCK = -502
    KEY_SHIFT = -600
    KEY_CONTROL = -601
    KEY_MENU = -602

    #  Colour palette for 8/16 colour terminals
    _8_palette = [
        0x00, 0x00, 0x00,
        0x80, 0x00, 0x00,
        0x00, 0x80, 0x00,
        0x80, 0x80, 0x00,
        0x00, 0x00, 0x80,
        0x80, 0x00, 0x80,
        0x00, 0x80, 0x80,
        0xc0, 0xc0, 0xc0,
    ] + [0x00 for _ in range(248 * 3)]

    # Colour palette for 256 colour terminals
    _256_palette = [
        0x00, 0x00, 0x00,
        0x80, 0x00, 0x00,
        0x00, 0x80, 0x00,
        0x80, 0x80, 0x00,
        0x00, 0x00, 0x80,
        0x80, 0x00, 0x80,
        0x00, 0x80, 0x80,
        0xc0, 0xc0, 0xc0,
        0x80, 0x80, 0x80,
        0xff, 0x00, 0x00,
        0x00, 0xff, 0x00,
        0xff, 0xff, 0x00,
        0x00, 0x00, 0xff,
        0xff, 0x00, 0xff,
        0x00, 0xff, 0xff,
        0xff, 0xff, 0xff,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x5f,
        0x00, 0x00, 0x87,
        0x00, 0x00, 0xaf,
        0x00, 0x00, 0xd7,
        0x00, 0x00, 0xff,
        0x00, 0x5f, 0x00,
        0x00, 0x5f, 0x5f,
        0x00, 0x5f, 0x87,
        0x00, 0x5f, 0xaf,
        0x00, 0x5f, 0xd7,
        0x00, 0x5f, 0xff,
        0x00, 0x87, 0x00,
        0x00, 0x87, 0x5f,
        0x00, 0x87, 0x87,
        0x00, 0x87, 0xaf,
        0x00, 0x87, 0xd7,
        0x00, 0x87, 0xff,
        0x00, 0xaf, 0x00,
        0x00, 0xaf, 0x5f,
        0x00, 0xaf, 0x87,
        0x00, 0xaf, 0xaf,
        0x00, 0xaf, 0xd7,
        0x00, 0xaf, 0xff,
        0x00, 0xd7, 0x00,
        0x00, 0xd7, 0x5f,
        0x00, 0xd7, 0x87,
        0x00, 0xd7, 0xaf,
        0x00, 0xd7, 0xd7,
        0x00, 0xd7, 0xff,
        0x00, 0xff, 0x00,
        0x00, 0xff, 0x5f,
        0x00, 0xff, 0x87,
        0x00, 0xff, 0xaf,
        0x00, 0xff, 0xd7,
        0x00, 0xff, 0xff,
        0x5f, 0x00, 0x00,
        0x5f, 0x00, 0x5f,
        0x5f, 0x00, 0x87,
        0x5f, 0x00, 0xaf,
        0x5f, 0x00, 0xd7,
        0x5f, 0x00, 0xff,
        0x5f, 0x5f, 0x00,
        0x5f, 0x5f, 0x5f,
        0x5f, 0x5f, 0x87,
        0x5f, 0x5f, 0xaf,
        0x5f, 0x5f, 0xd7,
        0x5f, 0x5f, 0xff,
        0x5f, 0x87, 0x00,
        0x5f, 0x87, 0x5f,
        0x5f, 0x87, 0x87,
        0x5f, 0x87, 0xaf,
        0x5f, 0x87, 0xd7,
        0x5f, 0x87, 0xff,
        0x5f, 0xaf, 0x00,
        0x5f, 0xaf, 0x5f,
        0x5f, 0xaf, 0x87,
        0x5f, 0xaf, 0xaf,
        0x5f, 0xaf, 0xd7,
        0x5f, 0xaf, 0xff,
        0x5f, 0xd7, 0x00,
        0x5f, 0xd7, 0x5f,
        0x5f, 0xd7, 0x87,
        0x5f, 0xd7, 0xaf,
        0x5f, 0xd7, 0xd7,
        0x5f, 0xd7, 0xff,
        0x5f, 0xff, 0x00,
        0x5f, 0xff, 0x5f,
        0x5f, 0xff, 0x87,
        0x5f, 0xff, 0xaf,
        0x5f, 0xff, 0xd7,
        0x5f, 0xff, 0xff,
        0x87, 0x00, 0x00,
        0x87, 0x00, 0x5f,
        0x87, 0x00, 0x87,
        0x87, 0x00, 0xaf,
        0x87, 0x00, 0xd7,
        0x87, 0x00, 0xff,
        0x87, 0x5f, 0x00,
        0x87, 0x5f, 0x5f,
        0x87, 0x5f, 0x87,
        0x87, 0x5f, 0xaf,
        0x87, 0x5f, 0xd7,
        0x87, 0x5f, 0xff,
        0x87, 0x87, 0x00,
        0x87, 0x87, 0x5f,
        0x87, 0x87, 0x87,
        0x87, 0x87, 0xaf,
        0x87, 0x87, 0xd7,
        0x87, 0x87, 0xff,
        0x87, 0xaf, 0x00,
        0x87, 0xaf, 0x5f,
        0x87, 0xaf, 0x87,
        0x87, 0xaf, 0xaf,
        0x87, 0xaf, 0xd7,
        0x87, 0xaf, 0xff,
        0x87, 0xd7, 0x00,
        0x87, 0xd7, 0x5f,
        0x87, 0xd7, 0x87,
        0x87, 0xd7, 0xaf,
        0x87, 0xd7, 0xd7,
        0x87, 0xd7, 0xff,
        0x87, 0xff, 0x00,
        0x87, 0xff, 0x5f,
        0x87, 0xff, 0x87,
        0x87, 0xff, 0xaf,
        0x87, 0xff, 0xd7,
        0x87, 0xff, 0xff,
        0xaf, 0x00, 0x00,
        0xaf, 0x00, 0x5f,
        0xaf, 0x00, 0x87,
        0xaf, 0x00, 0xaf,
        0xaf, 0x00, 0xd7,
        0xaf, 0x00, 0xff,
        0xaf, 0x5f, 0x00,
        0xaf, 0x5f, 0x5f,
        0xaf, 0x5f, 0x87,
        0xaf, 0x5f, 0xaf,
        0xaf, 0x5f, 0xd7,
        0xaf, 0x5f, 0xff,
        0xaf, 0x87, 0x00,
        0xaf, 0x87, 0x5f,
        0xaf, 0x87, 0x87,
        0xaf, 0x87, 0xaf,
        0xaf, 0x87, 0xd7,
        0xaf, 0x87, 0xff,
        0xaf, 0xaf, 0x00,
        0xaf, 0xaf, 0x5f,
        0xaf, 0xaf, 0x87,
        0xaf, 0xaf, 0xaf,
        0xaf, 0xaf, 0xd7,
        0xaf, 0xaf, 0xff,
        0xaf, 0xd7, 0x00,
        0xaf, 0xd7, 0x5f,
        0xaf, 0xd7, 0x87,
        0xaf, 0xd7, 0xaf,
        0xaf, 0xd7, 0xd7,
        0xaf, 0xd7, 0xff,
        0xaf, 0xff, 0x00,
        0xaf, 0xff, 0x5f,
        0xaf, 0xff, 0x87,
        0xaf, 0xff, 0xaf,
        0xaf, 0xff, 0xd7,
        0xaf, 0xff, 0xff,
        0xd7, 0x00, 0x00,
        0xd7, 0x00, 0x5f,
        0xd7, 0x00, 0x87,
        0xd7, 0x00, 0xaf,
        0xd7, 0x00, 0xd7,
        0xd7, 0x00, 0xff,
        0xd7, 0x5f, 0x00,
        0xd7, 0x5f, 0x5f,
        0xd7, 0x5f, 0x87,
        0xd7, 0x5f, 0xaf,
        0xd7, 0x5f, 0xd7,
        0xd7, 0x5f, 0xff,
        0xd7, 0x87, 0x00,
        0xd7, 0x87, 0x5f,
        0xd7, 0x87, 0x87,
        0xd7, 0x87, 0xaf,
        0xd7, 0x87, 0xd7,
        0xd7, 0x87, 0xff,
        0xd7, 0xaf, 0x00,
        0xd7, 0xaf, 0x5f,
        0xd7, 0xaf, 0x87,
        0xd7, 0xaf, 0xaf,
        0xd7, 0xaf, 0xd7,
        0xd7, 0xaf, 0xff,
        0xd7, 0xd7, 0x00,
        0xd7, 0xd7, 0x5f,
        0xd7, 0xd7, 0x87,
        0xd7, 0xd7, 0xaf,
        0xd7, 0xd7, 0xd7,
        0xd7, 0xd7, 0xff,
        0xd7, 0xff, 0x00,
        0xd7, 0xff, 0x5f,
        0xd7, 0xff, 0x87,
        0xd7, 0xff, 0xaf,
        0xd7, 0xff, 0xd7,
        0xd7, 0xff, 0xff,
        0xff, 0x00, 0x00,
        0xff, 0x00, 0x5f,
        0xff, 0x00, 0x87,
        0xff, 0x00, 0xaf,
        0xff, 0x00, 0xd7,
        0xff, 0x00, 0xff,
        0xff, 0x5f, 0x00,
        0xff, 0x5f, 0x5f,
        0xff, 0x5f, 0x87,
        0xff, 0x5f, 0xaf,
        0xff, 0x5f, 0xd7,
        0xff, 0x5f, 0xff,
        0xff, 0x87, 0x00,
        0xff, 0x87, 0x5f,
        0xff, 0x87, 0x87,
        0xff, 0x87, 0xaf,
        0xff, 0x87, 0xd7,
        0xff, 0x87, 0xff,
        0xff, 0xaf, 0x00,
        0xff, 0xaf, 0x5f,
        0xff, 0xaf, 0x87,
        0xff, 0xaf, 0xaf,
        0xff, 0xaf, 0xd7,
        0xff, 0xaf, 0xff,
        0xff, 0xd7, 0x00,
        0xff, 0xd7, 0x5f,
        0xff, 0xd7, 0x87,
        0xff, 0xd7, 0xaf,
        0xff, 0xd7, 0xd7,
        0xff, 0xd7, 0xff,
        0xff, 0xff, 0x00,
        0xff, 0xff, 0x5f,
        0xff, 0xff, 0x87,
        0xff, 0xff, 0xaf,
        0xff, 0xff, 0xd7,
        0xff, 0xff, 0xff,
        0x08, 0x08, 0x08,
        0x12, 0x12, 0x12,
        0x1c, 0x1c, 0x1c,
        0x26, 0x26, 0x26,
        0x30, 0x30, 0x30,
        0x3a, 0x3a, 0x3a,
        0x44, 0x44, 0x44,
        0x4e, 0x4e, 0x4e,
        0x58, 0x58, 0x58,
        0x62, 0x62, 0x62,
        0x6c, 0x6c, 0x6c,
        0x76, 0x76, 0x76,
        0x80, 0x80, 0x80,
        0x8a, 0x8a, 0x8a,
        0x94, 0x94, 0x94,
        0x9e, 0x9e, 0x9e,
        0xa8, 0xa8, 0xa8,
        0xb2, 0xb2, 0xb2,
        0xbc, 0xbc, 0xbc,
        0xc6, 0xc6, 0xc6,
        0xd0, 0xd0, 0xd0,
        0xda, 0xda, 0xda,
        0xe4, 0xe4, 0xe4,
        0xee, 0xee, 0xee,
    ]

    # Characters for anti-aliasing line drawing.
    _line_chars = " ''^.|/7.\\|Ywbd#"

    def __init__(self, height, width):
        """
        Don't call this constructor directly.
        """
        # Initialize base class variables - e.g. those used for drawing.
        self.height = height
        self.width = width
        self.colours = 0
        self._start_line = 0
        self._x = 0
        self._y = 0

    @classmethod
    def from_curses(cls, win, height=200):
        """
        Construct a new Screen from a curses windows.

        :param win: The curses window to use.
        :param height: The buffer height for this window (if using scrolling).
        """
        return _CursesScreen(win, height)

    @classmethod
    def from_blessed(cls, terminal, height=200):
        """
        Construct a new Screen from a blessed terminal.

        :param terminal: The blessed Terminal to use.
        :param height: The buffer height for this window (if using scrolling).
        """
        return _BlessedScreen(terminal, height)

    @classmethod
    def from_windows(cls, stdout, stdin, height=200):
        """
        Construct a new Screen from a Windows console.

        :param stdout: The Windows PyConsoleScreenBufferType for stdout returned
            from win32console.
        :param stdin: The Windows PyConsoleScreenBufferType for stdin returned
            from win32console.
        :param height: The buffer height for this window (if using scrolling).
        """
        return _WindowsScreen(stdout, stdin, height)

    @classmethod
    def wrapper(cls, func, height=200):
        """
        Construct a new Screen for any platform.  This will initialize and tidy
        up the system as required around the underlying console subsystem.

        :param func: The function to call once the screen has been created.
        :param height: The buffer height for this window (if using scrolling).
        """
        if sys.platform == "win32":
            # Get the standard input/output buffers.
            win_out = win32console.PyConsoleScreenBufferType(
                win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE))
            win_in = win32console.PyConsoleScreenBufferType(
                win32console.GetStdHandle(win32console.STD_INPUT_HANDLE))

            # Hide the cursor.
            (size, visible) = win_out.GetConsoleCursorInfo()
            win_out.SetConsoleCursorInfo(1, 0)

            # Disable scrolling
            out_mode = win_out.GetConsoleMode()
            win_out.SetConsoleMode(
                out_mode & ~ win32console.ENABLE_WRAP_AT_EOL_OUTPUT)

            # Enable mouse input
            in_mode = win_in.GetConsoleMode()
            win_in.SetConsoleMode(in_mode | win32console.ENABLE_MOUSE_INPUT)

            try:
                win_screen = _WindowsScreen(win_out, win_in, height)
                func(win_screen)
            finally:
                win_out.SetConsoleCursorInfo(size, visible)
                win_out.SetConsoleMode(out_mode)
                win_out.SetConsoleTextAttribute(7)
                win_in.SetConsoleMode(in_mode)
        else:
            def _wrapper(win):
                cur_screen = _CursesScreen(win, height)
                func(cur_screen)

            curses.wrapper(_wrapper)

    @property
    def start_line(self):
        """
        :return: The start line of the top of the window in the display buffer.
        """
        return self._start_line

    @property
    def dimensions(self):
        """
        :return: The full dimensions of the display buffer as a (height,
            width) tuple.
        """
        return self.height, self.width

    @property
    def palette(self):
        """
        :return: A palette compatible with the PIL.
        """
        if self.colours < 256:
            # Use the ANSI colour set.
            return self._8_palette
        else:
            return self._256_palette

    @abstractmethod
    def scroll(self):
        """
        Scroll the Screen up one line.
        """

    @abstractmethod
    def clear(self):
        """
        Clear the Screen of all content.
        """

    @abstractmethod
    def refresh(self):
        """
        Refresh the screen.
        """

    def get_key(self):
        """
        Check for a key without waiting.  This method is deprecated.  Use
        :py:meth:`.get_event` instead.
        """
        event = self.get_event()
        if event and isinstance(event, KeyboardEvent):
            return event.key_code
        return None

    @abstractmethod
    def get_event(self):
        """
        Check for any events (e.g. key-press or mouse movement) without waiting.

        :returns: A :py:obj:`.Event` object if anything was detected, otherwise
                  it returns None.
        """

    @abstractmethod
    def has_resized(self):
        """
        Check whether the screen has been re-sized.

        :returns: True when the screen has been re-sized since the last check.
        """

    @abstractmethod
    def get_from(self, x, y):
        """
        Get the character at the specified location.

        :param x: The column (x coord) of the character.
        :param y: The row (y coord) of the character.

        :return: A tuple of the ASCII code of the character at the location
                 and the colour attributes for that character.  The format
                 is (<character>, <foreground>, <attribute>, <background>).
        """

    def getch(self, x, y):
        """
        Check for a key without waiting.  This method is deprecated.  Use
        :py:meth:`.get_from` instead.
        """
        return self.get_from(x, y)

    @abstractmethod
    def print_at(self, text, x, y, colour=7, attr=0, bg=0, transparent=False):
        """
        Check for a key without waiting.  This method is deprecated.  Use
        :py:meth:`.print_at` instead.

        Print the text at the specified location using the
        specified colour and attributes.

        :param text: The (single line) text to be printed.
        :param x: The column (x coord) for the start of the text.
        :param y: The line (y coord) for the start of the text.
        :param colour: The colour of the text to be displayed.
        :param attr: The cell attribute of the text to be displayed.
        :param bg: The background colour of the text to be displayed.
        :param transparent: Whether to print spaces or not, thus giving a
            transparent effect.

        The colours and attributes are the COLOUR_xxx and A_yyy constants
        defined in the Screen class.
        """

    def putch(self, text, x, y, colour=7, attr=0, bg=0, transparent=False):
        """
        Check for a key without waiting.  This method is deprecated.  Use
        :py:meth:`.print_at` instead.
        """
        self.putch(text, x, y, colour, attr, bg, transparent)

    def centre(self, text, y, colour=7, attr=0, colour_map=None):
        """
        Centre the text on the specified line (y) using the optional
        colour and attributes.

        :param text: The (single line) text to be printed.
        :param y: The line (y coord) for the start of the text.
        :param colour: The colour of the text to be displayed.
        :param attr: The cell attribute of the text to be displayed.
        :param colour_map: Colour/attribute list for multi-colour text.

        The colours and attributes are the COLOUR_xxx and A_yyy constants
        defined in the Screen class.
        """
        x = (self.width - len(text)) // 2
        self.paint(text, x, y, colour, attr, colour_map=colour_map)

    def paint(self, text, x, y, colour=7, attr=0, bg=0, transparent=False,
              colour_map=None):
        """
        Paint multi-colour text at the defined location.

        :param text: The (single line) text to be printed.
        :param x: The column (x coord) for the start of the text.
        :param y: The line (y coord) for the start of the text.
        :param colour: The default colour of the text to be displayed.
        :param attr: The default cell attribute of the text to be displayed.
        :param bg: The default background colour of the text to be displayed.
        :param transparent: Whether to print spaces or not, thus giving a
            transparent effect.
        :param colour_map: Colour/attribute list for multi-colour text.

        The colours and attributes are the COLOUR_xxx and A_yyy constants
        defined in the Screen class.
        colour_map is a list of tuples (colour, attribute) that must be the
        same length as the passed in text (or None if no mapping is required).
        """
        if colour_map is None:
            self.print_at(text, x, y, colour, attr, bg, transparent)
        else:
            for i, c in enumerate(text):
                if len(colour_map[i]) > 0 and colour_map[i][0] is not None:
                    colour = colour_map[i][0]
                if len(colour_map[i]) > 1 and colour_map[i][1] is not None:
                    attr = colour_map[i][1]
                if len(colour_map[i]) > 2 and colour_map[i][2] is not None:
                    bg = colour_map[i][2]
                self.print_at(c, x + i, y, colour, attr, bg, transparent)

    def is_visible(self, x, y):
        """
        Return whether the specified location is on the visible screen.

        :param x: The column (x coord) for the location to check.
        :param y: The line (y coord) for the location to check.
        """
        return ((x >= 0) and
                (x <= self.width) and
                (y >= self._start_line) and
                (y < self._start_line + self.height))

    def play(self, scenes, stop_on_resize=False):
        """
        Play a set of scenes.

        :param scenes: a list of :py:obj:`.Scene` objects to play.
        :param stop_on_resize: Whether to stop when the screen is resized.
            Default is to carry on regardless - which will typically result
            in an error. This is largely done for back-compatibility.

        :raises ResizeScreenError: if the screen is resized (and allowed by
            stop_on_resize).
        """
        self.clear()
        while True:
            for scene in scenes:
                frame = 0
                if scene.clear:
                    self.clear()
                scene.reset()
                re_sized = skipped = False
                while (scene.duration < 0 or frame < scene.duration) and \
                        not re_sized and not skipped:
                    frame += 1
                    for effect in scene.effects:
                        effect.update(frame)
                        if effect.delete_count is not None:
                            effect.delete_count -= 1
                            if effect.delete_count == 0:
                                scene.remove_effect(effect)
                    self.refresh()
                    event = self.get_event()
                    while event is not None:
                        event = scene.process_event(event)
                        if isinstance(event, KeyboardEvent):
                            c = event.key_code
                            if c in (ord("X"), ord("x"), ord("Q"), ord("q")):
                                return
                            if c in (ord(" "), ord("\n")):
                                skipped = True
                                break
                        event = self.get_event()
                    re_sized = self.has_resized()
                    time.sleep(0.05)

                # Break out of the function if mandated by caller.
                if re_sized:
                    if stop_on_resize:
                        raise ResizeScreenError("Resized terminal")

    def move(self, x, y):
        """
        Move the drawing cursor to the specified position.

        :param x: The column (x coord) for the location to check.
        :param y: The line (y coord) for the location to check.
        """
        self._x = int(round(x, 1)) * 2
        self._y = int(round(y, 1)) * 2

    def draw(self, x, y, char=None, colour=7, bg=0, thin=False):
        """
        Draw a line from drawing cursor to the specified position.  This uses a
        modified Bressenham algorithm, interpolating twice as many points to
        render down to anti-aliased characters when no character is specified,
        or uses standard algorithm plotting with the specified character.

        :param x: The column (x coord) for the location to check.
        :param y: The line (y coord) for the location to check.
        :param char: Optional character to use to draw the line.
        :param colour: Optional colour for plotting the line.
        :param bg: Optional background colour for plotting the line.
        :param thin: Optional width of anti-aliased line.
        """
        # Define line end points.
        x0 = self._x
        y0 = self._y
        x1 = int(round(x, 1)) * 2
        y1 = int(round(y, 1)) * 2

        # Remember last point for next line.
        self._x = x1
        self._y = y1

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = -1 if x0 > x1 else 1
        sy = -1 if y0 > y1 else 1

        x_range = range(0, 2) if sx > 0 else range(1, -1, -1)
        y_range = range(0, 2) if sy > 0 else range(1, -1, -1)

        x = x0
        y = y0

        if dx > dy:
            err = dx
            while x != x1:
                next_chars = [0, 0]
                px = x & ~1
                py = y & ~1
                for ix in x_range:
                    if y >= py and y - py < 2:
                        next_chars[0] |= 2 ** ix * 4 ** (y % 2)
                    else:
                        next_chars[1] |= 2 ** ix * 4 ** (y % 2)
                    if not thin:
                        if y + sy >= py and y + sy - py < 2:
                            next_chars[0] |= 2 ** ix * 4 ** ((y + sy) % 2)
                        else:
                            next_chars[1] |= 2 ** ix * 4 ** ((y + sy) % 2)
                    err -= 2 * dy
                    if err < 0:
                        y += sy
                        err += 2 * dx
                    x += sx

                if char is None:
                    self.print_at(self._line_chars[next_chars[0]], px//2, py//2,
                                  colour, bg=bg)
                    if next_chars[1] != 0:
                        self.print_at(self._line_chars[next_chars[1]],
                                      px // 2, py // 2 + sy, colour, bg=bg)
                elif char == " ":
                    self.print_at(char, px // 2, py // 2, bg=bg)
                    self.print_at(char, px // 2, py // 2 + sy, bg=bg)
                else:
                    self.print_at(char, px // 2, py // 2, colour, bg=bg)
        else:
            err = dy
            while y != y1:
                next_chars = [0, 0]
                px = x & ~1
                py = y & ~1
                for iy in y_range:
                    if x >= px and x - px < 2:
                        next_chars[0] |= 2 ** (x % 2) * 4 ** iy
                    else:
                        next_chars[1] |= 2 ** (x % 2) * 4 ** iy
                    if not thin:
                        if x + sx >= px and x + sx - px < 2:
                            next_chars[0] |= 2 ** ((x + sx) % 2) * 4 ** iy
                        else:
                            next_chars[1] |= 2 ** ((x + sx) % 2) * 4 ** iy
                    err -= 2 * dx
                    if err < 0:
                        x += sx
                        err += 2 * dy
                    y += sy

                if char is None:
                    self.print_at(self._line_chars[next_chars[0]], px//2, py//2,
                                  colour, bg=bg)
                    if next_chars[1] != 0:
                        self.print_at(
                            self._line_chars[next_chars[1]], px//2 + sx, py//2,
                            colour, bg=bg)
                elif char == " ":
                    self.print_at(char, px // 2, py // 2, bg=bg)
                    self.print_at(char, px // 2 + sx, py // 2, bg=bg)
                else:
                    self.print_at(char, px // 2, py // 2, colour, bg=bg)


class _BufferedScreen(with_metaclass(ABCMeta, Screen)):
    """
    Abstract class to handle screen buffering when not using curses.
    """

    def __init__(self, height, width, buffer_height):
        """
        :param height: The buffer height for this window.
        :param width: The buffer width for this window.
        :param buffer_height: The buffer height for this window.
        """
        # Save off the screen details and se up the scrolling pad.
        super(_BufferedScreen, self).__init__(height, width)

        # Create screen buffers (required to reduce flicker).
        self._screen_buffer = None
        self._double_buffer = None
        self._buffer_height = buffer_height

        # Remember current state so we don't keep programming colours/attributes
        # and move commands unnecessarily.
        self._colour = None
        self._attr = None
        self._bg = None
        self._x = None
        self._y = None
        self._last_start_line = 0

        # Reset the screen ready to go...
        self._reset()

    def _reset(self):
        """
        Reset the internal buffers for the screen.
        """
        self._start_line = self._last_start_line = 0
        self._x = self._y = None

        # Reset our screen buffer
        line = [(" ", 7, 0, 0) for _ in range(self.width)]
        self._screen_buffer = [
            copy.deepcopy(line) for _ in range(self._buffer_height)]
        self._double_buffer = copy.deepcopy(self._screen_buffer)

    def scroll(self):
        """
        Scroll the Screen up one line.
        """
        self._start_line += 1

    def clear(self):
        """
        Clear the Screen of all content.
        """
        # Clear the actual terminal
        self._change_colours(self.COLOUR_WHITE, 0, 0)
        self._clear()
        self._reset()

    def refresh(self):
        """
        Refresh the screen.
        """
        # Scroll the screen as required to minimize redrawing.
        for _ in range(self._start_line - self._last_start_line):
            self._scroll()
        self._last_start_line = self._start_line

        # Now draw any deltas to the scrolled screen.
        for y in range(self.height):
            for x in range(self.width):
                new_cell = self._double_buffer[y + self._start_line][x]
                if self._screen_buffer[y + self._start_line][x] != new_cell:
                    self._change_colours(new_cell[1], new_cell[2], new_cell[3])
                    self._print_at(new_cell[0], x, y)
                    self._screen_buffer[y + self._start_line][x] = new_cell

    def get_from(self, x, y):
        """
        Get the character at the specified location.

        :param x: The column (x coord) of the character.
        :param y: The row (y coord) of the character.

        :return: A 4-tuple of (ascii code, foreground, attributes, background)
                 for the character at the location.
        """
        cell = self._screen_buffer[y][x]
        return ord(cell[0]), cell[1], cell[2], cell[3]

    def print_at(self, text, x, y, colour=7, attr=0, bg=0, transparent=False):
        """
        Print the text at the specified location using the
        specified colour and attributes.

        :param text: The (single line) text to be printed.
        :param x: The column (x coord) for the start of the text.
        :param y: The line (y coord) for the start of the text.
        :param colour: The colour of the text to be displayed.
        :param attr: The cell attribute of the text to be displayed.
        :param bg: The background colour of the text to be displayed.
        :param transparent: Whether to print spaces or not, thus giving a
            transparent effect.

        The colours and attributes are the COLOUR_xxx and A_yyy constants
        defined in the Screen class.
        """
        # Trim text to the buffer.
        if y < 0 or y >= self._buffer_height:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if x + len(text) >= self.width:
            text = text[:self.width - x]

        if len(text) > 0:
            for i, c in enumerate(text):
                if c != " " or not transparent:
                    self._double_buffer[y][x + i] = (c, colour, attr, bg)

    @abstractmethod
    def _change_colours(self, colour, attr, bg):
        """
        Change current colour if required.

        :param colour: New colour to use.
        :param attr: New attributes to use.
        :param bg: New background colour to use.
        """

    @abstractmethod
    def _print_at(self, text, x, y):
        """
        Print string at the required location.

        :param text: The text string to print.
        :param x: The x coordinate
        :param y: The Y coordinate
        """

    @abstractmethod
    def _clear(self):
        """
        Clear the window.
        """

    @abstractmethod
    def _scroll(self):
        """
        Scroll the window up one line.
        """


if sys.platform == "win32":
    import win32console
    import win32con

    class _WindowsScreen(_BufferedScreen):
        """
        Windows screen implementation.
        """

        # Virtual key code mapping.
        _KEY_MAP = {
            win32con.VK_ESCAPE: Screen.KEY_ESCAPE,
            win32con.VK_F1: Screen.KEY_F1,
            win32con.VK_F2: Screen.KEY_F2,
            win32con.VK_F3: Screen.KEY_F3,
            win32con.VK_F4: Screen.KEY_F4,
            win32con.VK_F5: Screen.KEY_F5,
            win32con.VK_F6: Screen.KEY_F6,
            win32con.VK_F7: Screen.KEY_F7,
            win32con.VK_F8: Screen.KEY_F8,
            win32con.VK_F9: Screen.KEY_F9,
            win32con.VK_F10: Screen.KEY_F10,
            win32con.VK_F11: Screen.KEY_F11,
            win32con.VK_F12: Screen.KEY_F12,
            win32con.VK_F13: Screen.KEY_F13,
            win32con.VK_F14: Screen.KEY_F14,
            win32con.VK_F15: Screen.KEY_F15,
            win32con.VK_F16: Screen.KEY_F16,
            win32con.VK_F17: Screen.KEY_F17,
            win32con.VK_F18: Screen.KEY_F18,
            win32con.VK_F19: Screen.KEY_F19,
            win32con.VK_F20: Screen.KEY_F20,
            win32con.VK_F21: Screen.KEY_F21,
            win32con.VK_F22: Screen.KEY_F22,
            win32con.VK_F23: Screen.KEY_F23,
            win32con.VK_F24: Screen.KEY_F24,
            win32con.VK_PRINT: Screen.KEY_PRINT_SCREEN,
            win32con.VK_INSERT: Screen.KEY_INSERT,
            win32con.VK_DELETE: Screen.KEY_DELETE,
            win32con.VK_HOME: Screen.KEY_HOME,
            win32con.VK_END: Screen.KEY_END,
            win32con.VK_LEFT: Screen.KEY_LEFT,
            win32con.VK_UP: Screen.KEY_UP,
            win32con.VK_RIGHT: Screen.KEY_RIGHT,
            win32con.VK_DOWN: Screen.KEY_DOWN,
            win32con.VK_PRIOR: Screen.KEY_PAGE_UP,
            win32con.VK_NEXT: Screen.KEY_PAGE_DOWN,
            win32con.VK_BACK: Screen.KEY_BACK,
            win32con.VK_TAB: Screen.KEY_TAB,
        }

        _EXTRA_KEY_MAP = {
            win32con.VK_NUMPAD0: Screen.KEY_NUMPAD0,
            win32con.VK_NUMPAD1: Screen.KEY_NUMPAD1,
            win32con.VK_NUMPAD2: Screen.KEY_NUMPAD2,
            win32con.VK_NUMPAD3: Screen.KEY_NUMPAD3,
            win32con.VK_NUMPAD4: Screen.KEY_NUMPAD4,
            win32con.VK_NUMPAD5: Screen.KEY_NUMPAD5,
            win32con.VK_NUMPAD6: Screen.KEY_NUMPAD6,
            win32con.VK_NUMPAD7: Screen.KEY_NUMPAD7,
            win32con.VK_NUMPAD8: Screen.KEY_NUMPAD8,
            win32con.VK_NUMPAD9: Screen.KEY_NUMPAD9,
            win32con.VK_MULTIPLY: Screen.KEY_MULTIPLY,
            win32con.VK_ADD: Screen.KEY_ADD,
            win32con.VK_SUBTRACT: Screen.KEY_SUBTRACT,
            win32con.VK_DECIMAL: Screen.KEY_DECIMAL,
            win32con.VK_DIVIDE: Screen.KEY_DIVIDE,
            win32con.VK_CAPITAL: Screen.KEY_CAPS_LOCK,
            win32con.VK_NUMLOCK: Screen.KEY_NUM_LOCK,
            win32con.VK_SCROLL: Screen.KEY_SCROLL_LOCK,
            win32con.VK_SHIFT: Screen.KEY_SHIFT,
            win32con.VK_CONTROL: Screen.KEY_CONTROL,
            win32con.VK_MENU: Screen.KEY_MENU,
        }

        # Foreground colour lookup table.
        _COLOURS = {
            Screen.COLOUR_BLACK: 0,
            Screen.COLOUR_RED: win32console.FOREGROUND_RED,
            Screen.COLOUR_GREEN: win32console.FOREGROUND_GREEN,
            Screen.COLOUR_YELLOW: (win32console.FOREGROUND_RED |
                                   win32console.FOREGROUND_GREEN),
            Screen.COLOUR_BLUE: win32console.FOREGROUND_BLUE,
            Screen.COLOUR_MAGENTA: (win32console.FOREGROUND_RED |
                                    win32console.FOREGROUND_BLUE),
            Screen.COLOUR_CYAN: (win32console.FOREGROUND_BLUE |
                                 win32console.FOREGROUND_GREEN),
            Screen.COLOUR_WHITE: (win32console.FOREGROUND_RED |
                                  win32console.FOREGROUND_GREEN |
                                  win32console.FOREGROUND_BLUE)
        }

        # Background colour lookup table.
        _BG_COLOURS = {
            Screen.COLOUR_BLACK: 0,
            Screen.COLOUR_RED: win32console.BACKGROUND_RED,
            Screen.COLOUR_GREEN: win32console.BACKGROUND_GREEN,
            Screen.COLOUR_YELLOW: (win32console.BACKGROUND_RED |
                                   win32console.BACKGROUND_GREEN),
            Screen.COLOUR_BLUE: win32console.BACKGROUND_BLUE,
            Screen.COLOUR_MAGENTA: (win32console.BACKGROUND_RED |
                                    win32console.BACKGROUND_BLUE),
            Screen.COLOUR_CYAN: (win32console.BACKGROUND_BLUE |
                                 win32console.BACKGROUND_GREEN),
            Screen.COLOUR_WHITE: (win32console.BACKGROUND_RED |
                                  win32console.BACKGROUND_GREEN |
                                  win32console.BACKGROUND_BLUE)
        }

        # Attribute lookup table
        _ATTRIBUTES = {
            0: lambda x: x,
            Screen.A_BOLD: lambda x: x | win32console.FOREGROUND_INTENSITY,
            Screen.A_NORMAL: lambda x: x,
            # Windows console uses a bitmap where background is the top nibble,
            # so we can reverse by swapping nibbles.
            Screen.A_REVERSE: lambda x: ((x & 15) * 16) + ((x & 240) // 16),
            Screen.A_UNDERLINE: lambda x: x
        }

        def __init__(self, stdout, stdin, buffer_height):
            """
            :param stdout: The win32console PyConsoleScreenBufferType object for
                stdout.
            :param stdin: The win32console PyConsoleScreenBufferType object for
                stdin.
            :param buffer_height: The buffer height for this window (if using
                scrolling).
            """
            # Save off the screen details and se up the scrolling pad.
            info = stdout.GetConsoleScreenBufferInfo()['Window']
            width = info.Right - info.Left + 1
            height = info.Bottom - info.Top + 1
            super(_WindowsScreen, self).__init__(height, width, buffer_height)

            # Save off the console details.
            self._stdout = stdout
            self._stdin = stdin
            self._last_width = None
            self._last_height = None

            # Windows is limited to the ANSI colour set.
            self.colours = 8

            # Opt for compatibility with Linux by default
            self._map_all = False

        def map_all_keys(self, state):
            """
            Switch on extended keyboard mapping for this Screen.

            :param state: Boolean flag where true means map all keys.

            Enabling this setting will allow Windows to tell you when any key
            is pressed, including metakeys (like shift and control) and whether
            the numeric keypad keys have been used.

            .. warning::

                Using this means your application will not be compatible across
                all platforms.
            """
            self._map_all = state

        def get_event(self):
            """
            Check for any event without waiting.
            """
            # Look for a new event and consume it if there is one.
            if len(self._stdin.PeekConsoleInput(1)) > 0:
                event = self._stdin.ReadConsoleInput(1)[0]
                if (event.EventType == win32console.KEY_EVENT and
                        event.KeyDown):
                    # Translate keys into a KeyboardEvent object.
                    key_code = ord(event.Char)
                    if event.VirtualKeyCode in self._KEY_MAP:
                        key_code = self._KEY_MAP[event.VirtualKeyCode]
                    if (self._map_all and
                            event.VirtualKeyCode in self._EXTRA_KEY_MAP):
                        key_code = self._EXTRA_KEY_MAP[event.VirtualKeyCode]
                    return KeyboardEvent(key_code)
                elif event.EventType == win32console.MOUSE_EVENT:
                    # Translate into a MouseEvent object.
                    button = 0
                    if event.EventFlags == 0:
                        # Button pressed - translate it.
                        if (event.ButtonState &
                                win32con.FROM_LEFT_1ST_BUTTON_PRESSED != 0):
                            button |= MouseEvent.LEFT_CLICK
                        if (event.ButtonState &
                                win32con.RIGHTMOST_BUTTON_PRESSED != 0):
                            button |= MouseEvent.RIGHT_CLICK
                    elif event.EventFlags & win32con.DOUBLE_CLICK != 0:
                        button |= MouseEvent.DOUBLE_CLICK

                    return MouseEvent(event.MousePosition.X,
                                      event.MousePosition.Y,
                                      button)
            return None

        def has_resized(self):
            """
            Check whether the screen has been re-sized.
            """
            # Get the current Window dimensions and check them against last
            # time.
            re_sized = False
            info = self._stdout.GetConsoleScreenBufferInfo()['Window']
            width = info.Right - info.Left + 1
            height = info.Bottom - info.Top + 1
            if self._last_width is not None and (
                    width != self._last_width or height != self._last_height):
                re_sized = True
            self._last_width = width
            self._last_height = height
            return re_sized

        def _change_colours(self, colour, attr, bg):
            """
            Change current colour if required.

            :param colour: New colour to use.
            :param attr: New attributes to use.
            :param bg: New background colour to use.
            """
            # Change attribute first as this will reset colours when swapping
            # modes.
            if colour != self._colour or attr != self._attr or self._bg != bg:
                new_attr = self._ATTRIBUTES[attr](
                    self._COLOURS[colour] + self._BG_COLOURS[bg])
                self._stdout.SetConsoleTextAttribute(new_attr)
                self._attr = attr
                self._colour = colour
                self._bg = bg

        def _print_at(self, text, x, y):
            """
            Print string at the required location.

            :param text: The text string to print.
            :param x: The x coordinate
            :param y: The Y coordinate
            """
            # Move the cursor if necessary
            if x != self._x or y != self._y:
                self._stdout.SetConsoleCursorPosition(
                    win32console.PyCOORDType(x, y))

            # Print the text at the required location and update the current
            # position.
            self._stdout.WriteConsole(text)
            self._x = x + len(text)
            self._y = y

        def _scroll(self):
            """
            Scroll up by one line.
            """
            # Scroll the visible screen up by one line
            info = self._stdout.GetConsoleScreenBufferInfo()['Window']
            rectangle = win32console.PySMALL_RECTType(info.Left, info.Top + 1,
                                                      info.Right, info.Bottom)
            new_pos = win32console.PyCOORDType(0, info.Top)
            self._stdout.ScrollConsoleScreenBuffer(
                rectangle, None, new_pos, " ", 0)

        def _clear(self):
            """
            Clear the terminal.
            """
            info = self._stdout.GetConsoleScreenBufferInfo()['Window']
            width = info.Right - info.Left + 1
            height = info.Bottom - info.Top + 1
            box_size = width * height
            self._stdout.FillConsoleOutputAttribute(
                0, box_size, win32console.PyCOORDType(0, 0))
            self._stdout.FillConsoleOutputCharacter(
                u" ", box_size, win32console.PyCOORDType(0, 0))
            self._stdout.SetConsoleCursorPosition(
                win32console.PyCOORDType(0, 0))
else:
    # UNIX compatible platform - use curses
    import curses

    class _CursesScreen(_BufferedScreen):
        """
        Curses screen implementation.
        """

        # Virtual key code mapping.
        _KEY_MAP = {
            27: Screen.KEY_ESCAPE,
            curses.KEY_F1: Screen.KEY_F1,
            curses.KEY_F2: Screen.KEY_F2,
            curses.KEY_F3: Screen.KEY_F3,
            curses.KEY_F4: Screen.KEY_F4,
            curses.KEY_F5: Screen.KEY_F5,
            curses.KEY_F6: Screen.KEY_F6,
            curses.KEY_F7: Screen.KEY_F7,
            curses.KEY_F8: Screen.KEY_F8,
            curses.KEY_F9: Screen.KEY_F9,
            curses.KEY_F10: Screen.KEY_F10,
            curses.KEY_F11: Screen.KEY_F11,
            curses.KEY_F12: Screen.KEY_F12,
            curses.KEY_F13: Screen.KEY_F13,
            curses.KEY_F14: Screen.KEY_F14,
            curses.KEY_F15: Screen.KEY_F15,
            curses.KEY_F16: Screen.KEY_F16,
            curses.KEY_F17: Screen.KEY_F17,
            curses.KEY_F18: Screen.KEY_F18,
            curses.KEY_F19: Screen.KEY_F19,
            curses.KEY_F20: Screen.KEY_F20,
            curses.KEY_F21: Screen.KEY_F21,
            curses.KEY_F22: Screen.KEY_F22,
            curses.KEY_F23: Screen.KEY_F23,
            curses.KEY_F24: Screen.KEY_F24,
            curses.KEY_PRINT: Screen.KEY_PRINT_SCREEN,
            curses.KEY_IC: Screen.KEY_INSERT,
            curses.KEY_DC: Screen.KEY_DELETE,
            curses.KEY_HOME: Screen.KEY_HOME,
            curses.KEY_END: Screen.KEY_END,
            curses.KEY_LEFT: Screen.KEY_LEFT,
            curses.KEY_UP: Screen.KEY_UP,
            curses.KEY_RIGHT: Screen.KEY_RIGHT,
            curses.KEY_DOWN: Screen.KEY_DOWN,
            curses.KEY_PPAGE: Screen.KEY_PAGE_UP,
            curses.KEY_NPAGE: Screen.KEY_PAGE_DOWN,
            curses.KEY_BACKSPACE: Screen.KEY_BACK,
            9: Screen.KEY_TAB,
            # Terminals translate keypad keys, so no need for a special
            # mapping here.

            # Terminals don't transmit meta keys (like control, shift, etc), so
            # there's no translation for them either.
        }

        def __init__(self, win, height=200):
            """
            :param win: The window object as returned by the curses wrapper
                method.
            :param height: The height of the screen buffer to be used.
            """
            # Save off the screen details.
            super(_CursesScreen, self).__init__(
                win.getmaxyx()[0], win.getmaxyx()[1], height)
            self._screen = win
            self._screen.keypad(1)

            # Set up basic colour schemes.
            self.colours = curses.COLORS

            # Disable the cursor.
            curses.curs_set(0)

            # Non-blocking key checks.
            self._screen.nodelay(1)

            # Set up signal handler for screen resizing.
            self._re_sized = False
            signal.signal(signal.SIGWINCH, self._resize_handler)

            # Enable mouse events
            curses.mousemask(curses.ALL_MOUSE_EVENTS |
                             curses.REPORT_MOUSE_POSITION)

            # Lookup the necessary escape codes in the terminfo database.
            self._move_y_x = curses.tigetstr("cup")
            self._fg_color = curses.tigetstr("setaf")
            self._bg_color = curses.tigetstr("setab")
            self._a_normal = curses.tigetstr("sgr0")
            self._a_bold = curses.tigetstr("bold")
            self._a_reverse = curses.tigetstr("rev")
            self._a_underline = curses.tigetstr("smul")
            self._clear_screen = curses.tigetstr("clear")

            # Conversion from Screen attributes to curses equivalents.
            self._ATTRIBUTES = {
                Screen.A_BOLD: self._a_bold,
                Screen.A_NORMAL: self._a_normal,
                Screen.A_REVERSE: self._a_reverse,
                Screen.A_UNDERLINE: self._a_underline
            }

            # We'll actually break out into low-level output, so flush any
            # high level buffers now.
            self._screen.refresh()

        def _resize_handler(self, *_):
            """
            Window resize signal handler.  We don't care about any of the
            parameters passed in beyond the object reference.
            """
            curses.endwin()
            curses.initscr()
            self._re_sized = True

        def _scroll(self):
            """
            Scroll the Screen up one line.
            """
            print(curses.tparm(self._move_y_x, self.height - 1, 0))

        def _clear(self):
            """
            Clear the Screen of all content.
            """
            sys.stdout.write(self._clear_screen)
            sys.stdout.flush()

        def refresh(self):
            """
            Refresh the screen.
            """
            super(_CursesScreen, self).refresh()
            try:
                sys.stdout.flush()
            except IOError:
                pass

        def get_event(self):
            """
            Check for an event without waiting.
            """
            key = self._screen.get_from()
            if key == curses.KEY_RESIZE:
                # Handle screen resize
                self._re_sized = True
            elif key == curses.KEY_MOUSE:
                # Handle a mouse event
                _, x, y, _, bstate = curses.getmouse()
                buttons = 0
                if bstate & curses.BUTTON1_CLICKED != 0:
                    buttons |= MouseEvent.LEFT_CLICK
                if bstate & curses.BUTTON3_CLICKED != 0:
                    buttons |= MouseEvent.RIGHT_CLICK
                if bstate & curses.BUTTON1_DOUBLE_CLICKED != 0:
                    buttons |= MouseEvent.DOUBLE_CLICK
                return MouseEvent(x, y, buttons)
            else:
                # Handle a genuine key press.
                if key in self._KEY_MAP:
                    return KeyboardEvent(self._KEY_MAP[key])
                elif key != -1:
                    return KeyboardEvent(key)
            return None

        def has_resized(self):
            """
            Check whether the screen has been re-sized.
            """
            re_sized = self._re_sized
            self._re_sized = False
            return re_sized

        def _change_colours(self, colour, attr, bg):
            """
            Change current colour if required.

            :param colour: New colour to use.
            :param attr: New attributes to use.
            :param bg: New background colour to use.
            """
            # Change attribute first as this will reset colours when swapping
            # modes.
            if attr != self._attr:
                sys.stdout.write(self._a_normal)
                if attr != 0:
                    sys.stdout.write(self._ATTRIBUTES[attr])
                self._attr = attr
                self._colour = None
                self._bg = None

            # Now swap colours if required.
            if colour != self._colour:
                sys.stdout.write(curses.tparm(self._fg_color, colour))
                self._colour = colour
            if bg != self._bg:
                sys.stdout.write(curses.tparm(self._bg_color, bg))
                self._bg = bg

        def _print_at(self, text, x, y):
            """
            Print string at the required location.

            :param text: The text string to print.
            :param x: The x coordinate
            :param y: The Y coordinate
            """
            # Move the cursor if necessary
            msg = ""
            if x != self._x or y != self._y:
                msg += curses.tparm(self._move_y_x, y, x)

            msg += text

            # Print the text at the required location and update the current
            # position.
            sys.stdout.write(msg)

    class _BlessedScreen(_BufferedScreen):
        """
        Blessed screen implementation.  This is deprecated as it doesn't support
        mouse input.
        """

        #: Conversion from Screen attributes to blessed equivalents.
        ATTRIBUTES = {
            Screen.A_BOLD: lambda term: term.bold,
            Screen.A_NORMAL: lambda term: "",
            Screen.A_REVERSE: lambda term: term.reverse,
            Screen.A_UNDERLINE: lambda term: term.underline
        }

        def __init__(self, terminal, height):
            """
            :param terminal: The blessed Terminal object.
            :param height: The buffer height for this window (if using
                scrolling).
            """
            # Save off the screen details and se up the scrolling pad.
            super(_BlessedScreen, self).__init__(
                terminal.height, terminal.width, height)

            # Save off terminal.
            self._terminal = terminal

            # Set up basic colour schemes.
            self.colours = terminal.number_of_colors

            # Set up signal handler for screen resizing.
            self._re_sized = False
            signal.signal(signal.SIGWINCH, self._resize_handler)

        def _resize_handler(self, *_):
            """
            Window resize signal handler.  We don't care about any of the
            parameters passed in beyond the object reference.
            """
            self._re_sized = True

        def refresh(self):
            """
            Refresh the screen.
            """
            # Flush screen buffer to get all updates after doing the common
            # processing.  Exact timing of the signal can interrupt the
            # flush, raising an EINTR IOError, which we can safely ignore.
            super(_BlessedScreen, self).refresh()
            try:
                sys.stdout.flush()
            except IOError:
                pass

        def get_event(self):
            """
            Check for any event without waiting.

            .. warning::

                Blessed does not support mouse events.
            """
            key = self._terminal.inkey(timeout=0)
            return KeyboardEvent(ord(key)) if key != "" else None

        def has_resized(self):
            """
            Check whether the screen has been re-sized.
            """
            re_sized = self._re_sized
            self._re_sized = False
            return re_sized

        def _change_colours(self, colour, attr, bg):
            """
            Change current colour if required.

            :param colour: New colour to use.
            :param attr: New attributes to use.
            :param bg: New background colour to use.
            """
            # Change attribute first as this will reset colours when swapping
            # modes.
            if attr != self._attr:
                sys.stdout.write(
                    self._terminal.normal + self._terminal.on_color(0))
                if attr != 0:
                    sys.stdout.write(self.ATTRIBUTES[attr](self._terminal))
                self._attr = attr
                self._colour = None

            # Now swap colours if required.
            if colour != self._colour:
                sys.stdout.write(self._terminal.color(colour))
                self._colour = colour
            if bg != self._bg:
                sys.stdout.write(self._terminal.on_color(bg))
                self._bg = bg

        def _print_at(self, text, x, y):
            """
            Print string at the required location.

            :param text: The text string to print.
            :param x: The x coordinate
            :param y: The Y coordinate
            """
            # Move the cursor if necessary
            msg = ""
            if x != self._x or y != self._y:
                msg += self._terminal.move(y, x)

            msg += text

            # Print the text at the required location and update the current
            # position.
            sys.stdout.write(msg)
            self._x = x + len(text)
            self._y = y

        def _scroll(self):
            """
            Scroll up by one line.
            """
            print(self._terminal.move(self.height - 1, 0))

        def _clear(self):
            """
            Clear the terminal.
            """
            sys.stdout.write(self._terminal.clear())
