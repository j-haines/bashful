import os
import subprocess
import sys
from io import BufferedIOBase
from typing import AnyStr, Callable, Iterable, Optional, Tuple, Union


Pipelinable = Union["Bash", "Pipeline"]


class Bash:
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        self._cmd = [*args]
        self._proc = subprocess.Popen(
            self._cmd,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            **kwargs,
        )

    def __or__(self, rhs: Pipelinable) -> Pipelinable:
        return Pipeline(self, rhs)

    def __call__(self, input_: Optional[AnyStr] = None) -> subprocess.CompletedProcess:
        stdout, stderr = self._proc.communicate(_ensure_bytes(input_))

        proc: subprocess.CompletedProcess = subprocess.CompletedProcess(
            self._cmd,
            self._proc.returncode,
            stdout=stdout,
            stderr=stderr,
        )
        return proc

    def communicate(self, input_: Optional[AnyStr] = None) -> Tuple[str, str]:
        proc = self(_ensure_bytes(input_))
        return (
            proc.stdout.decode("unicode_escape"),
            proc.stderr.decode("unicode_escape"),
        )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return " ".join(self._cmd)


class Pipeline:
    def __init__(
        self,
        lhs: Pipelinable,
        rhs: Pipelinable,
    ) -> None:
        self._lhs = lhs
        self._rhs = rhs

    def __or__(self, rhs: Pipelinable) -> Pipelinable:
        return Pipeline(self, rhs)

    def __call__(self, input_: Optional[AnyStr] = None) -> subprocess.CompletedProcess:
        lhs = self._lhs(input_)
        rhs = self._rhs(lhs.stdout)
        return rhs

    def communicate(self, input_: Optional[AnyStr] = None) -> Tuple[str, str]:
        proc = self(input_)
        return (
            proc.stdout.decode("unicode_escape").rstrip(),
            proc.stderr.decode("unicode_escape").rstrip(),
        )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self._lhs} | {self._rhs}"


def _ensure_bytes(s: Optional[AnyStr]) -> Optional[bytes]:
    if s is None:
        return None

    if isinstance(s, bytes):
        return s

    return s.encode("utf-8")


def bash(*args, **kwargs):
    return Bash(
        *args,
        **kwargs,
    )


def pipeline(*args: Iterable[str], **kwargs):
    procs = [bash(*arg, **kwargs) for arg in args]

    if len(procs) == 1:
        return procs[0]

    tail = procs[0]
    pipeline = procs[0] | procs[1]
    for proc in procs[2:]:
        pipeline = pipeline | proc

    return pipeline


if __name__ == "__main__":
    pipeline = bash("ls", "-la", "/etc") | bash("grep", "rc") | bash("sed", "s/rc$//")
    proc = pipeline()
    print(f"{proc.stdout.decode('unicode_escape')}")
