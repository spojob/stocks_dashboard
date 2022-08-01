#!/usr/bin/env bash
script_dir=$( cd "$(dirname "$BASH_SOURCE")"; pwd -P )
python "$script_dir/src/main".py $*

gunicorn  -w 2 -k --chdir $script_dir/src/ -b 0.0.0.0:8080 app:app