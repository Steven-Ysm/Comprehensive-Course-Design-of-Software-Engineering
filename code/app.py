from flask import Flask,redirect, render_template, request, Response, url_for, make_response,jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_user  import login_required,UserManager,UserMixin,SQLAlchemyAdapter,current_user
from flask_migrate import  Migrate,MigrateCommand
from flask_script import Manager

from flask_admin import Admin, AdminIndexView
from flask_admin.menu import MenuLink
from flask_admin.contrib.sqla import  ModelView

from flask_mail import Mail,Message
from flask_socketio import SocketIO, emit
import io
from io import StringIO
import base64
from PIL import Image
import numpy as np
import datetime
from datetime  import timedelta
from face.detect import face_detect
import cv2
import time
from deepsort.detector import build_detector
from deepsort.deep_sort import build_tracker
from deepsort.detector.YOLOv3 import YOLOv3
import os

'''
图像识别
'''
yolo = YOLOv3(r"deepsort/detector/YOLOv3/cfg/yolo_v3.cfg", r"deepsort/detector/YOLOv3/weight/yolov3.weights",r"deepsort/detector/YOLOv3/cfg/coco.names")
detector = build_detector(use_cuda=False)
deepsort = build_tracker(use_cuda=False)

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


app = Flask(__name__)

'''
发邮件
'''

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '409054990@qq.com'       #发信人账号
app.config['MAIL_PASSWORD'] = 'zlygsdzqkpsnbgbb'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

'''
数据库账号密码
'''

app.config['SECRET_KEY'] = "thisisasecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/test'
app.config["CSRF_ENABLED"]=True
app.config['USER_ENABLE_EMAIL'] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True
app.config["SQLALCHEMY_COMMIT_TEARDOWN "]= True
db = SQLAlchemy(app)

socketio = SocketIO(app)

'''
数据库版本迁移
'''

manager=Manager(app)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)


'''邮件发送'''
with app.app_context():
    msg = Message('Alert', sender=app.config['MAIL_USERNAME'],
                      recipients=['849087739@qq.com']) #收件人为YSL
    msg.body = "警告，有非本单位人员到来"
    mail.send(msg)

'''
用户
'''

class User(db.Model,UserMixin):
    id = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(50),nullable = False , unique = True)
    password = db.Column(db.String(255),nullable = False ,server_default = '')
    active = db.Column(db.Boolean(),nullable = False)

'''
人脸识别记录
'''

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default = datetime.datetime.utcnow)

db_adapter = SQLAlchemyAdapter(db,User)

user_namager = UserManager(db_adapter,app)

db.create_all()

@app.route("/")
@login_required
def index():
    dat = datetime.date.today()
    record = Record.query.filter_by(username=current_user.username).filter(db.cast(Record.time, db.DATE) == dat).first()
    if record is None:
        return render_template('index.html', text = "今日未打卡，请点击人脸识别打卡进行打卡！")
    else:
        return render_template('index.html', text = "今日已打卡！")


@app.route("/daka")
@login_required
def daka():
    return render_template('daka.html')

@app.route("/record")
@login_required
def record():
    if current_user.username == 'admin':
        records = Record.query.all()
    else:
        records = Record.query.filter_by(username=current_user.username).all()
    # 时区+8
    for i in range(len(records)):
        records[i].time = records[i].time + timedelta(hours=8)
    return render_template('record.html', records = records)

@app.route("/baojin")
@login_required
def baojin():
    msg = Message('Alert', sender=app.config['MAIL_USERNAME'],
                  recipients=['849087739@qq.com'])
    msg.body = "警告，有非本单位人员到来"
    mail.send(msg)
    return render_template('baojin.html')

'''
人脸识别系统管理员后台
'''



class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated == True and current_user.username == 'admin':
            return True
        else:
            return False
        # return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect("/user/sign-in")

admin = Admin(app, name=u"图像识别处理系统管理员后台", index_view=MyAdminIndexView())
class MyUserView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect("user.sign_in")

admin.add_view(MyUserView(User,db.session, name="用户管理"))


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

admin.add_link(LogoutMenuLink(name='登出', category='', url="/user/sign-out"))

'''
人脸识别
'''

face_detector = face_detect()


@socketio.on('image')
@login_required
def image(data_image):
    sbuf = StringIO()
    sbuf.write(data_image)

    b = io.BytesIO(base64.b64decode(data_image))
    pimg = Image.open(b)
    pimg = pimg.convert('RGB')
    pimg = np.array(pimg)
    #
    #
    name = face_detector.detect(pimg)
    if name == current_user.username:
        # 打卡成功，记入数据库
        db.session.add(Record(username=current_user.username))
        db.session.commit()
        # 网页返回
        emit('name_back', True)
        emit('response_back', True)
        emit('name', name)
    else:
        emit('response_back', False)
        emit('name_back', False)
        emit('name', name)

'''
上传头像
'''

