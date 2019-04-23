import numpy as np
import tensorflow as tf
import time
import os
import random
import sys
import canrpc_pb2 as pb
import canrpc_pb2_grpc as rpcservice
import grpc


class Job1:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.channel = grpc.insecure_channel(self.server_ip+':6000')
        self.client = rpcservice.CANRPCServiceStub(self.channel)
        self.model_full_path = '/usr/src/app/j1/signimages.pb'
        self.labels_full_path = '/usr/src/app/j1/output_labels.txt'
        self.sign_images = []

    def main(self):
        try:
            BASE_PATH = sys.argv[1]
        except:
            BASE_PATH = input("Input Image File Path: ")
        self.init_datas(BASE_PATH)
        self.run_inference_on_image()
        
    def init_datas(self, base_path):
        # imagePath = '/tmp/pass_left.jpg'                                      # 추론을 진행할 이미지 경로
        # modelFullPath = '/usr/src/app/j1/signimages.pb'                                      # 읽어들일 graph 파일 경로
        # labelsFullPath = '/usr/src/app/j1/output_labels.txt'                                   # 읽어들일 labels 파일 경로

        # sign_images = []

        for path in os.listdir(base_path):
            for f in os.listdir(base_path + "/" + path):
                self.sign_images.append(base_path + "/" + path + "/" + f)

    def get_random_photo(self):
        return self.sign_images[random.randint(0, len(self.sign_images) - 1)]

    def run_inference_on_image(self):
        answer = None

        # init_datas()

        # 저장된(saved) GraphDef 파일로부터 graph를 생성한다.
        with tf.gfile.FastGFile(self.model_full_path, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        # channel = grpc.insecure_channel(server_ip+':6000')
        # client = rpcservice.CANRPCServiceStub(channel)

        with tf.Session() as sess:
            total = 0.0
            softmax_tensor = sess.graph.get_tensor_by_name('InceptionV1/Logits/Predictions/Softmax:0')
            for _ in range(10000):
                start = time.time()
                image_data = tf.gfile.FastGFile(self.get_random_photo(), 'rb').read()
                predictions = sess.run(softmax_tensor,
                                    {'input_image:0': image_data})
                predictions = np.squeeze(predictions)
                top_k = predictions.argsort()[-1]  # 가장 높은 확률을 가진 1개
                f = open(self.labels_full_path, 'rb')
                lines = f.readlines()
                labels = [str(w).replace("\n", "") for w in lines]
                # print(labels)
                print(labels[top_k], predictions[top_k])
                # for node_id in top_k:
                #     human_string = labels[node_id]
                #     score = predictions[node_id]
                #     print('%s (score = %.5f)' % (human_string, score))

                # answer = labels[top_k[0]]
                end = time.time()
                total += end - start
                print("\nSEND\n")
                can = self.client.SendCAN(
                        pb.SendCANArgs(
                        contents=bytes(labels[top_k].encode()),
                    )
                )
                print("can created with id: %s" % can.id)

                print("\nREAD\n")
                can_clone = self.client.ReadCAN(
                    pb.ReadCANArgs(
                        id=can.id,
                    )
                )
                
                print("got id: %s, contents = %s" %
                    (can_clone.id, can_clone.contents.decode()))
                # print(end - start)
            print(total / 10000)
            return answer


if __name__ == "__main__":
    server_ip = os.getenv('SERVER_IP')
    
    if server_ip is None:
        print('server ip not defined')
        sys.exit(1)
	
    # channel = grpc.insecure_channel(server_ip+':6000')
    # client = rpcservice.CANRPCServiceStub(channel)

    # print("\nSEND\n")
    # can = client.SendCAN(
    #     pb.SendCANArgs(
    #         contents=bytes(b'hello'),
    #     )
    # )
    # print("can created with id: %s" % can.id)

    # print("\nREAD\n")
    # can_clone = client.ReadCAN(
    #     pb.ReadCANArgs(
    #         id=can.id,
    #     )
    # )
    # print("got id: %s, contents = %s" %
    #       (can_clone.id, can_clone.contents.decode()))
    job1 = Job1(server_ip)
    job1.main()
    # inf.run_inference_on_image(server_ip, channel)
