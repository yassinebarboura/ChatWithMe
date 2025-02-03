bind = "0.0.0.0:8001"  # This allows external connections
workers = 1
worker_class = "gevent"
timeout = 120
keepalive = 2
errorlog = "-"
loglevel = "info"
