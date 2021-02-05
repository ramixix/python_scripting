import socket
from termcolor import colored
import threading

def client_handler(client_socket, addr):
    # send a acknowledge to client
    client_socket.send(("ACK from the server").encode())
    
    # recive and print data that clients sended, until recieving 'q' from client
    recv_data = ""
    while recv_data.lower() != 'q':
        recv_data = ""
        while True:
            data = client_socket.recv(1024).decode()
            if len(data) < 1024:
                recv_data += data
                break
            recv_data += data
            
        if recv_data != "":
            print(colored(f"[+] Data received from {addr[0]} port {addr[1]} : {recv_data}", 'green'))
    
    # after clinet left the connection
    print(colored(f"[-] clinet {addr[1]} left the chat", 'yellow'))
    client_socket.send(("ByeBye").encode())
    client_socket.close()        

def main():

    # ipv4 and port to bind to
    bind_ip = "0.0.0.0"
    bind_port = 4444

    # create server socket using INET family and tcp type protocol
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # bind to specified ip and port 
        server_socket.bind((bind_ip, bind_port))
        print(colored(f"[*] Listening on {bind_ip}:{bind_port}", 'cyan'))
    except:
        print(colored("[!] falid to bind", 'red'))
        server_socket.close()
        exit(0)

    # start listening with a maximum backlog of connections set to 5
    server_socket.listen(5)

    while True:
        # wait for incoming connection and after recieving one, we use threads to handle connections
        connected_client, addr = server_socket.accept()
        print(colored(f"[*] Recieve connection from {addr[0]} port {addr[1]}", 'green'))
        client_thread = threading.Thread(target=client_handler, args=(connected_client, addr))
        client_thread.start()

if __name__ == "__main__":
    main()