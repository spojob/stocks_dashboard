#!/usr/bin/env bash
script_dir=$( cd "$(dirname "$BASH_SOURCE")"; pwd -P )
python "$script_dir/src/main".py $*