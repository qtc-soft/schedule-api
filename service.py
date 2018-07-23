import asyncio
import uvloop
from settings import *

from multiprocessing import Process
import signal

from main import main


# handler by signal
def signal_handler(processes):
    pass
    # for process in processes:
        #process.terminate()
        # process.join()


if __name__ == "__main__":
    # init logging system
    init_logging('service_', True)
    # process settings file
    init_settings()

    # set uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # set signal for close sub-processes
    signal.signal(signal.SIGINT, lambda num, handler: signal_handler(processes))
    signal.signal(signal.SIGTERM, lambda num, handler: signal_handler(processes))

    # create web-api sub-processes
    count_processes = int(config.get("SERVICE", "count_processes"))
    processes = [Process(
        target=main,
        kwargs=dict(prefix_name='{}-{}'.format(config.get("SERVICE", "name", fallback='mgate0'), i+1)),
        name='web_api %{}'.format(i+1),
    ) for i in range(count_processes)]

    # start web-api sub-processes
    for process in processes:
        process.daemon = True
        process.start()

    # processes.join
    for process in processes:
        process.join()
