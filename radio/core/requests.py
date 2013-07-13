from __future__ import unicode_literals
from __future__ import absolute_import
import math
import datetime

from . import events
from .cursor import Cursor
from .song import Song
from .queue import Queue, RequestSong


REQUEST_DELAY = datetime.timedelta(hours=1)


class RequestError(Exception):
    pass


def request(song, identifier):
    """
    Requests `song` under the `identifier`.

    if `song` is an integer it will be used as the track id to use.
    """
    if not isinstance(song, Song):
        song = Song(id=long(song))

    # Check if the song can be requested
    if not requestable(song):
        raise RequestError("You need to wait longer before"
                           "requesting this song.")

    # Check if the user is allowed to request
    if not can_request(identifier):
        raise RequestError("You need to wait longer before"
                            "requesting again.")

    queue = Queue()
    queue.put(RequestSong(song, identifier))

    # Update our time records, don't want unlimited requests.
    with Cursor() as cur:
        count = cur.execute(
            "UPDATE nickrequesttime SET time=NOW() WHERE ip=%s;",
            (identifier,),
        )
        if count == 0:
            cur.execute(
                "INSERT INTO nickrequesttime (ip) VALUES (%s);",
                (identifier,),
            )

    # Send a generic event for requests.
    events.send("song_request", song)

    return None


def can_request(identifier):
    """
    Checks if an identifier is allowed to request yet.

    :returns: True or False
    """
    with Cursor() as cur:
        cur.execute(
            "SELECT time FROM nickrequesttime WHERE host=%s"
            " LIMIT 1;",
            (identifier,),
        )

        for t, in cur:
            time = t
        else:
            time = datetime.datetime.min

        delta = datetime.datetime.now() - time

        return delta > REQUEST_DELAY
    return False


def requestable(song):
    """
    Helper function that returns True if the song given can be requested.
    """
    if song.id == 0:
        return False # song isn't in the db

    with Cursor() as cur:
        query = "SELECT `requestcount`, `usable` FROM `tracks` WHERE `id`=%s;"
        cur.execute(query, (self.id,))

        for count, usable in cur:
            if usable == 0:
                # Song isn't playable so we can't request it
                return False
        else:
            # We had no entry with that ID, can't play that what doesn't exist
            return False

    songdelay = calculate_delay(requestcount)

    now = time.time()
    if song.lp and songdelay > (now - song.lp):
        return False # the song delay has not passed for lp
    if song.lr and songdelay > (now - song.lr):
        return False # the song delay has not passed for lr
    return True


def calculate_delay(val):
    """
    Returns the amount of seconds to wait before this song is allowed to
    be played again. The amount of seconds is relative to the last time
    a song was played. This should be calculated by the caller.
    """
    # We have an upper bound for val
    if val > 30:
        val = 30

    if 0 <= val <= 7:
        return -11057 * val ** 2 + 172954 * val + 81720
    else:
        return long(599955 * math.exp(0.0372 * val) + 0.5)
