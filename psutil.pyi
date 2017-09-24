from typing import NamedTuple, Union, Text, Sequence, IO, Any, Optional, List, Callable, Tuple

_FILE = Union[None, int, IO[Any]]
_TXT = Union[bytes, Text]
_CMD = Union[_TXT, Sequence[_TXT]]

pcputimes = NamedTuple('pcputimes', [('user', float)])
pmem = NamedTuple('pmem', [('rss', int)])

class Process:
	returncode: Optional[int]
	stdin: _FILE
	stdout: _FILE
	stderr: _FILE

	def is_running(self) -> bool: ...
	def terminate(self) -> None: ...
	def cpu_times(self) -> pcputimes: ...
	def memory_info(self) -> pmem: ...

def Popen(args: _CMD,
	stdin: _FILE = ...,
	stdout: _FILE = ...,
	stderr: _FILE = ...
) -> Process: ...
def wait_procs(procs: List[Process], timeout: Optional[float] = ..., callback: Optional[Callable[[Process], None]] = ...) -> Tuple[List[Process], List[Process]]: ...

class Error(Exception): ...
class AccessDenied(Exception): ...
class TimeoutExpired(Error): ...
class NoSuchProcess(Error): ...
