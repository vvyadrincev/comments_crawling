#!/usr/bin/env python
# coding: utf-8

import time
import logging
import multiprocessing
import random

class Worker(multiprocessing.Process):
    def __init__(self, queue, processor):
        super(Worker, self).__init__()
        self._queue = queue
        self._proc = processor

    def run(self):
        while True:
            item = self._queue.get()
            if item is None:
                return

            try:
                self._proc(item)
            except Exception as e:
                logging.exception("failed to process item '%s' : %s ", item, e)


class WorkerWithOutput(Worker):
    """ processor's class should have get_result method"""
    def __init__(self, queue, processor, out_queue):
        super(WorkerWithOutput, self).__init__(queue, processor)
        self._out_queue = out_queue

    def run(self):
        super(WorkerWithOutput, self).run()
        try:
            if hasattr(self._proc, "get_result"):
                self._out_queue.put(self._proc.get_result())
            else:
                self._out_queue.put(None)
        except Exception as e:
            logging.error("exception during result retrieval: %s ", e)
            self._out_queue.put(None)



def process_items_simulteaniously(opts, items_fetcher, processor):
    """opts should contain following fields:
            - proc_cnt - amount of processess
            - delay - delay between two sequantial processings
    If processor has get_result method, it is invoked for all workers in the end.
    Results are returned in the list.
    If there is no such a method, list of None is returned.
"""

    assert(opts.proc_cnt > 0)

    #to support legacy code, that pass list of processors
    if isinstance(processor, list):
        if processor:
            processor = processor[0]
        else:
            raise RuntimeError("Empty list detected instead of a processor. Pass one processor")

    queue = multiprocessing.Queue(1)
    out_queue = multiprocessing.Queue(opts.proc_cnt)

    workers_list = []
    for _ in range(opts.proc_cnt):
        w = WorkerWithOutput(queue, processor, out_queue)
        w.start()
        workers_list.append(w)

    logging.info("%d workers were created ", len(workers_list))

    for item in items_fetcher:
        queue.put( item )
        _sleep(opts.delay)

    for _ in range(opts.proc_cnt):
        queue.put( None )


    return [out_queue.get() for w in workers_list]

def _sleep(delay):
    if (isinstance(delay, (int, float))):
        d = delay
    elif len(delay) == 2:
        d = random.uniform(*delay) #get random float number between delay[0] and delay[1]
    else:
        logging.error("Incorrect format of 'delay' param")
        d = 0
    time.sleep(d)

######END MULTIProcessing utils#############
