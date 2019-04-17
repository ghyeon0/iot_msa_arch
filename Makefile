SERVER:="$$SERVER_IP"

build-server:
	docker build -t grpc-server server
run-server:
	docker run --rm --name grpc-server -p 6000:6000 grpc-server
build-test-client:
	docker build -t grpc-test-client test_client
run-test-client:
	docker run --rm -e SERVER_IP=$(SERVER) grpc-test-client
build-tx2-client:
	docker build -t tx2-client tx2_client
run-tx2-client:
	tx2-docker run -it -e SERVER_IP=$(SERVER) tx2-client /bin/bash
