# Use this module to test functions & run arbitrary scripts
#within the context of this application.
# The block below must not be removed and must come first before any imports.
print("Initializing script runner...", end="")
######################################################################
import os  #

import django  #

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hms_api_gateway.settings")   #
django.setup()                                                       #
######################################################################


print("Finished running script")