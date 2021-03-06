# env.bash

# This file should help me set some env variables.
# I intend to 'dot' this file, not run it.
# Demo:
# . env.bash

export PGURL='postgres://tkrapi:tkrapi@127.0.0.1/tkrapi'
export PYTHON=${HOME}/anaconda3/bin/python
export PARPATH=${HOME}/tkrapi20
export PYTHONPATH=${PARPATH}/py
export SCRIPTPATH=${PARPATH}/bin
export TKRCSV=${HOME}'/tkrcsv'
export TKRCSVD=${TKRCSV}'/div'
export TKRCSVH=${TKRCSV}'/history'
export TKRCSVS=${TKRCSV}'/split'
export FLASK_DEBUG=1
export PORT=5011
export KERAS_BACKEND=tensorflow
export PATH=${HOME}/anaconda3/bin:$PATH
