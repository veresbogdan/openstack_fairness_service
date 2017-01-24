# coding=utf-8
import json
import time
import zmq

from fairness import utils
from fairness.node_service.nri import NRI
from fairness.config_parser import MyConfigParser


class ControllerServer:
    config = MyConfigParser()
    interval = config.config_section_map('communication')['ring_interval']
    zmq_port = config.config_section_map('communication')['controller_port']
    context = zmq.Context()
    client_socket = context.socket(zmq.REQ)

    def __init__(self, manager=None):
        """
        Initialize the controller server and start the ZMQ listener
        :param manager: the controller manager
        """
        self.manager = manager
        self.host_no = 0

        server_socket = self.context.socket(zmq.REP)
        # get own ip here from the manager
        server_socket.bind("tcp://" + NRI.get_public_ip_address() + ":" + self.zmq_port)

        while True:
            #  Wait for next request from clients
            message = server_socket.recv()
            print("Received request: " + message)
            # socket.send("")

            # start new thread to manage each request
            self.manage_message(message, server_socket)

    def manage_message(self, message, socket):
        """
        The method that manages accordingly each received message.
        :param message: the received message
        :param socket: the ZMQ socket
        """
        if message is not None:
            json_msj = json.loads(message)

            if 'nri' in json_msj:
                self.manager.crs = utils.dsum(self.manager.crs, json_msj['nri'])

            if 'neighbor' in json_msj:
                req_ip = json_msj['neighbor']
                ips_list = self.manager.ips_list
                if req_ip in ips_list:
                    index = ips_list.index(req_ip)

                    # the last node in the node list gets the controller as neighbor
                    if index == len(ips_list) - 1:
                        return_message = {'neighbor': NRI.get_public_ip_address()}
                    else:
                        return_message = {'neighbor': ips_list[index + 1]}

                    self.host_no += 1
                    json_string = json.dumps(return_message)
                    socket.send(json_string)

                    if self.host_no == len(ips_list):
                        print 'send crs...'
                        # the controller gets the first node from the node list as neighbor
                        self.send_crs(ips_list[0])

            if 'crs' in json_msj:
                # first send back ack reply (before sending a message to the next node)
                socket.send("")
                print 'start grid ring...'

                global start
                start = time.time()

                self.start_greed_ring()

            if 'greed' in json_msj:
                # first send back ack reply (before sending a message to the next node)
                socket.send("")
                print 'got greed...'

                # measure time again, subtract
                end = time.time()
                sleep_time = float(self.interval) - (end - start)
                time.sleep(sleep_time)
                start = time.time()

                self.client_socket.send(message)
                self.client_socket.recv()

    def send_crs(self, ip):
        """
        Method that connects to the first node to send the CRS when the CRS calculation is complete
        :param ip: the ip of the node to send to
        """
        print('Connecting to first node…')
        self.client_socket.connect("tcp://" + ip + ":" + self.zmq_port)

        json_string = json.dumps({'crs': self.manager.crs})
        self.client_socket.send(json_string)
        self.client_socket.recv()

    def start_greed_ring(self):
        """
        Method that computes the initial greediness vector and starts the ZMQ ring
        """
        json_string = json.dumps({'greed': self.manager.get_initial_user_vector()})
        self.client_socket.send(json_string)
        self.client_socket.recv()
