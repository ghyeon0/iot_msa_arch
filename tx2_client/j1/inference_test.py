import numpy as np
import tensorflow as tf
import time
import os
import random
import sys


def init_datas():
    global modelFullPath, labelsFullPath, sign_images
    # imagePath = '/tmp/pass_left.jpg'                                      # 추론을 진행할 이미지 경로
    modelFullPath = '/usr/src/app/j1/signimages.pb'                                      # 읽어들일 graph 파일 경로
    labelsFullPath = '/usr/src/app/j1/output_labels.txt'                                   # 읽어들일 labels 파일 경로

    sign_images = []
    try:
        BASE_PATH = sys.argv[1]
    except:
        BASE_PATH = input("Input Image File Path: ")

    for path in os.listdir(BASE_PATH):
        for f in os.listdir(BASE_PATH + "/" + path):
            sign_images.append(BASE_PATH + "/" + path + "/" + f)


def get_random_photo():
    global sign_images
    return sign_images[random.randint(0, len(sign_images) - 1)]

def run_inference_on_image():
    global modelFullPath, labelsFullPath, sign_images
    answer = None

    init_datas()
    # if not tf.gfile.Exists(imagePath):
    #     tf.logging.fatal('File does not exist %s', imagePath)
    #     return answer

    # 저장된(saved) GraphDef 파일로부터 graph를 생성한다.
    with tf.gfile.FastGFile(modelFullPath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
        total = 0.0
        softmax_tensor = sess.graph.get_tensor_by_name('InceptionV1/Logits/Predictions/Softmax:0')
        for _ in range(10000):
            start = time.time()
            image_data = tf.gfile.FastGFile(get_random_photo(), 'rb').read()
            predictions = sess.run(softmax_tensor,
                                {'input_image:0': image_data})
            predictions = np.squeeze(predictions)
            top_k = predictions.argsort()[-1]  # 가장 높은 확률을 가진 1개
            f = open(labelsFullPath, 'rb')
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
            print(end - start)
        print(total / 10000)
        return answer


#if __name__ == '__main__':
#    run_inference_on_image()
