#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = 'http://kele.codes'
RELATIVE_URLS = True

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/%s.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

DISQUS_SITENAME = "kele-github-io"

PLUGIN_PATHS = ['/usr/lib/python3.6/site-packages/pelican/pelican-plugins']
PLUGINS = ['i18n_subsites']

I18N_SUBSITES = {
    'en': { }
}
