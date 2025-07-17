# Copyright (c) 2025 Muad Bohmosh
#
# This file is part of the MTFIFO project.
# Released under the MIT License.
# See LICENSE file in the root of this repository for full license text.


import threading
import queue
import time

class MTFIFO:
    def __init__(self, options):
        if 'THREADS' not in options:
            raise ValueError("THREADS param must be defined")

        self.THREADS = options['THREADS']
        self.thread_count = len(self.THREADS)

        self.BUSY_THREADS = []  # list of dicts: {'index': int, 'request': dict}
        self.UNHANDLED = queue.Queue()  # holds request dicts: {'params': any, 'func': callable}

        # Callbacks
        self.request_success_callback = lambda response: print("request_handled", response)
        self.request_error_callback = lambda response: print("error", response)
        self.request_END_callback = lambda: print("all requests are handled")

        self.running = False
        self._intervalMs = 50  # polling interval in ms
        self.lock = threading.Lock()  # for thread-safe operations
        self.dispatcher_thread = None

    '''
      * Register event callbacks:
      *  'SUCCESS' => on each request's successfull completion
      *  'ERROR'   => on each request's failed completion
      *  'END'     => when queue drains
    '''

    def on(self, event, callback):
        event = event.upper()
        if event == 'SUCCESS':
            self.request_success_callback = callback
        elif event == 'ERROR':
            self.request_error_callback = callback
        elif event == 'END':
            self.request_END_callback = callback


    '''
      * Add one or more treads: function
      * @param {Array|function} Threads
    '''

    def add_threads(self, Threads):
        if not isinstance(Threads, list):
            Threads = [Threads]

        for t in Threads:
            if t and callable(t):
                self.THREADS.put(t)


    '''
      * Add one or more requests: { params: any, func: (params)=>Promise }
      * @param {Array|Object} reqs
    '''

    def add_requests(self, reqs):
        if not isinstance(reqs, list):
            reqs = [reqs]

        for r in reqs:
            if r and callable(r.get('func')):
                self.UNHANDLED.put(r)

        if not self.running:
            self.Start()


    '''
      * Get array of free thread threads.
    '''

    def get_free_threads(self):
        with self.lock:
            busy_indices = [b['index'] for b in self.BUSY_THREADS]
            return [i for i in range(self.thread_count) if i not in busy_indices]


    '''
      * Internal: assign a request to a thread and handle completion.
    '''

    def handle_request(self, request, thread_idx):
        # Mark thread as busy
        with self.lock:
            self.BUSY_THREADS.append({'index': thread_idx, 'request': request})

        # Execute request in a new thread
        def worker():
            try:
                # Call thread function with request
                result = self.THREADS[thread_idx](request)
                self.request_success_callback(result)
            except Exception as e:
                self.request_error_callback({'req': request, 'error': e})
            finally:
                # Free the thread
                with self.lock:
                    self.BUSY_THREADS = [b for b in self.BUSY_THREADS if b['index'] != thread_idx]
                self.checkIfDone()

        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()


    '''
      * once no requests are left to handle
    '''

    def checkIfDone(self):
        with self.lock:
            unhandled_empty = self.UNHANDLED.empty()
            busy_empty = len(self.BUSY_THREADS) == 0

        if unhandled_empty and busy_empty:
            self.Stop()
            self.request_END_callback()


    '''
      * Start processing the queue. Polls every _intervalMs ms for free threads.
    '''

    def Start(self):
        if self.running:
            return

        self.running = True

        def dispatcher_loop():
            while self.running:
                time.sleep(self._intervalMs / 1000.0)  # Convert ms to seconds

                free_threads = self.get_free_threads()
                if not free_threads or self.UNHANDLED.empty():
                    continue

                # Assign requests FIFO style
                for idx in free_threads:
                    if self.UNHANDLED.empty():
                        break
                    request = self.UNHANDLED.get()
                    self.handle_request(request, idx)

        self.dispatcher_thread = threading.Thread(target=dispatcher_loop)
        self.dispatcher_thread.daemon = True
        self.dispatcher_thread.start()


    '''
      * Stop the scheduler.
    '''

    def Stop(self):
        if self.running:
            self.running = False
            if self.dispatcher_thread and self.dispatcher_thread.is_alive():
                self.dispatcher_thread.join(timeout=1.0)
            self.dispatcher_thread = None


'''
# Example Usage
if __name__ == "__main__":
    import random

    def test_req_handling_function(params):
        print(f"----------------------\nSTARTED {params['text']}")
        time.sleep(1 + random.random() * 2)  # Simulate work
        print(f"----------------------\nFINISHED {params['text']}")
        return params['text']

    # Generate requests
    REQUESTS = []
    for i in range(20):
        REQUESTS.append({
            'params': {'text': f"Sentence {i}"},
            'func': test_req_handling_function
        })

    THREADS_NUMBER = 5

    # Create thread handlers
    THREADS = []
    for _ in range(THREADS_NUMBER):
        def thread_func(request):
            return request['func'](request['params'])
        THREADS.append(thread_func)

    pool = MTFIFO({'THREADS': THREADS})
    RESPONSES = []

    # Setup callbacks
    pool.on('SUCCESS', lambda res: [print(f'done -> {res}'), RESPONSES.append(res)])
    pool.on('ERROR', lambda err: print(f'error -> {err}'))
    pool.on('END', lambda: [print(f'all done 🤘 {RESPONSES}'),
                            threading.Timer(10.0, lambda: pool.add_requests(REQUESTS)).start()])

    # Start processing
    pool.add_requests(REQUESTS)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pool.Stop()
'''
