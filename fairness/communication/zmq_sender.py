# coding=utf-8
import json

import zmq

from fairness.config_parser import MyConfigParser
from fairness.node.nri import NRI

import api


class Sender:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    #  Socket to talk to server
    def __init__(self):
        print("Connecting to get the neighbor…")
        config = MyConfigParser()
        controller_ip = config.config_section_map('keystone_authtoken')['ip']
        address = "tcp://" + controller_ip + ":5555"
        self.socket.connect(address)
        json_string = json.dumps({'neighbor':NRI._get_public_ip_address()})
        self.socket.send(json_string)

        response = self.socket.recv()
        self.socket.close()

        json_res = json.loads(response)
        if 'neighbor' in json_res:
            address = "tcp://" + json_res['neighbor'] + ":5555"

            print 'The address is: ' + address

            self.socket.connect(address)

    def send_nri(self, nri):
        key = 'nri_' + NRI._get_public_ip_address()
        own_nri = {key: nri.__dict__}

        if not nri.server_nris.__contains__('nri'):
            nris = [own_nri]
            nri.server_nris['nri'] = nris
        else:
            if not any(d.get(key, None) is not None for d in nri.server_nris['nri']):
                nri.server_nris['nri'].append(own_nri)

        json_string = json.dumps(nri.server_nris)
        self.socket.send(json_string)
        Sender.socket.recv()

    def send_greediness(self, rui):
        key = 'greed_' + NRI._get_public_ip_address()
        own_greed = {key: rui.get_vm_greediness()}

        if not rui.server_greediness.__contains__('greed'):
            greeds = [own_greed]
            rui.server_greediness['greed'] = greeds
        else:
            if not any(d.get(key, None) is not None for d in rui.server_greediness['greed']):
                rui.server_greediness['greed'].append(own_greed)
            else:
                lool = [own_greed if key in x else x for x in rui.server_greediness['greed']]
                rui.server_greediness['greed'] = lool

        json_string = json.dumps(rui.server_greediness)
        self.socket.send(json_string)
        Sender.socket.recv()
