import socket
import threading
import sys
from termcolor import colored


# modify responses that comes from remote and goes to client
def response_handler(response):
    return response


# modify requests that comes from client and goes to remote
def request_handler(request):
    return request


def hexdump(source, length=16):
    """ take responses and turn them to hexadenimal values and ascii-printable characters.
    this is usedful for better understanding packets and protocols."""
    result = []
    digits = 2
    for i in range(0, len(source), length):
        src = source[i:i+length]
        hexa = ' '.join(["%0*x" %(digits, ord(x)) for x in src])
        text = ''.join([x if 32 <= ord(x) < 127 else '.' for x in src])
        result.append("%04x   %-*s    %s" %(i, length*(digits+1) , hexa, text))
    return '\n'.join(result)


def receive_from(socket):
    """ function receive all data sended to given socket and return data as string"""
    recv_data = ""
    while True:
        data = socket.recv(1024).decode()
        recv_data += data
        if len(data) < 1024:
            break
    return recv_data


def proxy_handler(client_socket, remotehost, remoteport, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # try to connect to remote host and port
        remote_socket.connect((remotehost, remoteport))
    except:
        print(colored(f"[!] Failed to connect to {remotehost}:{remoteport}", 'red'))
        remote_socket.close()
        sys.exit(2)
    
    # if the receive first is true then we must first receive some data from remote host
    # and then send that data to client
    if receive_first == "True":
        # take what remote host sends
        remote_response = receive_from(remote_socket)
        # hexdump it to our localhost server
        hexdump(remote_response)
        # send the remote response to response handler, if you want to modify that response before sending it to client
        remote_response = response_handler(remote_response)

        if remote_response:
            print(colored(f"[+] sending {len(remote_response)}bytes to client"))
            client_socket.send(remote_response.encode())
        
        # now we read from client send to remote and vice versa
        while True:
            client_buffer = receive_from(client_socket)
            if client_buffer:
                print(colored(f"[++] Received {len(client_buffer)}bytes from client"))
                hexdump(client_buffer)
                # send the client request to request handler to modify that request before sending it to remote host
                client_buffer = request_handler(client_buffer)

                remote_socket.send(client_buffer.encode())
                print(colored(f"[++] Sended  to remote host"))

            remote_buffer = receive_from(remote_socket)
            if remote_buffer:
                print(colored(f"[+++] Received {len(remote_buffer)}bytes from remote"))
                hexdump(remote_buffer)
                 # send the remote response to response handler, if you want to modify that response before sending it to client
                remote_buffer = request_handler(remote_buffer)

                client_socket.send(remote_buffer.encode())
                print(colored(f"[+++] Sended  to client"))

            # close connection if there is no data to be send and receive
            if not client_buffer and not remote_buffer:
                client_socket.close()
                remote_socket.close()
                print(colored(f"[*] No more data. Closing connections", 'cyan'))
                break


def server_loop(localhost, localport, remotehost, remoteport, receive_first):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # try to bind to specified localhost and port 
    try: 
        server_socket.bind((localhost, localport))
        server_socket.listen(5)
        print(colored(f"[*] Start listening on {localhost}:{localport}", 'green'))
    except:
        print(colored(f"[!] Failed to bind on {localhost}:{localport}", 'red'))
        server_socket.close()
        sys.exit(2)

    # if code in try block executed without any error then wait for incoming connections
    else:
        while True:   
            client_connected, addr = server_socket.accept()
            print(colored(f"[*] Received connection from {addr[0]}:{addr[1]}", 'green'))
            proxy_thread = threading.Thread(target=proxy_handler, args=(client_connected, remotehost, remoteport, receive_first))
            proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print(sys.argv[1:])
        usage = """#################################### Tcp Proxy #####################################
        Usage: ./tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]
        exmple: './tcp_proxy.py 192.168.1.33 4545 10.10.154.2 8989 True'
        """ 
        print(colored(usage, "yellow"))
        sys.exit(1)

    # setup local ip and port, we going to bind our server on them and when clients
    # connect to this server we redirct them to remote host and port and in the meanwhile we can
    # see the request and responses between clients and remote host, we also be able to modify traffic 
    localhost = sys.argv[1]
    localport = int(sys.argv[2])

    # remote ip and port 
    remotehost = sys.argv[3]
    remoteport = int(sys.argv[4])

    # tells our proxy to connect and receive data before sending to the remote host
    receive_first = sys.argv[5]
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    
    # run our server
    server_loop(localhost, localport, remotehost, remoteport, receive_first)

main()