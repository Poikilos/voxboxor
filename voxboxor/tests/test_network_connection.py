#!/usr/bin/env python3
from __future__ import print_function
from __future__ import division
import sys
import os

from unittest import TestCase

from voxboxor.network.connection import (
    get_packet_bytes,
    bytes_to_packet,
)

from voxboxor import (
    set_verbosity,
    echo0,
    echo1,
    echo2,
)

'''
myPath = os.path.realpath(__file__)
testsDir = os.path.dirname(myPath)
testDataPath = os.path.join(testsDir, "data")
if not os.path.isdir(testDataPath):
    raise IOError("The test folder is missing: \"{}\""
                  "".format(testDataPath))
'''


class DummyServer():

    def __init__(self):
        self.server_client_ids = []
        self.new_client_id = 2
        # 0 and 1 are not allowed (0 is PEER_ID_INEXISTENT)

    def generate_client_id(self):
        while self.new_client_id in self.server_client_ids:
            self.new_client_id += 1
        return self.new_client_id

    def client_connect_packet(self, values):
        client_connect_bytes = get_packet_bytes("client", "connect",
                                                values)
        client_connect_len = 4+2+1+1+2+1
        if len(client_connect_bytes) != client_connect_len:
            raise ValueError(
                "client_connect_bytes len should be {} but is {}"
                "".format(client_connect_len, len(client_connect_bytes))
            )
        return client_connect_bytes

    def server_accepted_connection_packet(self):
        set_verbosity(1)
        values = {}
        values['peer_id_new'] = self.generate_client_id()
        set_verbosity(2)
        server_connected_bytes = get_packet_bytes("server", "connected",
                                                  values)
        set_verbosity(1)
        server_connected_len = 4+2+1+1+2+1+1+2
        if len(server_connected_bytes) != server_connected_len:
            raise ValueError(
                "server_connected_bytes len should be {} but is {}"
                "".format(server_connected_len,
                          len(server_connected_bytes))
            )
        return server_connected_bytes

    def client_disconnect_packet(self, values):
        client_disconnect_bytes = get_packet_bytes(
            "client",
            "disconnect",
            values,
        )
        client_disconnect_len = 4+2+1+1+1
        if len(client_disconnect_bytes) != client_disconnect_len:
            raise ValueError(
                "client_disconnect_bytes len should be {} but is {}"
                "".format(client_disconnect_len,
                          len(client_disconnect_bytes))
            )
        return client_disconnect_bytes


class TestConnection(TestCase):
    '''
    def __init__(self, instance):
        self.server_client_ids = []
    '''

    def test_connect_and_disconnect_checking_peer_id(self):
        server = DummyServer()
        client_connect_bytes = server.client_connect_packet({})
        server_connected_bytes = \
            server.server_accepted_connection_packet()
        s_packet = bytes_to_packet('server', 'connected',
                                   server_connected_bytes)
        values = {}
        try:
            client_disconnect_bytes = \
                server.client_disconnect_packet(values)
        except ValueError as ex:
            if (("requires" in str(ex))
                    and ("sender_peer_id" in str(ex))):
                echo0("* sender_peer_id is required for disconnect"
                      " (test is ok)")
                # The non-failing state is tested next.
            else:
                raise ex
        # ^ Should raise: "ValueError: Constructing a client disconnect
        #   packet requires values to have the keys with no default:
        #   ['sender_peer_id']"
        values['sender_peer_id'] = s_packet.get('peer_id_new')
        client_disconnect_bytes = server.client_disconnect_packet(values)
