# -*- encoding: utf-8 -*-
from __future__ import absolute_import

import sys
import logging

logger = logging.getLogger('SlackApp')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)
