
import multiprocessing

bind = "0.0.0.0:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30

# Enable logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Worker settings
worker_tmp_dir = '/tmp'
