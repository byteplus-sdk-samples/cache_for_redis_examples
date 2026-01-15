## SSO (Single Sign-On) System

### Overview
This is a simple Single Sign-On (SSO) demo built with Flask and Redis. It allows users to access multiple related services after logging in once, without having to log in again for each service. The system includes an authentication center and two business services (Service A and Service B), and uses Redis as distributed session storage.

The system consists of the following core components:

- Authentication Server (`auth_server.py`): Responsible for user authentication and session management
- Service A (`service_a.py`): The first business application that requires authentication
- Service B (`service_b.py`): The second business application that requires authentication
- Redis: Distributed session storage used to persist user login state

### Workflow
1. The user visits any business service (A or B).
2. If the user is not logged in, they are redirected to the authentication server's login page.
3. The user enters a username and password for verification.
4. After successful verification, the system generates a unique session ID and saves it to Redis.
5. The system sets the session cookie and redirects to the service selection page.
6. The user can access any business service; each service validates the user by checking session data in Redis.
7. When the user logs out, the system clears the session data in Redis and removes the cookie.

### Quick Start

#### Prerequisites
- Python 3.10+
- Volcano Engine Redis Cloud Server

#### Install Dependencies
`bash pip install flask redis`

#### Configure the System
Edit the configuration in `config.py`:

```
# Server IP or domain
SERVER_HOST = '127.0.0.1'  # Change to the server's public IP in real deployment

# Redis configuration
REDIS_HOST = 'localhost'   # Change to the Redis server address
REDIS_PORT = 6379
REDIS_PASSWORD = None      # If Redis has a password, fill in the password string
```
#### Run the System
1. Ensure that the Redis service is running
2. Start the authentication server `bash python auth_server.py`
3. In a new terminal window, start Service A `bash python service_a.py`
4. In another new terminal window, start Service B `bash python service_b.py`

### Access the System
1. Open a browser and visit the business services:
- Service A: http://127.0.0.1:5001
- Service B: http://127.0.0.1:5002
2. The system will automatically redirect to the login page
3. Use the following test accounts to log in:
- Username: user1, Password: password1
- Username: user2, Password: password2
4. After successful login, you can choose to access different services

### Notes
- This system is for demonstration purposes only and is not intended for commercial use.
- No warranties or guarantees are provided.

### License
MIT License