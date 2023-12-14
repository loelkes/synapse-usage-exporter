#!/bin/sh
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
echo "----------------------------"
echo "Running entrypoint.sh script"
echo "----------------------------"
echo "Version: ${APP_VERSION}"
echo "Build: ${BUILD_ID}"
echo ""
echo "----------------------------"
echo "Create prometheus metrics dir"
echo "----------------------------"
echo ${PROMETHEUS_MULTIPROC_DIR}
mkdir -p ${PROMETHEUS_MULTIPROC_DIR}
echo ""
echo "----------------------------"
echo "Start µWSGI..."
echo "----------------------------"
uwsgi uwsgi.ini