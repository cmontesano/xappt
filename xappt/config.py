import logging
import os

from xappt.constants import APP_NAME, DEBUG_FLAG_ENV

log = logging.getLogger(APP_NAME)
log.setLevel(logging.WARN)
sh = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)8s] %(name)s : %(message)s")
sh.setFormatter(formatter)
sh.setLevel(logging.WARN)
log.addHandler(sh)

if os.environ.get(DEBUG_FLAG_ENV, "0") != "0":
    sh.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
