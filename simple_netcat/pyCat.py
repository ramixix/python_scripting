import sys
import socket
import threading
import getopt
import subprocess
from termcolor import colored
import random


# global variables
listen = False
command = False
execute = ""
upload_destination = ""
target = ""
port = 0


def usage():
    print(colored("""\n$############################################################ PyCat ############################################################$\n
    Usage : ./PyCat -t taget_host -p port
    -l --listen                     -listen on [host]:[port] for incoming connections
    -e --execute=file_to_run        -execute the give file upon receiving a connection
    -c --commandshell               -initialize a command shell
    -u --upload=destination         -upon receiving connection upload a file and write to [destination]\n\n
    Examples:
    ./PyCat -t 192.168.1.1 -p 4545 -l -c
    ./PyCat -t 192.168.1.1 -p 4545 -l -u=c:\\target.exe
    ./PyCat -t 192.168.1.1 -p 4545 -l -e='cat /etc/passwd'
    'echo \"hello\" |./PyCat -t 192.168.1.1 -p 5665
    """, 'yellow'))
    sys.exit(1)


def execute_command(command):
    command = command.strip(' ')
    try:
        output = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = output.stdout
    except:
        output = "Failed to execute command.\r\n"
    
    return output


def client_handler(client_socket):
    global command
    global execute
    
    if upload_destination:
        recv_file = ""  
        while True:
            data = client_socket.recv(1024).decode()
            recv_file += data
            if len(data) < 1024:
                break
    
        try:
            with open(upload_destination, "wb") as upload_file:
                upload_file.write(recv_file.encode())

            client_socket.send(f"Successfully save file to {upload_destination}\n".encode())
        
        except:
            client_socket.send(f"Failed to save file to {upload_destination}\n".encode())

    if execute:
        output = execute_command(execute)
        client_socket.send(output.encode())
    
    if command:
        while True:
            client_socket.send("nc#> ".encode())
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()

            output = execute_command(cmd_buffer)
            client_socket.send(output.encode())


def server_loop():
    global target

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if not target:
        target = "0.0.0.0"
    
    try:
        server_socket.bind((target, port))
    except:
        print(colored("[!] faild to bind to specified target and port(inside server_loop function", 'red'))
        sys.exit()

    server_socket.listen(5)

    while True:
        connected_socket, addr = server_socket.accept()
        print(colored(f"Recieved a connection from {addr[0]} port {addr[1]}", 'green'))
        client_thread = threading.Thread(target=client_handler, args=(connected_socket,))
        client_thread.start()


def client_sender(buffer):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((target, port))
    except : 
        print(colored("[!] failed to connect to specified target and ip(inside client_sender function)", 'red'))
        client_socket.close()
        sys.exit("connection failed")
    
    try:
        if buffer:
            client_socket.send(buffer.encode())

        while True:
            recv_data =""
            while True:
                data = client_socket.recv(2048).decode()
                recv_data += data
                if len(data) < 2048:
                    break
            
            print(colored(recv_data, "green"))

            buffer = input("")
            buffer += "\n"
            client_socket.send(buffer.encode())
    except:
        print(colored("[!] Exception inside client_sender funciton", 'red'))
        client_socket.close()
        exit(2)


def main():
    global listen
    global command
    global execute
    global upload_destination
    global target
    global port

    if not sys.argv[1:]:
        usage()

    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hlce:u:t:p:", ["help", "listen", "command", "execute=", "upload_destination=", "target=", "port="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        #sys.exit("Argument Error")
    
    for opt, arg in options:

        if opt in ['-h', '--help']:
            usage()
        if opt in ['-l', '--listen']:
            listen = True
        if opt in ['-c', '--commad']:
            command = True
        if opt in ['-e', '--execute']:
            execute = arg
        if opt in ['-u', '--upload_destination']:
            upload_destination = arg
        if opt in ['-t', '--target']:
            target = arg
        if opt in ['-p', '--port']:
            port = int(arg)
    
    if not port:
        random.randint(20000, 21000)
    
    if not listen and not target:
        sys.exit("Target is not specified")

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen: 
        server_loop()

main()