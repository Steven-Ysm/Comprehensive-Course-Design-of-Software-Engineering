import face_recognition
import cv2
import os


class face_detect():
    known_names = []
    known_encodings = []
    path = "./face/images/"

    def __init__(self):
        # 存储知道人名列表
        self.known_names = []
        # 存储知道的特征值
        self.known_encodings = []
        self.reload_images()


    def reload_images(self):
        for image_name in os.listdir(self.path):
            load_image = face_recognition.load_image_file(self.path + image_name)  # 加载图片
            image_face_encoding = face_recognition.face_encodings(load_image)[0]  # 获得128维特征值
            self.known_names.append(image_name.split(".")[0])
            self.known_encodings.append(image_face_encoding)


    def detect(self, rgb_frame):


        face_locations = face_recognition.face_locations(rgb_frame)  # 获得所有人脸位置
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)  # 获得人脸特征值
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_names[first_match_index]
                print(name)
                return name
        print("not found")
        return None
        # 打开摄像头，0表示内置摄像头
        # video_capture = cv2.VideoCapture(0)
        # process_this_frame = True
        # while True:
        #     ret, frame = video_capture.read()
        #     if ret == True:
        #         # opencv的图像是BGR格式的，而我们需要是的RGB格式的，因此需要进行一个转换。
        #         rgb_frame = frame[:, :, ::-1]
        #         if process_this_frame:
        #             face_locations = face_recognition.face_locations(rgb_frame)  # 获得所有人脸位置
        #             face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)  # 获得人脸特征值
        #             for face_encoding in face_encodings:
        #                 matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
        #                 if True in matches:
        #                     first_match_index = matches.index(True)
        #                     name = self.known_names[first_match_index]
        #                     print(name)
        #                     video_capture.release()
        #                     return name
        # video_capture.release()
        # cv2.destroyAllWindows()
        # return None




if __name__ == '__main__':
    detecter = face_detect()
    detecter.detect(None)