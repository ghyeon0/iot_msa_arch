import canrpc_pb2 as pb
import canrpc_pb2_grpc as rpcservice
import grpc
import sys
import os


class J1:
    channel = None
    client = None
    server_ip = None

    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.channel = grpc.insecure_channel(self.server_ip+':6000')
        self.client = rpcservice.CANRPCServiceStub(self.channel)

if __name__ == "__main__":
    server_ip = os.getenv('SERVER_IP')
    
    if server_ip is None:
        print('server ip not defined')
        sys.exit(1)
	
    j1 = J1(server_ip)

    print("\nSEND\n")
    can = j1.client.SendCAN(
        pb.SendCANArgs(
            contents=bytes(b'hello'),
        )
    )
    print("can created with id: %s" % can.id)

    print("\nREAD\n")
    can_clone = j1.client.ReadCAN(
        pb.ReadCANArgs(
            id=can.id,
        )
    )
    print("got id: %s, contents = %s" %
          (can_clone.id, can_clone.contents.decode()))
