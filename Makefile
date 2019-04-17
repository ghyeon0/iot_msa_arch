SERVER:="$$SERVER_IP"

run-server:
	docker build -t grpc-server server
	docker run --rm --name grpc-server -p 6000:6000 grpc-server
run-client:
	docker build -t grpc-test-client test_client
	docker run --rm -e SERVER_IP=$(SERVER) grpc-test-client
