import threading
import time

from mtfifo import MTFIFO

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
