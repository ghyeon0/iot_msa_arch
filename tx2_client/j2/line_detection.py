import cv2 # opencv 사용
import numpy as np
import canrpc_pb2 as pb
import canrpc_pb2_grpc as rpcservice
import grpc


class Job2:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.channel = grpc.insecure_channel(self.server_ip+':6000')
        self.client = rpcservice.CANRPCServiceStub(self.channel)

    def grayscale(self, img): # 흑백이미지로 변환
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    def canny(self, img, low_threshold, high_threshold): # Canny 알고리즘
        return cv2.Canny(img, low_threshold, high_threshold)

    def gaussian_blur(self, img, kernel_size): # 가우시안 필터
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    def region_of_interest(self, img, vertices, color3=(255,255,255), color1=255): # ROI 셋팅

        mask = np.zeros_like(img) # mask = img와 같은 크기의 빈 이미지
        
        if len(img.shape) > 2: # Color 이미지(3채널)라면 :
            color = color3
        else: # 흑백 이미지(1채널)라면 :
            color = color1
            
        # vertices에 정한 점들로 이뤄진 다각형부분(ROI 설정부분)을 color로 채움 
        cv2.fillPoly(mask, vertices, color)
        
        # 이미지와 color로 채워진 ROI를 합침
        ROI_image = cv2.bitwise_and(img, mask)
        return ROI_image

    def draw_lines(self, img, lines, color=[255, 0, 0], thickness=2): # 선 그리기
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), color, thickness)

    def draw_fit_line(self, img, lines, color=[255, 0, 0], thickness=10): # 대표선 그리기
            cv2.line(img, (lines[0], lines[1]), (lines[2], lines[3]), color, thickness)

    def hough_lines(self, img, rho, theta, threshold, min_line_len, max_line_gap): # 허프 변환
        lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
        #line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
        #draw_lines(line_img, lines)

        return lines

    def weighted_img(self, img, initial_img, α=1, β=1., λ=0.): # 두 이미지 operlap 하기
        return cv2.addWeighted(initial_img, α, img, β, λ)

    def get_fitline(self, img, f_lines): # 대표선 구하기   
        try:
            lines = np.squeeze(f_lines)
            lines = lines.reshape(lines.shape[0]*2,2)
            # rows, cols = img.shape[:2]
            output = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01)
            vx, vy, x, y = output[0], output[1], output[2], output[3]
            x1, y1 = int(((img.shape[0]-1)-y)/vy*vx + x) , img.shape[0]-1
            x2, y2 = int(((img.shape[0]/2+100)-y)/vy*vx + x) , int(img.shape[0]/2+100)
        except:
            result = [0, 0, 0, 0]
        else:
            result = [x1,y1,x2,y2]
        return result

    def calc_average(self, lst):
        total = sum(lst)
        return total // len(lst)

    def main(self):
        capture = cv2.VideoCapture('./j2/challenge.mp4')
        # capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        left_average_value_first = []
        right_average_value_first = []
        left_average_value_second = []
        right_average_value_second = []

        while (capture.isOpened()):
            # image = cv2.imread('slope_test.jpg') # 이미지 읽기
            ret, image = capture.read()
            if not ret or image is None:
                capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            height, width = image.shape[:2] # 이미지 높이, 너비
            gray_img = self.grayscale(image) # 흑백이미지로 변환
            blur_img = self.gaussian_blur(gray_img, 3) # Blur 효과
            canny_img = self.canny(blur_img, 70, 210) # Canny edge 알고리즘
            vertices = np.array([[(50,height),(width/2-45, height/2+60), (width/2+45, height/2+60), (width-50,height)]], dtype=np.int32)
            ROI_img = self.region_of_interest(canny_img, vertices) # ROI 설정
            line_arr = self.hough_lines(ROI_img, 1, 1 * np.pi/180, 30, 10, 20) # 허프 변환
            line_arr = np.squeeze(line_arr)

            # 기울기 구하기
            slope_degree = (np.arctan2(line_arr[:,1] - line_arr[:,3], line_arr[:,0] - line_arr[:,2]) * 180) / np.pi

            # 수평 기울기 제한
            line_arr = line_arr[np.abs(slope_degree)<160]
            slope_degree = slope_degree[np.abs(slope_degree)<160]

            # 수직 기울기 제한
            line_arr = line_arr[np.abs(slope_degree)>95]
            slope_degree = slope_degree[np.abs(slope_degree)>95]

            # 필터링된 직선 버리기
            L_lines, R_lines = line_arr[(slope_degree>0),:], line_arr[(slope_degree<0),:]
            temp = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
            L_lines, R_lines = L_lines[:,None], R_lines[:,None]

            # 왼쪽, 오른쪽 각각 대표선 구하기
            left_fit_line = self.get_fitline(image,L_lines)
            right_fit_line = self.get_fitline(image,R_lines)

            if 0 not in left_fit_line and 0 not in right_fit_line:
                left_average_value_first.append(left_fit_line[0])
                right_average_value_first.append(right_fit_line[0])
                left_average_value_second.append(left_fit_line[2])
                right_average_value_second.append(right_fit_line[2])

                if len(left_average_value_first) > 5:
                    left_average_value_first.pop(0)
                    right_average_value_first.pop(0)
                    left_average_value_second.pop(0)
                    right_average_value_second.pop(0)
                # center_position = self.calc_average(left_fit_line[0])
                # print(left_fit_line, right_fit_line)
                center_position = (((self.calc_average(left_average_value_first) + self.calc_average(right_average_value_first)) // 2)
                                 + ((self.calc_average(left_average_value_second) + self.calc_average(right_average_value_second)) // 2)) // 2
                # print(center_position)
                print("\nSEND\n")
                can = self.client.SendCAN(
                        pb.SendCANArgs(
                        contents=bytes(str(center_position).encode()),
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

            # 대표선 그리기
            try:
                self.draw_fit_line(temp, left_fit_line)
                self.draw_fit_line(temp, right_fit_line)
            except:
                pass
            else:
                result = self.weighted_img(temp, image) # 원본 이미지에 검출된 선 overlap
            # cv2.imshow('result',result) # 결과 이미지 출력
            if cv2.waitKey(1) > 0: break

        capture.release()
        # cv2.destoryAllWindows()        
        
