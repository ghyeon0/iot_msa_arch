package main

import (
	"context"
	"errors"
	"log"
	"github.com/rs/xid"
)

var errCANNotFound = errors.New("failed to find data")

type RPCServer struct {
	canList map[string]CAN
}

func newRPCServer() *RPCServer {
	return &RPCServer{
		canList: make(map[string]CAN),
	}
}

func (s *RPCServer) SendCAN(ctx context.Context, args *SendCANArgs) (*CAN, error) {
	log.Println("got SendCAN request")

	can, err := newCAN(args.GetContents())

	if err != nil {
		return nil, err
	}

	s.canList[can.GetId()] = *can

	return can, nil
}

func (s *RPCServer) ReadCAN(ctx context.Context, args *ReadCANArgs) (*CAN, error) {
	log.Println("got ReadCAN request")

	can, _ := s.canList[args.GetId()]

	return &can, nil
}

func newCAN(contents []byte) (*CAN, error){
	return &CAN{
		Id:      xid.New().String(),
		Contents:     contents,
	}, nil
}
