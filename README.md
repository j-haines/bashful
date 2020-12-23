# bashful

`bashful` provides streamlined execution of Bash pipelines from Python. It's useful for quickly rewriting complex Bash scripts in Python, but probably just shouldn't be used.

Only tested with Python 3.8.

## Examples

### Single bash command

```lang=python
In [1]: from bashful import bash

In [2]: ls = bash("ls", "-a", "/etc/systemd")

In [3]: proc = ls()

In [4]: print(proc.stdout.decode("utf-8"))
.
..
coredump.conf
journald.conf
logind.conf
resolved.conf
system
system.conf
user
user.conf
```

### Piping multiple bash commands

```lang=python
In [1]: from bashful import bash

In [2]: pipelined = bash("ls", "/var/log") | bash("wc", "-l")

In [3]: proc = pipelined()

In [4]: print(proc.stdout.decode("utf-8"))
59
```

### ... or as a single function call

```lang=python
In [1]: from bashful import pipeline

In [2]: pipelined = pipeline(["ls", "/var/log"], ["wc", "-l"])

In [3]: proc = pipelined()

In [4]: print(proc.stdout.decode("utf-8"))
59
```

### Passing input to commands

```lang=python
In [1]: from bashful import bash

In [2]: wc = bash("wc", "-c")

In [3]: proc = wc("abcdefh")

In [4]: print(proc.stdout.decode("utf-8"))
7
```
