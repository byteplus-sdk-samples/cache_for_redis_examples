# config

# Server IP or domain
SERVER_HOST = '127.0.0.1'  # Change to the server's public IP in real deployment

# Authentication center configuration
AUTH_SERVER_PORT = 5000

# Business service A configuration
SERVICE_A_PORT = 5001

# Business service B configuration
SERVICE_B_PORT = 5002

# Redis configuration
REDIS_HOST = 'localhost'   # Change to the Redis instance's domain in real deployment
REDIS_PORT = 6379
REDIS_PASSWORD = None      # If there is a password, fill in the string; if not, write None

# Session expiration time (seconds)
SESSION_EXPIRE = 3600
