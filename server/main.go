package main

import (
	"log"
	"net"
	"fmt"

	"google.golang.org/grpc"
)

func main() {
	fmt.Printf("-----start manage server-----\n")
	listener, err := net.Listen("tcp", ":6000")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	grpcServer := grpc.NewServer()
	RegisterCANRPCServiceServer(grpcServer, newRPCServer())

	grpcServer.Serve(listener)
}

