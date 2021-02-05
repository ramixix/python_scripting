import socket 
from termcolor import colored

# reciev what server sends and retrun all as string
def recv_from_server(cli_socket):
    recv_data = ""
    while True:
        data = cli_socket.recv(1024).decode()
        if len(data) < 1024:
            recv_data += data
            break
        recv_data += data
    if recv_data:
        return recv_data
    else:
        return ""

def main():

    # target host and port to connect to 
    thost_ipv4 = "0.0.0.0"
    tport = 4444

    # create socket using INET family and tcp type protocol
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # try to connet to target
        client_socket.connect((thost_ipv4, tport))
    except :
        print(colored("[!] failed to connet to target host ip", "red"))
        client_socket.close()
        exit()

    recv_data = recv_from_server(client_socket)
    if recv_data:
        print(colored(recv_data, "green"))

    # get data from client and send it to server, repeat this untill client quit by entering q keyword
    while True:
        data_to_send = input(colored("[*] send data (enter q to quit): ", "cyan"))
        client_socket.send(data_to_send.encode())
        if data_to_send.lower() == 'q' :
            break

    # recieve server response 
    recv_data = recv_from_server(client_socket)
    if recv_data:
        print(colored(recv_data, "green"))

if __name__ == "__main__":
    main()