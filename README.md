# 🧠 MTFIFO: A Minimalist Multi-Threaded FIFO Orchestrator for AI (Python)

A lightweight thread-pool manager that schedules asynchronous task requests across a fixed number of worker callables, preserving FIFO ordering.

### 🚀 Ultra-Light. Super-Dynamic. Hardware-Aware.

---

## 🧩 What is MTFIFO?

**MTFIFO** is a blazing-fast, zero-dependency **multithreaded task orchestrator** for AI workloads ( or anything really ) — capable of:

* Running **multiple concurrent user requests**
* Spanning **multiple GPUs, CPUs, or TPUs**
* Maintaining **FIFO ordering** where needed
* Dynamically managing inference tasks with **fine-grained control**

Built from scratch with **minimal overhead** and full **hardware-awareness**, `MTFIFO` is ideal for **real-time inference pipelines** like:

* TTS
* LLM serving
* Custom AI agents
* Distributed multimodal tasks

---

## 🧠 Why It Matters

Modern AI workloads are:

* **Concurrent** (many users)
* **Heavy** (multi-GPU processing)
* **Dynamic** (varying task lengths)
* **Deterministic-demanding** (you want predictable output)

But existing solutions are:

* Too heavy (Ray, vLLM, Serve ... )
* Too static (fixed pipelines, no real-time routing)
* Not hardware-aware enough (especially for cross-GPU orchestration)

### `MTFIFO` solves this with:

✔️ **Minimalism** — No dependencies. Runs anywhere.
✔️ **Determinism** — Control over execution order, batching, and stream consistency.
✔️ **Performance** — Utilizes threading, queuing, and per-device workloads efficiently.
✔️ **Flexibility** — Drop in your own TTS/LLM/ML model and go.

---

## 🛠 Use Cases

* Multi-user **LLM inference server**
* Real-time **TTS generation backend**
* Distributed **multimodal agent pipeline**
* Low-latency **task routing engine** for any AI service
* user requests load orchestration

---

## 🛠 Built For Builders

This is for:

* Engineers building **self-hosted AI APIs**
* Researchers needing **deterministic inference**
* Makers tired of black-box schedulers

---

## 🧠 Overview

- You provide a list of thread functions (`THREADS`), each callable accepting a request `dict` and returning a result.
- Requests are dictionaries containing:
  - `params`: input data for the task
  - `func`: a callable to execute with the given params
- MTFIFO dispatches requests to free threads as soon as possible.
- Completion and error callbacks are supported.
- The dispatcher polls periodically for free threads and assigns tasks.
- When all tasks are done, an optional `"END"` callback is triggered.

---

## ✅ Features

- Maintains FIFO task order
- Supports dynamic addition of worker threads and tasks
- Handles concurrent execution with thread safety
- Event-driven callbacks: `"SUCCESS"`, `"ERROR"`, and `"END"`

---

## 📦 Installation

Clone this repository:

```bash
git clone https://github.com/Muad-Bohmosh/mtfifo-py.git
cd mtfifo-py
````

Then import `MTFIFO` from `mtfifo.py` in your project.

---

## 🧩 Class API

### `__init__(options)`

* **Parameters:**

  * `options`: dict with key `"THREADS"`: a list of callable thread functions.
* **Raises:**

  * `ValueError` if `"THREADS"` key is missing.
* **Behavior:**

  * Initializes thread pool size, internal queues, callbacks, and synchronization primitives.

---

### `on(event_name: str, callback: callable)`

* Registers event callbacks. Supported events:

  * `"SUCCESS"` — called with result of successful task
  * `"ERROR"` — called with dict containing `req` and `error`
  * `"END"` — called when all tasks have been processed

```python
pool.on('SUCCESS', lambda res: print("Task done:", res))
```

---

### `add_requests(reqs: list | dict)`

* Adds one or more requests to the queue.
* Each request must be a dict containing:

  * `'params'`: input data
  * `'func'`: callable task function
* Automatically starts the scheduler if not already running.

```python
pool.add_requests([
    {'params': {...}, 'func': callable_func},
    {'params': {...}, 'func': callable_func},
])
```

---

### `add_threads(Threads: list | function)`

* Dynamically adds one or more worker functions to the thread pool.
* Each thread must be a callable that accepts a request dict and returns a result.

```python
def thread_func(request):
    return request['func'](request['params'])

pool.add_threads([thread_func])
```

---

### `Start()`

* Starts the dispatcher thread.
* Periodically polls every `_intervalMs` milliseconds (default: 50ms).
* Assigns requests to free threads in FIFO order.

---

### `Stop()`

* Gracefully stops the dispatcher thread.
* Waits briefly for it to exit.

---

## 🔧 Internal Methods

* `get_free_threads() -> list[int]` — Returns list of free thread indices
* `handle_request(request: dict, thread_idx: int)` — Executes a task on the given thread, manages success/error callbacks
* `checkIfDone()` — Called after each task completes; stops dispatcher if no tasks remain

---

## 🧪 Example Usage

```python
import time
import random

def test_req_handling_function(params):
    print(f"STARTED: {params['text']}")
    time.sleep(1 + random.random() * 2)  # Simulate work
    print(f"FINISHED: {params['text']}")
    return params['text']

# Generate 20 requests
REQUESTS = [{'params': {'text': f"Sentence {i}"}, 'func': test_req_handling_function} for i in range(20)]

# Worker threads
THREADS = []
for _ in range(5):
    def thread_func(request):
        return request['func'](request['params'])
    THREADS.append(thread_func)

# Initialize pool
from mtfifo import MTFIFO
pool = MTFIFO({'THREADS': THREADS})
RESPONSES = []

# Setup event hooks
pool.on('SUCCESS', lambda res: [print(f'DONE -> {res}'), RESPONSES.append(res)])
pool.on('ERROR', lambda err: print(f'ERROR -> {err}'))
pool.on('END', lambda: print(f'ALL DONE 🤘 {RESPONSES}'))

# Start tasks
pool.add_requests(REQUESTS)

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pool.Stop()
```

---

## 📦 Wanna contribute fast ?

* More examples (simple projects)
* Web Ui dashboard for task visualization

## hardcore

* Web dashboard for task monitoring
* Example project templates (LLMs, TTS, agents)

---

## 📣 Claim It, Fork It, Use It

> Like everything else, I Built it Because I Needed it.

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.

---

Contributions welcome. — thanks in advance!
