import os
from xappt.constants import LOAD_EXAMPLES_ENV

if os.environ.get(LOAD_EXAMPLES_ENV, "0") != "0":
    from xappt.plugins.tools.examples import *
