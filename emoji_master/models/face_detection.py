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

    def detect_faces_with_confidence(self, image_path):
        """带置信度的人脸检测 - 紧密裁剪长方形区域"""
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

            # 紧密裁剪：只扩展很少部分确保包含完整面部特征
            expand_ratio = 0.02  # 只扩展2%
            expand_x = int(w * expand_ratio)
            expand_y = int(h * expand_ratio)

            x = max(0, x - expand_x)
            y = max(0, y - expand_y)
            w = min(image.shape[1] - x, w + 2 * expand_x)
            h = min(image.shape[0] - y, h + 2 * expand_y)

            # 直接使用检测到的长方形区域，不强制转为正方形
            # 裁剪长方形人脸区域
            face_crop = image[y:y + h, x:x + w]

            if face_crop.size == 0:
                return None, 0

            # 转换为PIL图像
            face_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))

            # 智能调整大小：保持宽高比，最长边不超过设定值
            max_size = getattr(Config, 'MAX_FACE_SIZE', 512)  # 默认最大512像素

            original_width, original_height = face_pil.size
            scale_factor = min(max_size / original_width, max_size / original_height)

            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

            face_resized = face_pil.resize((new_width, new_height), Image.LANCZOS)

            print(f"✅ 人脸裁剪: 位置({x},{y}), 原始尺寸({w}x{h})")
            print(f"✅ 调整后尺寸: {face_resized.size} (缩放因子: {scale_factor:.2f})")

            return face_resized, best_confidence

        except Exception as e:
            print(f"人脸检测错误: {str(e)}")
            return None, 0
