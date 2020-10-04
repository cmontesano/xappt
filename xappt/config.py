import logging
import os

from xappt.constants import APP_NAME

log = logging.getLogger(APP_NAME)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)8s] %(name)s : %(message)s")
sh.setFormatter(formatter)
log.addHandler(sh)

if os.environ.get("XAPPT_DEBUG", "0") != "0":
    log.setLevel(logging.DEBUG)
