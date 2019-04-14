import canrpc_pb2 as pb
import canrpc_pb2_grpc as rpcservice
import grpc


if __name__ == "__main__":
    channel = grpc.insecure_channel('grpc-server:6000')
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
