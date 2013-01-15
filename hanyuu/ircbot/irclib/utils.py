from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
import re
import string

def parse_modes(string):
    """
    Returns a generator that yields tuples of (operator, mode)
    
    >>> list(parse_modes('+bbb-a'))
    [('+', 'b'), ('+', 'b'), ('+', 'b'), ('-', 'a')]
    
    """
    mode = None
    for char in string:
            if char in ('-', '+'):
                    mode = char
            elif mode is None:
                    raise TypeError("Invalid mode string.")
            else:
                    yield (mode, char)


def intertwine_modes(modes, targets):
    """
    :params modes: An iterator of (operator, mode) tuples as returned by :func:`parse_modes`
    :params targets: A list of equal size of the iterator.
    """
    # TODO: Actually implement this.
    # This might need to be moved to a server specific factory
    pass


_LOW_LEVEL_QUOTE = "\020"
_CTCP_LEVEL_QUOTE = "\134"
_CTCP_DELIMITER = "\001"

# Huh!?  Crrrrazy EFNet doesn't follow the RFC: their ircd seems to
# use \n as message separator!  :P
_linesep_regexp = re.compile("\r?\n")

_low_level_mapping = {
    "0": "\000",
    "n": "\n",
    "r": "\r",
    _LOW_LEVEL_QUOTE: _LOW_LEVEL_QUOTE
}

_low_level_regexp = re.compile(_LOW_LEVEL_QUOTE + "(.)", re.UNICODE)

def mask_matches(nick, mask):
    """Check if a nick matches a mask.

    Returns true if the nick matches, otherwise false.
    """
    nick = irc_lower(nick)
    mask = irc_lower(mask)
    mask = mask.replace("\\", "\\\\")
    for ch in ".$|[](){}+":
        mask = mask.replace(ch, "\\" + ch)
    mask = mask.replace("?", ".")
    mask = mask.replace("*", ".*")
    r = re.compile(mask, re.IGNORECASE)
    return r.match(nick)

_special = "-[]\\`^{}"
nick_characters = string.ascii_letters + string.digits + _special
_ircstring_translation = string.maketrans(string.ascii_uppercase + "[]\\^",
                                        string.ascii_lowercase + "{}|~")

def irc_lower(s):
    """Returns a lowercased string.

    The definition of lowercased comes from the IRC specification (RFC
    1459).
    """
    if (type(s) == unicode):
        s = s.encode('utf-8')
    return s.translate(_ircstring_translation)

def _ctcp_dequote(message):
    """[Internal] Dequote a message according to CTCP specifications.

    The function returns a list where each element can be either a
    string (normal message) or a tuple of one or two strings (tagged
    messages).  If a tuple has only one element (ie is a singleton),
    that element is the tag; otherwise the tuple has two elements: the
    tag and the data.

    Arguments:

        message -- The message to be decoded.
    """

    def _low_level_replace(match_obj):
        ch = match_obj.group(1)

        # If low_level_mapping doesn't have the character as key, we
        # should just return the character.
        return _low_level_mapping.get(ch, ch)

    if _LOW_LEVEL_QUOTE in message:
        # Yup, there was a quote.  Release the dequoter, man!
        message = _low_level_regexp.sub(_low_level_replace, message)

    if _CTCP_DELIMITER not in message:
        return [message]
    else:
        # Split it into parts.  (Does any IRC client actually *use*
        # CTCP stacking like this?)
        chunks = message.split(_CTCP_DELIMITER)

        messages = []
        i = 0
        while i < len(chunks)-1:
            # Add message if it's non-empty.
            if len(chunks[i]) > 0:
                messages.append(chunks[i])

            if i < len(chunks)-2:
                # Aye!  CTCP tagged data ahead!
                messages.append(tuple(chunks[i+1].split(" ", 1)))

            i = i + 2

        if len(chunks) % 2 == 0:
            # Hey, a lonely _CTCP_DELIMITER at the end!  This means
            # that the last chunk, including the delimiter, is a
            # normal message!  (This is according to the CTCP
            # specification.)
            messages.append(_CTCP_DELIMITER + chunks[-1])

        return messages

def is_channel(string, chan_prefixes='#&+!'):
    """Check if a string is a channel name.

    Returns true if the argument is a channel name, otherwise false.
    """
    return string and string[0] in (chan_prefixes or "#&+!")

def ip_numstr_to_quad(num):
    """Convert an IP number as an integer given in ASCII
    representation (e.g. '3232235521') to an IP address string
    (e.g. '192.168.0.1')."""
    n = long(num)
    p = map(str, map(int, [n >> 24 & 0xFF, n >> 16 & 0xFF,
                           n >> 8 & 0xFF, n & 0xFF]))
    return ".".join(p)

def ip_quad_to_numstr(quad):
    """Convert an IP address string (e.g. '192.168.0.1') to an IP
    number as an integer given in ASCII representation
    (e.g. '3232235521')."""
    p = map(long, quad.split("."))
    s = str((p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3])
    if s[-1] == "L":
        s = s[:-1]
    return s

def nm_to_n(s):
    """Get the nick part of a nickmask.

    (The source of an Event is a nickmask.)
    """
    return s.split("!")[0]

def nm_to_uh(s):
    """Get the userhost part of a nickmask.

    (The source of an Event is a nickmask.)
    """
    return s.split("!")[1]

def nm_to_h(s):
    """Get the host part of a nickmask.

    (The source of an Event is a nickmask.)
    """
    return s.split("@")[1]

def nm_to_u(s):
    """Get the user part of a nickmask.

    (The source of an Event is a nickmask.)
    """
    s = s.split("!")[1]
    return s.split("@")[0]


def _parse_modes(mode_string, always_param='beIkqaohv', set_param='l', no_param='BCMNORScimnpstz'):
    """
    This function parses a mode string based on a set of mode types.
    It returns a list of tuples like (prefix, mode, parameter), where
    prefix is either + or -, mode is a character that specifies a mode,
    and parameter is an optional parameter to the mode. If no parameter
    was specified, the value is None.
    
    always_param contains the modes that always have a parameter, both
    when they are set and unset.
    
    set_param contains modes that have a parameter when they are set.
    
    no_param contains modes that do not have a parameter.
    
    The default values are taken from Rizon's ircd.
    """
    
    
    modes = []
    sign = ''
    param_index = 0;
    
    split = mode_string.split()
    if len(split) == 0:
        return []
    else:
        mode_part, args = split[0], split[1:]
    
    if mode_part[0] not in "+-":
        return []
    
    for ch in mode_part:
        if ch in "+-":
            sign = ch
        elif (ch in always_param) or (ch in set_param and sign == '+'):
            if param_index < len(args):
                modes.append((sign, ch, args[param_index]))
                param_index += 1
            else:
                modes.append((sign, ch, None))
        else: # assume that any unknown mode is no_param
            modes.append((sign, ch, None))
    return modes