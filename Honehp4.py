import socket
import datetime

# Change the server name here
HOST = 'Thor'  # Change this to your desired hostname or IP address
PORT = 22  # SSH port

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)  # Allow up to 5 pending connections

print("Serving on port:", PORT)

def get_log_file_name():
    # Generate log file name based on the current date
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return f"ssh_logs_{today_date}.txt"

def log_connection(client_address, username, password, connection_time):
    # Log connection details including timestamp, IP address, username, password, and connection time
    log_file = get_log_file_name()
    with open(log_file, "a") as logfile:
        logfile.write(f"{connection_time}: Connection from {client_address}, Username: {username}, Password: {password}\n")

while True:
    client_connection, client_address = listen_socket.accept()
    print("Connection from:", client_address)
    
    try:
       message = "Hello Client"
       client_connection.sendall(message.encode())

      # Prompting user for password
       password = input("Please enter your password: ")

      # Logging connection details
       connection_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       log_connection(client_address[0], '', password, connection_time)

    finally:
      client_connection.close()



