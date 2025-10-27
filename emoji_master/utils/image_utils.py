from PIL import Image
import io
import base64


def pil_to_base64(image):
    """
    将PIL图像转换为base64字符串
    """
    buffered = io.BytesIO()
    image.save(buffered, format="PNG", quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def base64_to_pil(base64_string):
    """
    将base64字符串转换为PIL图像
    """
    if ',' in base64_string:
        base64_string = base64_string.split(',')[1]

    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))


def validate_image_size(image, max_width=1920, max_height=1080):
    """
    验证图像尺寸
    """
    width, height = image.size
    return width <= max_width and height <= max_height


def compress_image(image, quality=85, max_size=(1080, 1080)):
    """
    压缩图像
    """
    # 调整尺寸
    image.thumbnail(max_size, Image.LANCZOS)

    return image