#!/usr/bin/env bash
script_dir=$( cd "$(dirname "$BASH_SOURCE")"; pwd -P )
gunicorn  -w 2 -k uvicorn.workers.UvicornWorker --chdir $script_dir/src/ -b 0.0.0.0:8000 app:app