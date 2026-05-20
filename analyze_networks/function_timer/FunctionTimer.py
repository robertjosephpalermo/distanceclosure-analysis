import time 
import psutil
import platform
import uuid
import sys
import json
from functools import wraps


class FunctionTimer:
    def __init__(self):
        self.json_log = []

    def json_dump(self):
        print(json.dumps(self.json_log, indent=2))

    def _jsv(self, value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return repr(value)

    def __call__(self, func):
        
        @wraps(func)
        def wrapped(*args, **kwargs):
            t_0 = time.perf_counter_ns()
            out = func(*args, **kwargs)
            dt_ns = time.perf_counter_ns() - t_0

            self.json_log.append({
                "run_log": {
                    "run_id": str(uuid.uuid4()),
                    "function": func.__name__,
                    "args": {
                        str(i): self._jsv(v)
                        for i, v in enumerate(args)
                    },
                    "kwargs": {
                        str(k): self._jsv(v)
                        for k, v in kwargs.items()
                    },
                    "runtime_in_nanoseconds": dt_ns,
                    "runtime_in_seconds": dt_ns / 1e9,
                    "runtime_in_minutes": dt_ns / 6e10
                },
                "system_log": {
                    "python_version": sys.version,
                    "python_implementation": platform.python_implementation(),
                    "os": platform.system(),
                    "os_release": platform.release(),
                    "os_version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "cpu_cores_physical": psutil.cpu_count(logical=False),
                    "cpu_cores_logical": psutil.cpu_count(logical=True),
                    "ram_gb": round(psutil.virtual_memory().total / 1e9, 2),
                }
            })
            return out
        
        return wrapped