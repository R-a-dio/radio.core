from __future__ import absolute_import
from __future__ import unicode_literals

from .config import load_configuration, create_configuration
from .events import Registrar


config = create_configuration()

def load(filename="radio.conf.yaml"):
    """
    Convenience function to load a configuration file.

    Calls :func:`radio.core.config.load_configuration` and returns the result
    while also setting the global variable `config` in :mod:`radio.core`.

    The usual usage of configuration access is by using the `config`
    global from :mod:`radio.core`.
    """
    load_configuration(config, filename)


events = Registrar()
