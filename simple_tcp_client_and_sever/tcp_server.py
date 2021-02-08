import socket
from termcolor import colored
import threading


# format that is using for decoding and encoding messages, and header size that is used to determine the length of messages
FORMAT = "utf-8"
HEADERSIZE = 16

# make a header for every message that is going to be send.
# this header contain message length so this way by reading header first 
# client can easily find the length of message
def send_to_client(client_socket, msg):
    msg_length = len(msg)
    headersize = str(msg_length)
    msg_header = headersize + " " * (HEADERSIZE - len(headersize))
    message = (msg_header + msg).encode(FORMAT)
    client_socket.send(message)
    

def client_handler(client_socket, addr):
    # send a acknowledge to client
    send_to_client(client_socket, "ACK from the server")
    
    # receive and print data that clients send to server. quit if client enter q keyword.
    while True:
        # get header that contain the length of message that is going to be receive
        msg_header = client_socket.recv(HEADERSIZE).decode(FORMAT)
        if msg_header:
            msg_length =  int(msg_header.strip(" "))
            data = client_socket.recv(msg_length).decode(FORMAT)
            if data.lower() == "q":
                break
            if data != "":
                print(colored(f"[+] Data received from {addr[0]} port {addr[1]} : {data}", 'green'))
    
    # after clinet left the connection
    print(colored(f"[-] clinet {addr[1]} left the chat", 'yellow'))
    send_to_client(client_socket, "ByeBye")
    client_socket.close()        

def main():

    # ipv4 and port to bind to (ip will be the local address of the computer that server is going to run on.)
    bind_ip = socket.gethostbyname(socket.gethostname())
    bind_port = 4444
    BindADDR = (bind_ip, bind_port)

    # create server socket using INET family and tcp type protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # bind to specified ip and port 
        server_socket.bind( BindADDR )
        print(colored(f"[*] Listening on {bind_ip}:{bind_port}", 'cyan'))
    except:
        print(colored("[!] falid to bind", 'red'))
        server_socket.close()
        exit(0)

    # start listening with a maximum backlog of connections set to 5
    try:
        server_socket.listen(5)
        while True:
            # wait for incoming connection and after recieving one, we use threads to handle connections
            connected_client, addr = server_socket.accept()
            print(colored(f"[*] Recieve connection from {addr[0]} port {addr[1]}", 'yellow'))
            client_thread = threading.Thread(target=client_handler, args=(connected_client, addr))
            client_thread.start()
    
    except KeyboardInterrupt:
        print(colored("\n[!] Closing Server ", 'yellow'))
        server_socket.close()
        exit()


if __name__ == "__main__":
    main()