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
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from .metrics import Prometheus, INFOS

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
prometheus = Prometheus(app)


@app.route("/report-usage-stats/push", methods=['PUT'])
def report_usage_stats():
    """Receive usage stats and write to prometheus metrics."""
    labels = [request.json[key] or 'None' for key in INFOS]
    if not app.config['LABELS_INITIALIZED']:
        app.logger.debug('Initialize labels %s', labels)
    for key, value in request.json.items():
        if key in INFOS:
            continue
        if not app.config['LABELS_INITIALIZED']:
            prometheus.metrics[key].labels(*labels)
        prometheus.metrics[key].labels(*labels).set(value)
        app.logger.debug('Receive value %s for %s', value, key)
    app.config['LABELS_INITIALIZED'] = True
    return jsonify({})
