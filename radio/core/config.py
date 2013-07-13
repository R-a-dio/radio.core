from __future__ import absolute_import
from __future__ import unicode_literals
import io

import kaptan


def load_configuration(config, filename):
    """
    Loads a configuration file specified by `filename`
    with the help of the kaptan library.

    This assumes the file is encoded as UTF-8.

    :returns: :class:`kaptan.Kaptan` instance.
    :raises: Any errors from `io.open` and `import_config`.
    """
    with io.open(filename, "r", encoding="utf8") as f:
        config.import_config(f.read())
    return config


def create_configuration(filename=None):
    """
    Creates a Configuration instance, this can be passed to load_configuration
    together with a filename to load a configuration file.
    """
    c = kaptan.Kaptan(handler="yaml")
    if filename is not None:
        load_configuration(c, filename)
    return c
