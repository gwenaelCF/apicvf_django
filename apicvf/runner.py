from django.test.runner import DiscoverRunner
from django.test import utils

class CustomRunner(DiscoverRunner):
    utils.setup_databases(
    	verbosity=2, interactive=True, keepdb=True, aliases='test')
        