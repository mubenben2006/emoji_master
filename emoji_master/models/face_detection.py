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
        """检测并裁剪人脸"""
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

            # 扩展边界以确保完整人脸
            margin_x = int(w * 0.2)
            margin_y = int(h * 0.2)

            height, width = image.shape[:2]
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(width, x + w + margin_x)
            y2 = min(height, y + h + margin_y)

            # 裁剪人脸
            face_crop = image[y1:y2, x1:x2]

            if face_crop.size == 0:
                return None

            # 转换为RGB并调整尺寸
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            face_resized = face_pil.resize(Config.FACE_SIZE, Image.LANCZOS)

            return face_resized

        except Exception as e:
            print(f"人脸检测错误: {str(e)}")
            return None

    def detect_faces_with_confidence(self, image_path):
        """带置信度的人脸检测（增强版本）"""
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

            # 扩展边界
            margin_x = int(w * 0.15)
            margin_y = int(h * 0.15)

            height, width = image.shape[:2]
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(width, x + w + margin_x)
            y2 = min(height, y + h + margin_y)

            face_crop = image[y1:y2, x1:x2]

            if face_crop.size == 0:
                return None, 0

            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_pil = Image.fromarray(face_rgb)
            face_resized = face_pil.resize(Config.FACE_SIZE, Image.LANCZOS)

            return face_resized, best_confidence

        except Exception as e:
            print(f"增强人脸检测错误: {str(e)}")
            return None, 0