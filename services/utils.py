from services.log import log
import random
from time import sleep

def api_sleep(is_retry = False):
    t = random.uniform(1.5, 2.8)
    log.debug(f":zzz:{' :arrows_counterclockwise:' if is_retry else ''} Sleeping for {round(t, 2)} seconds{' (retry)' if is_retry else ''}")
    sleep(t)

