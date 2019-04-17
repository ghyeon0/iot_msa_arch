SERVER:="$$SERVER_IP"

build-server:
	docker build -t grpc-server server
run-server:
	docker run --rm --name grpc-server -p 6000:6000 grpc-server
build-client:
	docker build -t grpc-test-client test_client
run-client:
	docker run --rm -e SERVER_IP=$(SERVER) grpc-test-client
