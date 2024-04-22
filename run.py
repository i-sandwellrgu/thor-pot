# Refrences https://snyk.io/advisor/python/paramiko/functions/paramiko.RSAKey.generate, https://docs.python.org/3/library/datetime.html, https://github.com/ramonmeza/PythonSSHServerTutorial, https://docs.paramiko.org/en/latest/api/server.html,
# https://codereview.stackexchange.com/questions/171179/python-script-to-execute-a-command-using-paramiko-ssh, https://readthedocs.org/projects/paramiko-docs/downloads/pdf/2.7/, https://realpython.com/python-sockets/
#



import socket
import datetime
import paramiko
import os
import signal
import logging

# Change the server name here
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 22  # SSH port

# Starts logging 
log_file_name = f"ssh_logs_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s: %(message)s')

# Variable to termanate the server, when changed to true the server terminates
terminate_server = False

# This function handles SSH connections and generates the key pairs
def handle_ssh(client, client_address):
    transport = paramiko.Transport(client)
    transport.add_server_key(paramiko.RSAKey.generate(2048))

    # This function fakes an SSH server, no banner sent as I could not get it to work
    class NoBannerSSHServer(paramiko.ServerInterface):
        def get_banner(self):
            return '', ''  # Empty banner

        def check_auth_password(self, username, password):
            # Logs username, password, and client IP address
            logging.info(f'Connection from: {client_address}, Username: {username}, Password: {password}')
            return paramiko.AUTH_FAILED

    server = NoBannerSSHServer()
    transport.start_server(server=server)

    # Accepting the SSH session
    channel = transport.accept(20)
    if channel is None:
        logging.error('SSH connection timed out')
        transport.close()
        return

    try:
        while transport.is_active():
            channel.close()
    except EOFError:
        pass
    finally:
        transport.close()

# Signal handler for terminating the server
def signal_handler(sig, frame):
    global terminate_server
    logging.info("Received signal: %s", sig)
    logging.info("Terminating server...")
    terminate_server = True

# Register signal handler for SIGINT (Signal Interupt) (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Create a TCP socket and start listening
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind((HOST, PORT))
    listen_socket.listen(5)  # Allow up to 5 pending connections

    logging.info("Serving on port: %s", PORT)

    # Set a timeout for accepting connections
    # listen_socket.settimeout(1)  # 1 second timeout

    while not terminate_server:
        try:
            client_connection, client_address = listen_socket.accept()
            logging.info("Connection from: %s", client_address)
            handle_ssh(client_connection, client_address)
        except socket.timeout:
            # Timeout occurred, continue listening
            logging.error("Timeout occurred while waiting for connections.")

    # Close the listening socket
    listen_socket.close()

logging.info("Server stopped.")
