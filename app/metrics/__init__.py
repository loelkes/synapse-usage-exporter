"""Prometheus metrics module."""
import sys
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import multiprocess, make_wsgi_app, Info, Gauge
from prometheus_client import CollectorRegistry


GAUGES = [
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

INFOS = [
    'homeserver',
    'server_context',
    'python_version',
    'database_engine',
    'database_server_version',
    'log_level',
]


class Prometheus:
    """Prometheus metrics class."""

    def __init__(self, app: Flask = None):
        self.registry = CollectorRegistry()
        self.metadata = Info('app_build_info', 'Description of the build')
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        """Initialize Flask application."""
        # See https://prometheus.github.io/client_python/instrumenting/labels/
        app.config['LABELS_INITIALIZED'] = False  # Set True once labels are initialized.
        app.config['METRICS_PREFIX'] = 'synapse_usage_'
        try:
            multiprocess.MultiProcessCollector(self.registry)
        except ValueError as error:
            app.logger.error(error)
            sys.exit(1)
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})
        self.metadata.info({'version':  app.config['VERSION'], 'build': app.config['BUILD']})
        self.metrics = {
            metric: Gauge(app.config['METRICS_PREFIX'] + metric, metric, INFOS) for metric in GAUGES
        }
