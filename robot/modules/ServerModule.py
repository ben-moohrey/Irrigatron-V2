from modules.BaseModule import BaseModule
import socket
import json
import time

class ServerModule(BaseModule):
    def __init__(self, topics, thread_id, settings, server_ip, server_port):
        super().__init__(topics, thread_id, settings)

        self.server_ip = server_ip
        self.server_port = server_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((server_ip, server_port))
        self.server_socket.listen(1)

        self.control_data_topic = self.topics.get_topic("control_data")
        self.server_socket.settimeout(0.5)
        self.retries = 0
        self.retry_count = 3
        

    # def run(self, shutdown_flag):
    #     print("Waiting for a connection...")
    #     try:
    #         client_socket, addr = self.server_socket.accept()
    #         print("Connected to:", addr)
    #         while not shutdown_flag.is_set():
    #             data = client_socket.recv(1024)
    #             if data:
    #                 try:

    #                     control_data = json.loads(data.decode())
    #                 except json.decoder.JSONDecodeError as e:
    #                     continue
    #                 self.control_data_topic.write_data(control_data)

    #                 # if (mode=="controller"):

    #                 #     motor_state = robot.xy_state_to_motor_state(control_data)

    #                 #     # print(json.dumps(motor_state, indent=4))
    #                 #     try:
    #                 #         robot.write_to_serial(motor_state)
    #                 #     except BaseException as e:
    #                 #         print(e)
    #                 #         print("FAILED TO WRITE")
    #                 # else:
    #                 #     enabled = True
    #                 #     while enabled:
    #                 #         enabled = robot.run()
    #             else:
    #                 break
    #     except socket.timeout:
    #         print("Socket Timed Out: Retrying")


    def shutdown(self):
        self.server_socket.close()

    def run(self, shutdown_flag):
        self.log("Waiting for a connection...")

        client_socket = None
        addr = None

        # Loop until shutdown_flag is set
        while not shutdown_flag.is_set():
            try:
                client_socket, addr = self.server_socket.accept()
                self.log("Connected to:", addr)
                break
            except socket.timeout:
                continue  # Go back to start of loop and check shutdown_flag again
            except socket.error as e:
                # Handle error (if necessary)
                continue

        # If a client connected successfully
        if client_socket:
            client_socket.setblocking(1)  # Set blocking mode for recv calls
            while not shutdown_flag.is_set():
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break  # No more data, exit loop
                    # Process data
                    try:

                        control_data = json.loads(data.decode())
                    except json.decoder.JSONDecodeError as e:
                        continue
                    self.control_data_topic.write_data(control_data)
                except socket.error as e:
                    # Handle errors, e.g., client disconnected
                    break

        # Clean up client connection
        if client_socket:
            client_socket.close()

            
                

