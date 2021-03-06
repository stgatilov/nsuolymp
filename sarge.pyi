from typing import NamedTuple, IO, Optional, Any

Pipeline = NamedTuple('Pipeline', [('returncode', int)])
def run(cmd: str, input: Optional[IO[Any]] = ...) -> Pipeline: ...
def capture_both(cmd: str, input: Optional[IO[Any]] = ...) -> Pipeline: ...
def capture_stderr(cmd: str, input: Optional[IO[Any]] = ...) -> Pipeline: ...
