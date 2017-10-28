import socket
import select
import sys
import time
from optparse import OptionParser

# Used to parse the optional arguments passed
parser = OptionParser()
parser.add_option("--raw", help="placeholder", action="store_true")
parser.add_option("--strip", help="placeholder", action="store_true")
parser.add_option("--hex", help="placeholder", action="store_true")
parser.add_option("--auto", help="placeholder")

# Parses options and arguments
(options, args) = parser.parse_args()


print(options)
print(args)


# Checks that the number of arguments is valid (should be 3)
if(len(args) != 3):
	print("Invalid Number of Arguments: proxy.py [logOptions] [replaceOptions] <srcPort> <server> <dstPort>")
	sys.exit(0)

src_port = int(args[0])
host = args[1]
dst_port = int(args[2])

port_client = socket.socket()
port_client.setblocking(0)
port_client.bind(('0.0.0.0',  int(args[0])))
port_client.listen()


port_server = socket.socket()
connected = False

inputs = [port_client, port_server]
outputs = []
msg_queue = {}
msg_index = []



try:
    while inputs:
        readable, writable, exception = select.select(inputs, outputs, inputs)
        for s in readable:
            if s is port_client:
				# Accepts the client conenction
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                
                # Prints out connection details and time of connection
                localtime = time.asctime( time.localtime(time.time()) )
                print("Port logger running: src_port=%s host=%s dst_port=%s" % (src_port, host, dst_port))
                print("New connection: %s, from %s" % (localtime, s.getsockname()[0]))

				# Adds connection to the message queue for sending
                msg_queue[s.getsockname()[1]] = connection
                # Adds socket port to message index for later retrieval of messages
                msg_index.append(s.getsockname()[1])
                #print(msg_queue[port_2])
            elif s is port_server and connected == False:
                # Continously attempts to connect to the remote server 
                while not connected:
                    try:
                        port_server.connect((host, dst_port))
                        connected = True
                    except Exception as e:
                        pass #Do nothing, just try again
                localtime = time.asctime( time.localtime(time.time()) )
				# Adds connection to the message queue for sending
                msg_queue[s.getsockname()[1]] = port_server
                # Adds socket port to message index for later retrieval of messages
                msg_index.append(s.getsockname()[1])
            else:
                data = s.recv(1024)
                # Socket is still open and data has been received
                if data:
					# Print out incoming data and send to other connection
                    print("<- %s from %s" % (data, s))
                    for i in msg_index:
                        if(i != s.getsockname()[1]):
                            msg_queue[i].send(data)
                            break
                else:
                    s.close()

                if s not in outputs:
                    outputs.append(s)

        for s in writable:
            if data:
                print("-> %s to %s" % (data, s))
                print("\n")
            outputs.remove(s)
# User enters a keyboard interrupt to close program
except KeyboardInterrupt:
    print("Closing sockets and exiting program")
    port_client.close()
    port_server.close()
    sys.exit(1)
# Exception occured in select function
except select.error:
    print("select error!!!")
    port_client.close()
    port_server.close()
    sys.exit(1)



#nc -l -p <port>
