#!/bin/sh

set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

# Setup Python virtualenv if necessary
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

export PROMETHEUS_MULTIPROC_DIR=/tmp
export APP_LOG_LEVEL=DEBUG
export WERKZEUG_LOG_LEVEL=WARNING

FLASK_DEBUG=True flask run
