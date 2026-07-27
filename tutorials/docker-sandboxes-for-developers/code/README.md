# Sandbox Demo Server

A dependency-free Python HTTP server used by the Docker Sandboxes lesson.

## Run the tests

```bash
python3 -m unittest -v
```

## Run the server

On the host:

```bash
python3 server.py
curl http://127.0.0.1:3000/
```

Inside a sandbox, listen on all IPv4 interfaces before publishing the port:

```bash
python3 server.py --host 0.0.0.0 --port 3000
```

## Reset

The lesson creates a disposable copy of this directory with `mktemp`. Delete that temporary directory and create another copy to reset the demo.