#设置允许的文件格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
 
app.send_file_max_age_default = timedelta(seconds=1)
 
@app.route('/upload', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']
 
        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
 
        user_input = request.form.get("name")
 
        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        filename = user_input + '.jpg'
 
        upload_path = os.path.join(basepath, './face/images',secure_filename(filename))  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
 
        image_data = open(upload_path, "rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response
    
    return render_template('upload.html')

'''
摄像头识别
'''
@app.route("/camera")
def camera():
    return render_template('camera.html')

@app.route("/programer", methods=['Get'])
def test():
    import os
    os.system("python   ./yolo-camera.py")
    return render_template('camera.html')

'''
视频识别
'''

#置信度和nms设置
confThreshold = 0.25
nmsThreshold = 0.4

class_names = []#初始化一个列表以存储类名
COLORS = [(0, 255, 255),(0,0,255), (255, 255, 0),(0, 255, 0), (255, 0, 0)]#颜色
color=(0,255,0)
color1=(0,0,255)
c=(0, 0, 0)

#模型参数

weights="./deepsort/detector/YOLOv4/yolov4.weights"
cfg="./deepsort/detector/YOLOv4/yolov4.cfg"
m="./deepsort/detector/YOLOv4/coco.names"
# 网络设置
net = cv2.dnn_DetectionModel(cfg, weights)
#GPU运行
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

net.setInputSize(608, 608)
net.setInputScale(1.0 / 255)
net.setInputSwapRB(True)
with open(m, "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

@app.route('/video', methods=['POST', 'GET'])
def upload_video():
    if request.method == 'POST':
        f = request.form.get("name")
        if len(f)==0:
            g = request.files['file']
            f = g.filename
            basepath = os.path.dirname(__file__)  # 当前文件所在路径
            # basepath = 'C:\\Users\\1\\Desktop\\test'
            upload_video_path = os.path.join(basepath,secure_filename(g.filename))
            upload_video_path = os.path.abspath(upload_video_path) # 将路径转换为绝对路径
            g.save(upload_video_path)
            f = upload_video_path

        return redirect(url_for('video_display',path = f))
    return render_template('video.html')


def gen_frames(path):  # generate frame by frame from camera
    count = 0
    dir = 0
    pTime = 0
    if path[0]!='r':
        path='/'+path
    camera = cv2.VideoCapture(path)
    #camera = cv2.VideoCapture("8.mp4")
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            start = time.time()
            classes, confidences, boxes = net.detect(frame, confThreshold, nmsThreshold)
            end = time.time()

            start_drawing = time.time()
            count=0
            for (classid, score, box) in zip(classes, confidences, boxes):
                
                label = "%s(%2.0f%%)" % (class_names[classid[0]], score*100)#标签置信度
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                left, top, width, height = box

                cv2.rectangle(frame, box, color1, 2)
                cv2.rectangle(frame, (left-1, top - labelSize[1]-5), (left + labelSize[0], top), color, cv2.FILLED)
                cv2.putText(frame, label, (left, top-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, c,2)
                count+=1
            end_drawing = time.time() 
            fps_label = "FPS: %.2f (excluding drawing time of %.2fms)" % (1 / (end - start),(end_drawing - start_drawing) * 1000)
            #print(fps_label)
            cv2.putText(frame,"Num: %s" % str(count),(100,150),cv2.FONT_HERSHEY_SIMPLEX,2,[255,255,0],3)
            cv2.putText(frame, fps_label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_display/<path:path>')
def video_display(path):
    return Response(gen_frames(path), mimetype='multipart/x-mixed-replace; boundary=frame')

'''
图像识别
'''
# 类名及文件名
class_names = [c.strip() for c in open(r'deepsort/detector/YOLOv3/cfg/coco.names').readlines()]

file_name = ['jpg','jpeg','png']


# API that returns image with detections on it
@app.route('/images', methods= ['POST'])
def get_image():
    image = request.files["images"]
    image_name = image.filename

    image.save(os.path.join(os.getcwd(), image_name))

    if image_name.split(".")[-1] in file_name:
        img = cv2.imread(image_name)
        h,w,_ = img.shape
        if h > 2000 or w > 2000:
            h = h // 2
            w = w // 2
            img = cv2.resize(img,(int(w),int(h)))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        bbox, cls_conf, cls_ids = yolo(img)
        from vizer.draw import draw_boxes as db
        if bbox is not None:
            img = db(img, bbox, cls_ids, cls_conf, class_name_map=class_names)
        img = img[:, :, (2, 1, 0)]
        _, img_encoded = cv2.imencode('.jpg', img)
        response = img_encoded.tobytes()
        os.remove(image_name)
        try:
            return Response(response=response, status=200, mimetype='image/jpg')
        except:
            return render_template('image.html')

@app.route('/image')
def upload_file():
   return render_template('image.html')


if __name__ == '__main__':
    app.run(debug=True,host='127.0.0.1',port='5000')