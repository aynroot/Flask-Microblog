# -*- coding: utf-8 -*-s
import os.path


# general application settings
WTF_CSRF_ENABLED = True
SECRET_KEY = '9b7f09b5-8159-4b64-8d28-5809daec63f3'

# db settings
basedir = os.path.dirname(__file__)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

WHOOSH_BASE = os.path.join(basedir, 'search.db')

# debug settings
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

# languages settings
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский'
}

# app settings
POSTS_PER_PAGE = 3
MAX_SEARCH_RESULTS = 10