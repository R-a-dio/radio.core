from __future__ import absolute_import
from __future__ import unicode_literals

from .config import load_configuration
from .events import Registrar

config = load_configuration("radio.conf.yaml")

events = Registrar()
