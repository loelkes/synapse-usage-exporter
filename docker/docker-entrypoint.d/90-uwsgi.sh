#!/bin/sh
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
echo "----------------------------"
echo "Start µWSGI..."
echo "----------------------------"
uwsgi uwsgi.ini