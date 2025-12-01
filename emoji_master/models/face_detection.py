import cv2
import numpy as np
from PIL import Image
import os
from config import Config


class FaceDetector:
    """人脸检测模块 - 基于椭圆裁剪的可靠版本"""

    def __init__(self):
        # 加载基础人脸检测器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # 加载可用的五官检测器
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

        # 鼻子和嘴巴检测器初始化为None
        self.nose_cascade = None
        self.mouth_cascade = None

        # 检查并初始化所有级联器
        self._initialize_cascades()
        print("✅ 人脸检测器初始化完成")

    def _initialize_cascades(self):
        """初始化级联分类器"""
        print("🔧 初始化面部特征检测器...")

        # 可选的级联器
        optional_cascades = {
            'nose': 'haarcascade_mcs_nose.xml',
            'mouth': 'haarcascade_smile.xml'
        }

        # 检查可选级联器，如果不存在就跳过
        for name, filename in optional_cascades.items():
            cascade_path = cv2.data.haarcascades + filename
            if os.path.exists(cascade_path):
                if name == 'nose':
                    self.nose_cascade = cv2.CascadeClassifier(cascade_path)
                elif name == 'mouth':
                    self.mouth_cascade = cv2.CascadeClassifier(cascade_path)
                print(f"✅ {name}检测器: {filename}")
            else:
                print(f"⚠️ {name}检测器不可用，将使用估算位置: {filename}")

    def detect_face(self, image_path):
        """主检测方法 - 返回人脸图像、置信度和椭圆信息"""
        try:
            print(f"🔍 开始人脸检测: {image_path}")

            # 读取图像
            image = cv2.imread(str(image_path))
            if image is None:
                print("❌ 无法读取图像")
                return None, 0, None

            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 图像增强
            gray = cv2.equalizeHist(gray)

            # 首先检测人脸区域
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60)  # 适当的最小尺寸
            )

            if len(faces) == 0:
                print("❌ 未检测到人脸，尝试放宽参数...")
                # 尝试放宽参数
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.05,
                    minNeighbors=3,
                    minSize=(40, 40)
                )

            if len(faces) == 0:
                print("❌ 最终未检测到人脸")
                return None, 0, None

            # 选择最大的人脸
            faces = sorted(faces, key=lambda rect: rect[2] * rect[3], reverse=True)
            x, y, w, h = faces[0]
            print(f"✅ 检测到人脸: 位置({x},{y}), 尺寸({w}x{h})")

            # 在人脸区域内检测五官
            face_roi_gray = gray[y:y + h, x:x + w]

            # 检测各个面部特征
            features = self._detect_all_features(face_roi_gray, x, y, w, h)

            # 计算整体置信度
            confidence = self._calculate_confidence(features, w * h, image.shape[0] * image.shape[1])

            # 获取椭圆裁剪的人脸区域
            face_region, ellipse_info = self._get_ellipse_face_region_with_info(image, (x, y, w, h), features)

            if face_region is None:
                print("❌ 椭圆裁剪失败，使用矩形裁剪")
                face_region = image[y:y + h, x:x + w]
                # 创建默认椭圆信息
                center_x = x + w // 2
                center_y = y + h // 2
                ellipse_width = int(w * 0.9)
                ellipse_height = int(h * 0.8)
                ellipse_info = {
                    'center': (center_x, center_y),
                    'size': (ellipse_width, ellipse_height),
                    'image_size': image.shape[:2],
                    'face_rect': (x, y, w, h)
                }

            # 转换为PIL图像
            face_pil = Image.fromarray(cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB))

            # 调整大小
            face_resized = self._resize_face_image(face_pil, ellipse_info)

            print(f"🎯 人脸检测完成: 尺寸{face_resized.size}, 置信度{confidence:.3f}")
            return face_resized, confidence, ellipse_info

        except Exception as e:
            print(f"❌ 人脸检测过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, 0, None

    def _detect_all_features(self, face_gray, face_x, face_y, face_w, face_h):
        """检测所有可用的面部特征"""
        features = {
            'eyes': [],
            'nose': [],
            'mouth': []
        }

        # 检测眼睛（通常最可靠）
        try:
            eyes = self.eye_cascade.detectMultiScale(
                face_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(20, 20)
            )
            for (ex, ey, ew, eh) in eyes:
                # 调整到原图坐标
                abs_x = face_x + ex
                abs_y = face_y + ey
                features['eyes'].append((abs_x, abs_y, ew, eh))
            print(f"👀 检测到 {len(features['eyes'])} 个眼睛")
        except Exception as e:
            print(f"⚠️ 眼睛检测失败: {e}")

        # 如果鼻子检测器可用则检测鼻子
        if self.nose_cascade is not None:
            try:
                noses = self.nose_cascade.detectMultiScale(
                    face_gray,
                    scaleFactor=1.1,
                    minNeighbors=5
                )
                for (nx, ny, nw, nh) in noses:
                    abs_x = face_x + nx
                    abs_y = face_y + ny
                    features['nose'].append((abs_x, abs_y, nw, nh))
                print(f"👃 检测到 {len(features['nose'])} 个鼻子")
            except Exception as e:
                print(f"⚠️ 鼻子检测失败: {e}")

        # 如果嘴巴检测器可用则检测嘴巴
        if self.mouth_cascade is not None:
            try:
                # 在脸部下半部分检测嘴巴
                mouth_region = face_gray[int(face_gray.shape[0] * 0.6):, :]
                mouths = self.mouth_cascade.detectMultiScale(
                    mouth_region,
                    scaleFactor=1.1,
                    minNeighbors=15,
                    minSize=(30, 15)
                )
                for (mx, my, mw, mh) in mouths:
                    abs_x = face_x + mx
                    abs_y = face_y + int(face_gray.shape[0] * 0.6) + my
                    features['mouth'].append((abs_x, abs_y, mw, mh))
                print(f"👄 检测到 {len(features['mouth'])} 个嘴巴")
            except Exception as e:
                print(f"⚠️ 嘴巴检测失败: {e}")

        return features

    def _get_ellipse_face_region_with_info(self, image, face_rect, features):
        """获取椭圆面部区域并返回椭圆信息"""
        try:
            x, y, w, h = face_rect

            # 计算椭圆参数
            center_x = x + w // 2
            center_y = y + h // 2
            ellipse_width = int(w * 0.9)
            ellipse_height = int(h * 0.8)

            # 创建椭圆信息
            ellipse_info = {
                'center': (center_x, center_y),
                'size': (ellipse_width, ellipse_height),
                'image_size': image.shape[:2],
                'face_rect': (x, y, w, h)
            }

            # 计算裁剪区域
            roi_x = max(0, center_x - ellipse_width // 2)
            roi_y = max(0, center_y - ellipse_height // 2)
            roi_x2 = min(image.shape[1], center_x + ellipse_width // 2)
            roi_y2 = min(image.shape[0], center_y + ellipse_height // 2)

            # 裁剪区域
            cropped_region = image[roi_y:roi_y2, roi_x:roi_x2]

            # 创建椭圆遮罩
            height, width = cropped_region.shape[:2]
            rgba_image = np.zeros((height, width, 4), dtype=np.uint8)

            # 复制RGB通道
            rgba_image[:, :, :3] = cropped_region

            # 创建椭圆遮罩
            mask = np.zeros((height, width), dtype=np.uint8)
            center_local_x = width // 2
            center_local_y = height // 2

            cv2.ellipse(mask,
                        (center_local_x, center_local_y),
                        (ellipse_width // 2, ellipse_height // 2),
                        0, 0, 360, 255, -1)

            # 应用遮罩
            rgba_image[:, :, 3] = mask
            rgba_image[mask == 0] = [0, 0, 0, 0]

            print(f"✅ 椭圆裁剪完成 - 尺寸: {ellipse_width}x{ellipse_height}")
            return rgba_image, ellipse_info

        except Exception as e:
            print(f"⚠️ 椭圆裁剪失败: {e}")
            return None, None

    def _resize_face_image(self, face_image, ellipse_info):
        """调整人脸图像大小"""
        max_size = Config.MAX_FACE_SIZE
        original_width, original_height = face_image.size

        # 计算缩放比例
        if original_width > original_height:
            new_width = max_size
            new_height = int(original_height * max_size / original_width)
            scale_factor = max_size / original_width
        else:
            new_height = max_size
            new_width = int(original_width * max_size / original_height)
            scale_factor = max_size / original_height

        # 确保最小尺寸
        new_width = max(new_width, 100)
        new_height = max(new_height, 100)

        # 记录缩放因子
        ellipse_info['scale_factor'] = scale_factor
        ellipse_info['resized_size'] = (new_width, new_height)

        # 高质量重采样
        return face_image.resize((new_width, new_height), Image.LANCZOS)

    def _calculate_confidence(self, features, face_area, image_area):
        """计算检测置信度"""
        # 基础置信度基于人脸大小
        area_ratio = face_area / image_area
        base_confidence = min(area_ratio * 8, 0.6)

        # 根据检测到的特征数量增加置信度
        feature_count = sum(len(features[key]) for key in features)

        if feature_count >= 3:
            feature_bonus = 0.3
        elif feature_count >= 2:
            feature_bonus = 0.2
        elif feature_count >= 1:
            feature_bonus = 0.1
        else:
            feature_bonus = 0.0

        confidence = min(base_confidence + feature_bonus, 1.0)

        print(f"📊 置信度计算: 面积比例{area_ratio:.4f}, 特征数{feature_count}, 最终{confidence:.3f}")
        return confidence

    def apply_border_cleanup(self, image, ellipse_info, border_pixels):
        """应用边界清理 - 兼容旧版本"""
        try:
            if border_pixels <= 0:
                return image

            print(f"🧹 应用边界清理: {border_pixels}像素")

            # 如果图像不是RGBA，先转换为RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')

            img_array = np.array(image)
            height, width = img_array.shape[:2]

            # 计算缩放后的椭圆参数
            scale_factor = ellipse_info.get('scale_factor', 1.0)
            original_size = ellipse_info['size']

            scaled_width = int(original_size[0] * scale_factor) - border_pixels * 2
            scaled_height = int(original_size[1] * scale_factor) - border_pixels * 2
            scaled_width = max(20, scaled_width)
            scaled_height = max(20, scaled_height)

            print(f"📐 缩放后椭圆尺寸: {scaled_width}x{scaled_height}")

            # 创建椭圆遮罩
            center_x, center_y = width // 2, height // 2
            mask = np.zeros((height, width), dtype=np.uint8)

            # 绘制椭圆（内缩边界清理像素）
            cv2.ellipse(mask,
                        (center_x, center_y),
                        (scaled_width // 2, scaled_height // 2),
                        0, 0, 360, 255, -1)

            # 应用遮罩：椭圆外完全透明，且RGB值设为0
            img_array[:, :, 3] = mask
            img_array[mask == 0] = [0, 0, 0, 0]

            print("✅ 边界清理完成")
            return Image.fromarray(img_array)

        except Exception as e:
            print(f"❌ 边界清理失败: {e}")
            return image

    # 向后兼容的方法 - 与原蓝图保持相同
    def detect_facial_features_with_confidence(self, image_path, border_cleanup_pixels=0):
        """向后兼容的旧方法名"""
        print("⚠️ 使用旧方法名 detect_facial_features_with_confidence")
        return self.detect_face(image_path)

    def detect_and_crop_face(self, image_path, border_cleanup_pixels=0):
        """另一个向后兼容的方法"""
        print("⚠️ 使用旧方法名 detect_and_crop_face")
        return self.detect_face(image_path)
