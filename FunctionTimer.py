import time 
import psutil
import platform
import uuid
import sys
import json


class FunctionTimer:
    def __init__(self, module):
        self._module = module
        self.json_log = []
    
    def json_dump(self):
        print(json.dumps(self.json_log, indent=2))

    def _jsv(self, value):
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return repr(value)

    def __getattr__(self, name):
        func = getattr(self._module, name)

        def wrapped(*args, **kwargs):
            t_0 = time.perf_counter()
            out = func(*args, **kwargs)
            dt = time.perf_counter() - t_0
            
            self.json_log.append({
                    "run_log": { 
                        "run_id": str(uuid.uuid4()),
                        "function": f"{str(self._module.__name__)}.{name}",
                        "args": {self._jsv(i): self._jsv(v) for i, v in enumerate(args)},
                        "kwargs": {self._jsv(k): self._jsv(v) for k, v in kwargs.items()},
                        "runtime_in_seconds": dt,
                        "runtime_in_minutes": dt / 60
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
                }
            )

            return out 
        return wrapped