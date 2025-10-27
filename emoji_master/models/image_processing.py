from PIL import Image, ImageEnhance, ImageFilter
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

            # 应用背景虚化
            final_face = self._blur_background(enhanced_face)

            return final_face

        except Exception as e:
            print(f"人脸处理错误: {str(e)}")
            return face_image  # 出错时返回原图

    def _enhance_image(self, image):
        """增强图像质量"""
        # 亮度增强
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.enhance_params['brightness'])

        # 对比度增强
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.enhance_params['contrast'])

        # 饱和度调整
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.enhance_params['saturation'])

        return image

    def _blur_background(self, image):
        """背景虚化（简单实现）"""
        # 创建模糊版本
        blurred = image.filter(ImageFilter.GaussianBlur(5))

        # 创建中心区域的掩码（简单圆形）
        width, height = image.size
        mask = Image.new('L', (width, height), 0)

        # 在中心创建椭圆区域
        center_x, center_y = width // 2, height // 2
        radius_x, radius_y = width // 3, height // 3

        for y in range(height):
            for x in range(width):
                if ((x - center_x) / radius_x) ** 2 + ((y - center_y) / radius_y) ** 2 <= 1:
                    mask.putpixel((x, y), 255)

        # 组合图像：中心清晰，边缘模糊
        result = Image.composite(image, blurred, mask)
        return result