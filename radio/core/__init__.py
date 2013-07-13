from __future__ import absolute_import
from __future__ import unicode_literals

from .config import load_configuration


config = load_configuration("hanyuu.conf.yaml")

events = EventRegistrar()
