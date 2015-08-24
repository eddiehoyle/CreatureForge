#!/usr/bin/env bash

realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}

root=$(realpath $(dirname $(pwd)))

export CREATUREFORGE_ROOT=$root
export PYTHONPATH=$root/pylib
source $root/.env/bin/activate

exec $root/tests/test_pylib/runtests.py $@ --verbose