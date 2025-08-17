import logging, os, sys
def get_logger(name="app", level=None):
    lvl = level or os.environ.get("LOG_LEVEL","INFO").upper()
    logging.basicConfig(level=getattr(logging,lvl,logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)])
    return logging.getLogger(name)
