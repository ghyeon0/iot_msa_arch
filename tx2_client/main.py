import canrpc_pb2 as pb
import canrpc_pb2_grpc as rpcservice
from j1 import inference_test as inf
import grpc
import sys
import os

if __name__ == "__main__":
    server_ip = os.getenv('SERVER_IP')
    
    if server_ip is None:
        print('server ip not defined')
        sys.exit(1)
	
    channel = grpc.insecure_channel(server_ip+':6000')
    client = rpcservice.CANRPCServiceStub(channel)

    print("\nSEND\n")
    can = client.SendCAN(
        pb.SendCANArgs(
            contents=bytes(b'hello'),
        )
    )
    print("can created with id: %s" % can.id)

    print("\nREAD\n")
    can_clone = client.ReadCAN(
        pb.ReadCANArgs(
            id=can.id,
        )
    )
    print("got id: %s, contents = %s" %
          (can_clone.id, can_clone.contents.decode()))
    inf.run_inference_on_image()
