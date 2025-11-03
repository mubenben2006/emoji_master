from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np

from config import Config


class FaceProcessor:
    """人脸处理模块"""

    def __init__(self):
        self.enhance_params = Config.IMAGE_ENHANCE_PARAMS

    def process_face(self, face_image):
        """处理人脸图像"""
        try:
            # 转换为RGB（确保格式正确）
            if face_image.mode != 'RGB':
                face_image = face_image.convert('RGB')

            # 应用图像增强
            enhanced_face = self._enhance_image(face_image)

            return enhanced_face

        except Exception as e:
            print(f"人脸处理错误: {str(e)}")
            return face_image  # 出错时返回原图

    def _enhance_image(self, image):
        """增强图像质量 - 从配置参数调用"""
        # 亮度调整
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.enhance_params['brightness'])

        # 曝光调整
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.enhance_params['exposure'])

        # 对比度调整
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.enhance_params['contrast'])

        # 饱和度调整
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.enhance_params['saturation'])

        # 自然饱和度调整
        image = self._adjust_vibrance(image, self.enhance_params['vibrance'])

        # 色温调整
        image = self._adjust_color_temperature(image, self.enhance_params['temperature'])

        # 色调调整
        image = self._adjust_hue(image, self.enhance_params['hue'])

        # 光感调整
        image = self._adjust_lightness(image, self.enhance_params['lightness'])

        return image

    def _adjust_vibrance(self, image, vibrance_change):
        """调整自然饱和度"""
        # 由于已经饱和度-100，自然饱和度-100的效果相同
        return image

    def _adjust_color_temperature(self, image, temp_change):
        """调整色温"""
        # 将图像转换为RGB数组
        img_array = np.array(image)
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

        # 色温调整：减少红色，增加蓝色（冷色调）
        r = np.clip(r.astype('float') + temp_change, 0, 255)
        g = np.clip(g.astype('float') + temp_change * 0.5, 0, 255)  # 绿色适当调整
        b = np.clip(b.astype('float') - temp_change * 0.5, 0, 255)  # 蓝色相反调整

        # 重新组合通道
        img_array[:, :, 0] = r.astype('uint8')
        img_array[:, :, 1] = g.astype('uint8')
        img_array[:, :, 2] = b.astype('uint8')

        return Image.fromarray(img_array)

    def _adjust_hue(self, image, hue_change):
        """调整色调"""
        # 转换为HSV调整色调
        hsv_image = image.convert('HSV')
        h, s, v = hsv_image.split()

        # 色调调整（在0-255范围内循环）
        h = h.point(lambda x: (x + hue_change) % 256)

        return Image.merge('HSV', (h, s, v)).convert('RGB')

    def _adjust_lightness(self, image, lightness_change):
        """调整光感"""
        # 通过亮度调整模拟光感
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(lightness_change)
