
# Yeah. just used for ~~one~~ two boolean flags.
run = True

# Determines if proxies in nameTools preload contents when started.
preloadDicts = False


# Global run control value. Only used to stop running processes.
import multiprocessing
run_state         = multiprocessing.Value('i', 1)
agg_run_state     = multiprocessing.Value('i', 1)
job_run_state     = multiprocessing.Value('i', 1)
raw_job_run_state = multiprocessing.Value('i', 1)


db_imp_lock = multiprocessing.Lock()


# For synchronizing saving cookies to disk
cookie_lock  = multiprocessing.Lock()