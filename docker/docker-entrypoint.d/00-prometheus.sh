#!/bin/sh
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
echo "----------------------------"
echo "Create prometheus metrics dir"
echo "----------------------------"
echo ${PROMETHEUS_MULTIPROC_DIR}
mkdir -p ${PROMETHEUS_MULTIPROC_DIR}