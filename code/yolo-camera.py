import cv2
import numpy as np
import time

#email
import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

host = 'smtp.qq.com'  # 发件人邮箱的SMTP服务器
sender = '409054990@qq.com'  # 发件人邮箱账号
password = 'zlygsdzqkpsnbgbb'  # 发件人邮箱密码（不是qq密码，通过设置--》账户--》开启--》授权码）
receivers = ['849087739@qq.com']  # 接收人邮箱账号（可以多个，逗号隔开）


def yolo():
    # 下载权重文件、配置文件
    net = cv2.dnn.readNet("./deepsort/detector/YOLOv3/weight/yolov3.weights", "./deepsort/detector/YOLOv3/cfg/yolo_v3.cfg")
    classes = []

    with open("./deepsort/detector/YOLOv3/cfg/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    # 输入待检测视频、或打开摄像头实时检测
    # cap = cv2.VideoCapture(0) # 参数为0是打开摄像头，用摄像头实时检测
    cap = cv2.VideoCapture(0)  # 参数为文件名表示打开视频

    font = cv2.FONT_HERSHEY_PLAIN
    starting_time = time.time()
    frame_id = 0
    while True:
        _, frame = cap.read()
        frame_id += 1

        height, width, channels = frame.shape

        # 检测对象
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(output_layers)

        # 在屏幕上显示信息
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.2:
                    # 目标检测
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # 绘制矩形框
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = confidences[i]
                color = colors[class_ids[i]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)
                if label == 'dog':
                    cv2.imwrite('./detect_Image/dog.jpg', frame)
                    try:   
                        # 创建并登录SMTP服务器
                        # 创建多形式组合邮件
                        msg = MIMEMultipart('mixed')
                        
                        msg['From'] = formataddr(['dddd', sender])  # 发件人邮箱昵称、发件人邮箱账号
                        msg['To'] = formataddr(['Admin', ','.join(receivers)])  # 收件人邮箱昵称、收件人邮箱账号
                        # msg['To'] = ','.join(receivers)
                        msg['Subject'] = "Found a dog"  # 邮件主题

                        ######## 添加附件- 图片
                        att_img2 = MIMEText(open(r'E:\\大学\\软件工程课设\22 图像识别处理系统 颜劭铭\\代码-V1\detect_Image\\dog.jpg', 'rb').read(), 'base64', 'utf-8')
                        att_img2['Content-disposition'] = 'attachment;filename="dog.jpg"'
                        msg.attach(att_img2)# 添加图片文件到邮件-附件中去
                        server = smtplib.SMTP_SSL(host, 465)  # 创建一个STMP对象，SSL加密(也可选择明文发送server = smtplib.SMTP(host, 25))
                        server.login(sender, password)  # 登陆需要认证的SMTP服务器（发件人邮箱账号、密码）
                        # 发送邮件
                        server.sendmail(sender, receivers, msg.as_string())  # 发件人邮箱账号、收件人邮箱账号、发送邮件内容，as_string()是将msg(MIMEText对象或者MIMEMultipart对象)变为str
                        server.quit()   # 断开STMP服务器链接
                        print ('邮件发送成功！')
                    except smtplib.SMTPException as e:
                        print ('Error: 邮件发送失败！', e)
                elif label == 'cat':
                    cv2.imwrite('./detect_Image/cat.jpg', frame)
                    try:   
                        # 创建并登录SMTP服务器
                        # 创建多形式组合邮件
                        msg = MIMEMultipart('mixed')
                        
                        msg['From'] = formataddr(['dddd', sender])  # 发件人邮箱昵称、发件人邮箱账号
                        msg['To'] = formataddr(['Admin', ','.join(receivers)])  # 收件人邮箱昵称、收件人邮箱账号
                        # msg['To'] = ','.join(receivers)
                        msg['Subject'] = "Found a cat"  # 邮件主题

                        ######## 添加附件- 图片
                        att_img2 = MIMEText(open(r'E:\\大学\\软件工程课设\22 图像识别处理系统 颜劭铭\\代码-V1\detect_Image\\cat.jpg', 'rb').read(), 'base64', 'utf-8')
                        att_img2['Content-disposition'] = 'attachment;filename="cat.jpg"'
                        msg.attach(att_img2)# 添加图片文件到邮件-附件中去
                        server = smtplib.SMTP_SSL(host, 465)  # 创建一个STMP对象，SSL加密(也可选择明文发送server = smtplib.SMTP(host, 25))
                        server.login(sender, password)  # 登陆需要认证的SMTP服务器（发件人邮箱账号、密码）
                        # 发送邮件
                        server.sendmail(sender, receivers, msg.as_string())  # 发件人邮箱账号、收件人邮箱账号、发送邮件内容，as_string()是将msg(MIMEText对象或者MIMEMultipart对象)变为str
                        server.quit()   # 断开STMP服务器链接
                        print ('邮件发送成功！')
                    except smtplib.SMTPException as e:
                        print ('Error: 邮件发送失败！', e)
                elif label == 'bird':
                    cv2.imwrite('./detect_Image/bird.jpg', frame)
                    try:   
                        msg = MIMEMultipart('mixed')
                        
                        msg['From'] = formataddr(['dddd', sender])  # 发件人邮箱昵称、发件人邮箱账号
                        msg['To'] = formataddr(['Admin', ','.join(receivers)])  # 收件人邮箱昵称、收件人邮箱账号
                        # msg['To'] = ','.join(receivers)
                        msg['Subject'] = "Found a bird"  # 邮件主题

                        ######## 添加附件- 图片
                        att_img2 = MIMEText(open(r'E:\\大学\\软件工程课设\22 图像识别处理系统 颜劭铭\\代码-V1\detect_Image\\bird.jpg', 'rb').read(), 'base64', 'utf-8')
                        att_img2['Content-disposition'] = 'attachment;filename="bird.jpg"'
                        msg.attach(att_img2)# 添加图片文件到邮件-附件中去
                        server = smtplib.SMTP_SSL(host, 465)  # 创建一个STMP对象，SSL加密(也可选择明文发送server = smtplib.SMTP(host, 25))
                        server.login(sender, password)  # 登陆需要认证的SMTP服务器（发件人邮箱账号、密码）
                        # 发送邮件
                        server.sendmail(sender, receivers, msg.as_string())  # 发件人邮箱账号、收件人邮箱账号、发送邮件内容，as_string()是将msg(MIMEText对象或者MIMEMultipart对象)变为str
                        server.quit()   # 断开STMP服务器链接
                        print ('邮件发送成功！')
                    except smtplib.SMTPException as e:
                        print ('Error: 邮件发送失败！', e)

        elapsed_time = time.time() - starting_time
        fps = frame_id / elapsed_time
        cv2.putText(frame, "FPS: " + str(round(fps, 2)), (10, 50), font, 4, (0, 0, 0), 3)
        cv2.imshow("Image", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
yolo()