# Image recognition processing system

## 1. 项目介绍

- 该项目借助 Flask 框架，对于 YOLO 和 OpenCV 等代码进行整合，在 Web 端实现了注册登录，后台管理，人脸识别，图像及视频识别等功能。

## 2.权重文件

- 因为图像识别和摄像头识别使用的是YOLOv3，视频识别使用的是YOLOv4，所以把这些权重文件都上传到了百度网盘

- 链接：https://pan.baidu.com/s/1KtR1l4gdR5sbTxbWHLb83g 

- 提取码：0801 

- 其中YOLOv4需要做的是

- ```
  cd code
  cd deepsort
  cd detector
  cd YOLOv4
  ```
  
- 然后将网盘中的对应YOLOv4文件夹中的内容存放进去

- 而YOLOv3需要做的是

- ```
  cd code
  cd deepsort
  cd detector
  cd YOLOv3
  cd weight
  ```
  
- 然后将网盘中的对应YOLOv3文件夹中的内容存放进去
- 至此整个文件可以开始运行

## 3. 配置环境

```
pip install -r requirements.txt
```

## 4. 操作方法

- 先创立一个管理员账号admin
- 管理员界面在登录后更改后缀为/admin即可进入
- 后续可以随意创建账号
- 上传头像储存至./face/images文件夹
- 注意头像文件名需要和用户名一致
- 摄像头识别可使用ESC关闭

## 5. 演示视频

以下为演示视频，这是较早版本，后续的登录注册页面重新进行了修改，具体可观看报告中的截图。

[![Watch the video](https://github.com/Steven-Ysm/Comprehensive-Course-Design-of-Software-Engineering/blob/master/video/%E6%BC%94%E7%A4%BA%E8%A7%86%E9%A2%91.mp4）


## 6. 参考来源

本项目主要参考两个来源：

+ <https://blog.csdn.net/qq_34717531/article/details/125095246?spm=1001.2014.3001.5502%E3%80%82>
+ <https://download.csdn.net/download/weixin_44441567/85020472?spm=1001.2014.3001.5503>

