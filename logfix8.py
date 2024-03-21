import socket
import datetime
import paramiko
import os

# Change the server name here
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 22  # SSH port

# Specify the directory where logs should be saved (absolute path)
LOGS_DIR = '/path/to/logs/'

def get_log_file_name():
    # Generate log file name based on the current date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # Return the full path to the log file
    return os.path.join(LOGS_DIR, f"ssh_logs_{today_date}.txt")

def log_connection(client_address, username, password, connection_time):
    # Log connection details including timestamp, IP address, username, password, and connection time
    log_file = get_log_file_name()
    try:
        with open(log_file, "a") as logfile:
            logfile.write(f"{connection_time}: Connection from {client_address}, Username: {username}, Password: {password}\n")
    except Exception as e:
        print("Error writing to log file:", e)

# Generate RSA key pair for SSH
key = paramiko.RSAKey.generate(2048)

# Function to handle SSH connections
def handle_ssh(client):
    transport = paramiko.Transport(client)
    transport.add_server_key(key)

    # Implementing a custom SSH server that doesn't send any banner
    class NoBannerSSHServer(paramiko.ServerInterface):
        def get_banner(self):
            return '', ''  # Empty banner and language

    server = NoBannerSSHServer()
    transport.start_server(server=server)

    # Accepting the SSH session
    channel = transport.accept(20)
    if channel is None:
        print('SSH connection timed out')
        transport.close()
        return

    # Collecting client's username
    username = transport.get_username()
    print(f'Connection from: {client.getpeername()}, Username: {username}')

    # Waiting for the client's password
    try:
        # Send a request for password
        channel.send('\nPlease enter your password: ')

        # Receive password from client
        password = channel.recv(1024).decode().strip()
        print(f'Password received: {password}')

        # Log connection details
        connection_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_connection(client.getpeername()[0], username, password, connection_time)

        # Close SSH session
        channel.close()
    finally:
        transport.close()

# Create a TCP socket and start listening
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(5)  # Allow up to 5 pending connections

print("Serving on port:", PORT)

while True:
    client_connection, client_address = listen_socket.accept()
    print("Connection from:", client_address)
    handle_ssh(client_connection)
