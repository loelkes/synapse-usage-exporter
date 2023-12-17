#!/bin/sh
# Run all scripts inside /docker-entrypoint.d/
set -e

SCRIPTS_DIR="/docker-entrypoint.d/"
RESULT=0

echo "INFO: Run /docker-entrypoint.sh"

if ! [ -d "${SCRIPTS_DIR}" ]; then
    echo "WARNING: ${SCRIPTS_DIR} doesn't exist"
    exit 1
else
    echo "INFO: Run scripts from ${SCRIPTS_DIR}"
    find "${SCRIPTS_DIR}" -type f -maxdepth 1 -iname '*.sh' -print | sort | while read -r SCRIPT_PATH; do
        if ! [ -x "${SCRIPT_PATH}" ]; then
            echo "WARNING: Skip ${SCRIPT_PATH} because it is not flagged as executable."
            continue
        fi
        echo "INFO: Run (cwd: $(pwd)): ${SCRIPT_PATH} ${1}"
        sh -c "${SCRIPT_PATH} ${1}" || RESULT="$?"
        if [ "${RESULT}" -ne "0" ]; then
            echo "INFO: ${SCRIPT_PATH} failed with exit code ${RESULT}"
            exit 1
        fi
        echo "INFO: Finished ${SCRIPT_PATH}"
    done
fi