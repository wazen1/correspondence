# -*- coding: utf-8 -*-
# Copyright (c) 2025, ERP Team and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

# Import new utilities for version 1.0.1
try:
	from .digital_signature import *
	from .barcode_qr import *
	from .ml_analytics import *
	from .voice_to_text import *
except ImportError:
	# Dependencies might not be installed yet or bench needs restart
	pass
