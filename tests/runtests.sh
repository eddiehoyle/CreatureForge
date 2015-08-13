#!/usr/bin/env bash

script_dir=`dirname $0`
source $script_dir/../.env/bin/activate
export CREATUREFORGE_ROOT="/Users/eddiehoyle/Code/python/creatureforge/"
exec $script_dir/test_pylib/runtests.py --verbose
# exec nosetests -v