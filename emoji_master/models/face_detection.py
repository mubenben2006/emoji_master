import cv2
import numpy as np
from PIL import Image, ImageDraw
import os
from config import Config


class FaceDetector:
    """五官检测模块 - 使用OpenCV Haar级联分类器检测面部特征"""

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

        # 检查并初始化所有级联器（跳过下载）
        self._initialize_cascades_skip_download()

    def _initialize_cascades_skip_download(self):
        """初始化级联分类器 - 跳过下载，直接使用可用的"""
        print("🔧 初始化面部特征检测器...")

        # 基础级联器（通常都可用）
        base_cascades = {
            'face': 'haarcascade_frontalface_default.xml',
            'eyes': 'haarcascade_eye.xml'
        }

        # 可选的级联器
        optional_cascades = {
            'nose': 'haarcascade_mcs_nose.xml',
            'mouth': 'haarcascade_smile.xml'
        }

        # 检查基础级联器
        for name, filename in base_cascades.items():
            cascade_path = cv2.data.haarcascades + filename
            if os.path.exists(cascade_path):
                print(f"✅ {name}检测器: {filename}")
            else:
                print(f"❌ {name}检测器缺失: {filename}")

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

    def detect_facial_features_with_confidence(self, image_path, border_cleanup_pixels=3):
        """检测面部五官 - 返回人脸图像和椭圆信息（不进行边界清理）"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                print("❌ 无法读取图像")
                return None, 0, None

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # 首先检测人脸区域
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )

            if len(faces) == 0:
                print("❌ 未检测到人脸")
                return None, 0, None

            # 选择最大的人脸
            x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
            print(f"✅ 检测到人脸: 位置({x},{y}), 尺寸({w}x{h})")

            # 在人脸区域内检测五官
            face_roi_gray = gray[y:y + h, x:x + w]

            # 检测各个面部特征
            features = self._detect_all_features(face_roi_gray, x, y, w, h)

            # 计算整体置信度
            confidence = self._calculate_confidence(features, w * h, image.shape[0] * image.shape[1])

            # 获取椭圆裁剪的面部特征区域（不进行边界清理）
            feature_region, ellipse_info = self._get_ellipse_face_region_with_info(
                image, (x, y, w, h), features, 0  # 这里传入0，表示不清理边界
            )

            if feature_region is None:
                print("❌ 椭圆裁剪失败，使用矩形裁剪")
                feature_region = image[y:y + h, x:x + w]
                # 创建默认椭圆信息
                center_x = x + w // 2
                center_y = y + h // 2
                ellipse_width = int(w * 0.9)
                ellipse_height = int(h * 0.8)
                ellipse_info = {
                    'center': (center_x, center_y),
                    'original_size': (ellipse_width, ellipse_height),
                    'border_cleanup': border_cleanup_pixels,  # 记录清理参数，但实际不应用
                    'image_size': image.shape[:2],  # (height, width)
                    'scale_factor': 1.0  # 初始缩放因子
                }

            # 转换为PIL图像
            feature_pil = Image.fromarray(cv2.cvtColor(feature_region, cv2.COLOR_BGR2RGB))

            # 计算缩放因子并记录
            max_size = getattr(Config, 'MAX_FACE_SIZE', 256)
            original_width, original_height = feature_pil.size

            # 保持宽高比调整大小
            if original_width > original_height:
                new_width = max_size
                new_height = int(original_height * max_size / original_width)
                scale_factor = max_size / original_width
            else:
                new_height = max_size
                new_width = int(original_width * max_size / original_height)
                scale_factor = max_size / original_height

            feature_resized = feature_pil.resize((new_width, new_height), Image.LANCZOS)

            # 更新椭圆信息中的缩放因子
            ellipse_info['scale_factor'] = scale_factor
            ellipse_info['resized_size'] = (new_width, new_height)

            print(f"✅ 椭圆面部特征检测完成 - 置信度: {confidence:.3f}")
            print(f"✅ 椭圆信息记录: 中心{ellipse_info['center']}, 原始尺寸{ellipse_info['original_size']}")
            print(f"✅ 缩放因子: {scale_factor:.4f}, 最终特征尺寸: {feature_resized.size}")

            return feature_resized, confidence, ellipse_info

        except Exception as e:
            print(f"❌ 面部特征检测错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, 0, None

    def _get_ellipse_face_region_with_info(self, image, face_rect, features, border_pixels=0):
        """获取椭圆面部区域并返回椭圆信息（可选择是否清理边界）"""
        try:
            x, y, w, h = face_rect

            # 计算椭圆参数
            center_x = x + w // 2
            center_y = y + h // 2
            ellipse_width = int(w * 0.9)
            ellipse_height = int(h * 0.8)

            # 如果指定了边界清理，则内缩椭圆
            if border_pixels > 0:
                ellipse_width = max(10, ellipse_width - border_pixels * 2)
                ellipse_height = max(10, ellipse_height - border_pixels * 2)
                print(f"🔧 应用边界清理: 椭圆尺寸内缩 {border_pixels} 像素")

            # 创建椭圆信息
            ellipse_info = {
                'center': (center_x, center_y),
                'original_size': (ellipse_width, ellipse_height),
                'border_cleanup': border_pixels,
                'image_size': image.shape[:2]  # (height, width)
            }

            # 创建白色背景
            white_background = np.ones_like(image) * 255

            # 创建椭圆掩码
            mask = np.zeros(image.shape[:2], dtype=np.uint8)

            # 绘制椭圆
            cv2.ellipse(mask,
                        (center_x, center_y),
                        (ellipse_width // 2, ellipse_height // 2),
                        0, 0, 360, 255, -1)

            # 应用掩码：椭圆内保留原图，椭圆外显示白色
            elliptical_face = np.where(
                mask[:, :, np.newaxis] == 255,
                image,
                white_background
            ).astype(np.uint8)

            # 裁剪椭圆区域
            roi_x = max(0, center_x - ellipse_width // 2)
            roi_y = max(0, center_y - ellipse_height // 2)
            roi_x2 = min(image.shape[1], center_x + ellipse_width // 2)
            roi_y2 = min(image.shape[0], center_y + ellipse_height // 2)

            cropped_face = elliptical_face[roi_y:roi_y2, roi_x:roi_x2]

            print(f"✅ 椭圆裁剪完成 - 尺寸: {ellipse_width}x{ellipse_height}, 清理: {border_pixels}像素")

            return cropped_face, ellipse_info

        except Exception as e:
            print(f"⚠️ 椭圆裁剪失败: {e}")
            return None, None

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

        # 如果鼻子检测器不可用，估算鼻子位置
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
        else:
            # 估算鼻子位置（在人脸中心偏下）
            nose_x = face_x + face_w // 2
            nose_y = face_y + face_h // 2
            nose_w = face_w // 6
            nose_h = face_h // 8
            features['nose'].append((nose_x - nose_w // 2, nose_y - nose_h // 2, nose_w, nose_h))
            print("👃 使用估算鼻子位置")

        # 如果嘴巴检测器不可用，估算嘴巴位置
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
        else:
            # 估算嘴巴位置（在人脸下部）
            mouth_x = face_x + face_w // 4
            mouth_y = face_y + int(face_h * 0.7)
            mouth_w = face_w // 2
            mouth_h = face_h // 6
            features['mouth'].append((mouth_x, mouth_y, mouth_w, mouth_h))
            print("👄 使用估算嘴巴位置")

        return features

    def _calculate_confidence(self, features, face_area, image_area):
        """计算检测置信度"""
        confidence = 0.0

        # 基础置信度基于人脸大小
        base_confidence = min(face_area / image_area * 10, 0.5)

        # 根据检测到的特征数量增加置信度
        feature_count = sum(len(features[key]) for key in features)

        if feature_count >= 3:
            confidence = base_confidence + 0.4
        elif feature_count >= 2:
            confidence = base_confidence + 0.3
        elif feature_count >= 1:
            confidence = base_confidence + 0.2
        else:
            confidence = base_confidence

        return min(confidence, 1.0)

    def apply_final_border_cleanup(self, processed_image, ellipse_info, border_cleanup_pixels):
        """在最终处理后的图像上应用边界清理"""
        try:
            print(f"🎯 应用最终边界清理: {border_cleanup_pixels} 像素")

            # 将PIL图像转换为numpy数组
            if isinstance(processed_image, Image.Image):
                img_array = np.array(processed_image)
            else:
                img_array = processed_image.copy()

            # 获取图像尺寸
            height, width = img_array.shape[:2]

            # 计算缩放后的椭圆参数
            scale_factor = ellipse_info.get('scale_factor', 1.0)
            original_center = ellipse_info['center']
            original_size = ellipse_info['original_size']

            # 计算在缩放后图像中的椭圆中心（相对位置）
            # 由于图像已经过裁剪和缩放，我们需要重新计算中心点
            scaled_center_x = width // 2
            scaled_center_y = height // 2

            # 计算缩放后的椭圆尺寸（考虑边界清理）
            scaled_ellipse_width = int(original_size[0] * scale_factor) - border_cleanup_pixels * 2
            scaled_ellipse_height = int(original_size[1] * scale_factor) - border_cleanup_pixels * 2

            # 确保椭圆尺寸不会太小
            scaled_ellipse_width = max(10, scaled_ellipse_width)
            scaled_ellipse_height = max(10, scaled_ellipse_height)

            print(
                f"📐 缩放后椭圆参数: 中心({scaled_center_x},{scaled_center_y}), 尺寸({scaled_ellipse_width}x{scaled_ellipse_height})")

            # 创建白色背景
            if len(img_array.shape) == 3:  # 彩色图像
                white_background = np.ones_like(img_array) * 255
            else:  # 灰度图像
                white_background = np.ones_like(img_array) * 255

            # 创建椭圆掩码
            mask = np.zeros((height, width), dtype=np.uint8)

            # 绘制椭圆（中心不变，尺寸内缩）
            cv2.ellipse(mask,
                        (scaled_center_x, scaled_center_y),
                        (scaled_ellipse_width // 2, scaled_ellipse_height // 2),
                        0, 0, 360, 255, -1)

            # 应用掩码：椭圆内保留原图，椭圆外显示白色
            if len(img_array.shape) == 3:  # 彩色图像
                result = np.where(
                    mask[:, :, np.newaxis] == 255,
                    img_array,
                    white_background
                ).astype(np.uint8)
            else:  # 灰度图像
                result = np.where(
                    mask == 255,
                    img_array,
                    white_background
                ).astype(np.uint8)

            # 转换回PIL图像
            final_image = Image.fromarray(result)

            print(f"✅ 最终边界清理完成 - 内缩 {border_cleanup_pixels} 像素")
            return final_image

        except Exception as e:
            print(f"❌ 最终边界清理失败: {e}")
            return processed_image

    # 向后兼容的方法
    def detect_faces_with_confidence(self, image_path, border_cleanup_pixels=3):
        """向后兼容的旧方法名"""
        print("⚠️ 使用旧方法名 detect_faces_with_confidence")
        return self.detect_facial_features_with_confidence(image_path, border_cleanup_pixels)

    def detect_and_crop_face(self, image_path, border_cleanup_pixels=3):
        """另一个向后兼容的方法"""
        print("⚠️ 使用旧方法名 detect_and_crop_face")
        return self.detect_facial_features_with_confidence(image_path, border_cleanup_pixels)
