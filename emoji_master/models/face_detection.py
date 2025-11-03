import cv2
import numpy as np
from PIL import Image
import os

from config import Config


class FaceDetector:
    """人脸检测模块 - 使用OpenCV Haar级联分类器"""

    def __init__(self):
        # 加载OpenCV的人脸检测器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # 如果找不到默认的，尝试下载
        if self.face_cascade.empty():
            self._download_haar_cascade()

    def _download_haar_cascade(self):
        """下载Haar级联分类器文件"""
        import urllib.request
        url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml'
        local_file = 'haarcascade_frontalface_default.xml'

        if not os.path.exists(local_file):
            print("下载人脸检测模型...")
            urllib.request.urlretrieve(url, local_file)

        self.face_cascade = cv2.CascadeClassifier(local_file)

    def detect_and_crop_face(self, image_path):
        """检测并裁剪人脸 - 只保留面部区域，背景透明"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return None

            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 检测人脸
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(Config.MIN_FACE_SIZE, Config.MIN_FACE_SIZE),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) == 0:
                return None

            # 选择最大的人脸
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = faces[0]

            # 只裁剪精确的面部区域
            face_crop = image[y:y + h, x:x + w]

            if face_crop.size == 0:
                return None

            # 创建RGBA图像（带透明通道）
            face_rgba = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGBA)

            # 创建椭圆掩码
            mask = np.zeros((h, w), dtype=np.uint8)
            center_x, center_y = w // 2, h // 2
            radius_x, radius_y = int(w * 0.45), int(h * 0.45)

            # 绘制椭圆（填充白色）
            cv2.ellipse(mask, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, 255, -1)

            # 将椭圆外部的alpha通道设置为0（完全透明）
            face_rgba[:, :, 3] = mask

            # 转换为PIL图像
            face_pil = Image.fromarray(face_rgba)

            # 调整尺寸
            face_resized = face_pil.resize(Config.FACE_SIZE, Image.LANCZOS)

            return face_resized

        except Exception as e:
            print(f"人脸检测错误: {str(e)}")
            return None

    def detect_faces_with_confidence(self, image_path):
        """带置信度的人脸检测（增强版本）- 只保留面部区域，背景透明"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None, 0

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 使用多个参数检测，选择最好的结果
            faces_params = [
                {'scaleFactor': 1.1, 'minNeighbors': 3, 'minSize': (30, 30)},
                {'scaleFactor': 1.05, 'minNeighbors': 5, 'minSize': (50, 50)},
                {'scaleFactor': 1.2, 'minNeighbors': 7, 'minSize': (70, 70)}
            ]

            best_face = None
            best_confidence = 0

            for params in faces_params:
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=params['scaleFactor'],
                    minNeighbors=params['minNeighbors'],
                    minSize=params['minSize'],
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                if len(faces) > 0:
                    # 计算置信度（基于人脸大小和检测参数）
                    face = max(faces, key=lambda x: x[2] * x[3])
                    confidence = (face[2] * face[3]) / (image.shape[0] * image.shape[1])

                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_face = face

            if best_face is None:
                return None, 0

            x, y, w, h = best_face

            # 只裁剪精确的面部区域
            face_crop = image[y:y + h, x:x + w]

            if face_crop.size == 0:
                return None, 0

            # 创建RGBA图像（带透明通道）
            face_rgba = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGBA)

            # 创建椭圆掩码
            mask = np.zeros((h, w), dtype=np.uint8)
            center_x, center_y = w // 2, h // 2
            radius_x, radius_y = int(w * 0.45), int(h * 0.45)

            # 绘制椭圆（填充白色）
            cv2.ellipse(mask, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, 255, -1)

            # 将椭圆外部的alpha通道设置为0（完全透明）
            face_rgba[:, :, 3] = mask

            # 转换为PIL图像
            face_pil = Image.fromarray(face_rgba)
            face_resized = face_pil.resize(Config.FACE_SIZE, Image.LANCZOS)

            return face_resized, best_confidence

        except Exception as e:
            print(f"增强人脸检测错误: {str(e)}")
            return None, 0
