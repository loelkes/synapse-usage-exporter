"""Synapse usage stats exporter
Copyright (C) 2023 Christian Lölkes

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from logging.config import dictConfig
import os
import sys
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from prometheus_client import multiprocess, make_wsgi_app, Info, Gauge
from prometheus_client import CollectorRegistry
from werkzeug.middleware.dispatcher import DispatcherMiddleware

load_dotenv()  # take environment variables from .env.

# Configure logging.

dictConfig({
    'version': 1,
    'formatters': {'default': {'format': '%(created)i server %(levelname)s %(name)s: %(message)s'}},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': logging.getLevelName(os.environ.get('APP_LOG_LEVEL', 'INFO')),
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger()
logger.warning('Root logger set to %s', logging.getLevelName(logger.level))
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(os.environ.get('WERKZEUG_LOG_LEVEL', logger.level))
logger.warning('Werkzeug logger set to %s', logging.getLevelName(werkzeug_logger.level))

# Create Flask application

app = Flask(__name__)
app.logger.setLevel(logging.getLogger().level)
app.config['VERSION'] = os.environ.get('APP_VERSION', 'undefined')
app.config['BUILD'] = os.environ.get('BUILD_ID', 'undefined')
# See https://prometheus.github.io/client_python/instrumenting/labels/
app.config['LABELS_INITIALIZED'] = False  # Set True once labels are initialized.
app.config['METRICS_PREFIX'] = 'synapse_usage_'

# Initialize Prometheus-Client

registry = CollectorRegistry()
try:
    multiprocess.MultiProcessCollector(registry)
except ValueError as error:
    app.logger.error(error)
    app.logger.error('PROMETHEUS_MULTIPROC_DIR: "%s"', os.environ.get('PROMETHEUS_MULTIPROC_DIR'))
    sys.exit(1)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

# Initialize metrics

metadata = Info('app_build_info', 'Description of the build')
metadata.info({'version':  app.config['VERSION'], 'build': app.config['BUILD']})

gauges = [
    'memory_rss',
    'cpu_average',
    'timestamp',
    'uptime_seconds',
    'total_users',
    'total_nonbridged_users',
    'daily_user_type_native',
    'daily_user_type_guest',
    'daily_user_type_bridged',
    'total_room_count',
    'daily_active_users',
    'monthly_active_users',
    'daily_active_rooms',
    'daily_active_e2ee_rooms',
    'daily_messages',
    'daily_e2ee_messages',
    'daily_sent_messages',
    'daily_sent_e2ee_messages',
    'r30v2_users_all',
    'r30v2_users_android',
    'r30v2_users_ios',
    'r30v2_users_electron',
    'r30v2_users_web',
    'cache_factor',
    'event_cache_size'
]

infos = [
    'homeserver',
    'server_context',
    'python_version',
    'database_engine',
    'database_server_version',
    'log_level',
]

metrics = {metric: Gauge(app.config['METRICS_PREFIX'] + metric, metric, infos) for metric in gauges}

@app.route("/report-usage-stats/push", methods=['PUT'])
def report_usage_stats():
    """Receive usage stats and write to prometheus metrics."""
    labels = [request.json[key] or 'None' for key in infos]
    if not app.config['LABELS_INITIALIZED']:
        app.logger.debug('Initialize labels %s', labels)
    for key, value in request.json.items():
        if key in infos:
            continue
        if not app.config['LABELS_INITIALIZED']:
            metrics[key].labels(*labels)
        metrics[key].labels(*labels).set(value)
        app.logger.debug('Receive value %s for %s', value, key)
    app.config['LABELS_INITIALIZED'] = True
    return jsonify({})
