from __future__ import unicode_literals
from __future__ import absolute_import
from collections import namedtuple
import time

from .song import Song
from .cursor import Cursor


# Small wrapper around a Song instance to differentiate.
RequestSong = namedtuple("RequestSong", ("song", "requester"))


class Queue(object):
    REGULAR = 0
    REQUEST = 1
    POPPED = 2

    @staticmethod
    def _calculate_timestamp():
        with Cursor() as cur:
            cur.execute(
                "SELECT sum(unix_timestamp(time) - unix_timestamp())"
                    " + unix_timestamp() FROM queue;",
            )

            for timestamp, in cur:
                return timestamp
            return long(time.time())

    def put(self, song):
        """
        Put a new song on the queue, if the song should be registered
        as a request, it should be wrapped in a :class:`RequestSong`
        before passing it to :meth:`put`.
        """
        if isinstance(song, RequestSong):
            type = Queue.REQUEST
            # RequestSong has our actual Song instance inside. Pull it out
            request = song
            song = song.song
        else:
            type = Queue.REGULAR

        estimated_play_time = self._calculate_timestamp()

        parameters = [
            song.id,
            estimated_play_time,
            request.requester,
            type,
            song.meta,
            song.length,
        ]

        with Cursor() as cur:
            cur.execute(
                "INSERT INTO queue (trackid, time, ip, type, meta, length) "
                    "VALUES (%s, from_unixtime(%s), %s, %s, %s, %s, %s);",
                parameters,
            )

    def pop(self):
        with Cursor() as cur:
            cur.execute(
                "SELECT id, trackid, meta, length FROM queue WHERE type "
                    "IN (%s, %s) ORDER BY time ASC LIMIT 1;",
                (Queue.REGULAR, Queue.REQUEST),
            )

            song = None

            for id, track, meta, length in cur:
                song = Song(track, meta, length)

                cur.execute(
                    "UPDATE queue SET type=%s WHERE id=%s;",
                    (Queue.POPPED, id),
                )

                return song

    def peek(self):
        with Cursor() as cur:
            cur.execute(
                "SELECT trackid, meta, length FROM queue WHERE type "
                    "IN (%s, %s) ORDER BY time ASC LIMIT 1;",
                (Queue.REGULAR, Queue.REQUEST),
            )
            for id, meta, length in cur:
                return Song(id, meta, length)

    def __len__(self):
        with Cursor() as cur:
            cur.execute("SELECT count(*) FROM `queue`;")
            for count, in cur:
                return int(count)
            return 0
