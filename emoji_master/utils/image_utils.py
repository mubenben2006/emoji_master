from PIL import Image
import io
import base64


class ImageUtils:
    """图像工具类 - 静态方法集合"""

    @staticmethod
    def pil_to_base64(image, format='PNG', quality=95):
        """PIL图像转base64"""
        buffer = io.BytesIO()
        image.save(buffer, format=format, quality=quality)
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{img_base64}"

    @staticmethod
    def base64_to_pil(base64_str):
        """base64转PIL图像"""
        if ',' in base64_str:
            base64_str = base64_str.split(',', 1)[1]

        image_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_data))

    @staticmethod
    def validate_image_size(image, max_width=2048, max_height=2048):
        """验证图像尺寸"""
        width, height = image.size
        return width <= max_width and height <= max_height

    @staticmethod
    def optimize_image(image, max_size=1024, quality=85):
        """优化图像尺寸和质量"""
        # 调整尺寸
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.LANCZOS)

        return image

    @staticmethod
    def ensure_rgba(image):
        """确保图像为RGBA模式"""
        if image.mode != 'RGBA':
            return image.convert('RGBA')
        return image

    @staticmethod
    def create_fallback_image(size=(400, 400), text="图像处理失败"):
        """创建回退图像"""
        from PIL import ImageDraw

        image = Image.new('RGB', size, color=(240, 240, 240))
        draw = ImageDraw.Draw(image)

        # 简单文本（实际使用时需要更复杂的绘制）
        try:
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_position = ((size[0] - text_width) // 2, size[1] // 2)
            draw.text(text_position, text, fill=(255, 0, 0))
        except:
            pass

        return image
