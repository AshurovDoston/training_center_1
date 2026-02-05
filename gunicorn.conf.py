# Server socket
bind = "127.0.0.1:8040"

# Workers
workers = 3
worker_class = "sync"
timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "training_center"

# Server mechanics
daemon = False
pidfile = None