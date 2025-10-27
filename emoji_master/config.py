import os
import tempfile
from PIL import Image, ImageDraw

# OpenMP冲突解决方案
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


class Config:
    """应用配置类"""

    # 基础配置
    SECRET_KEY = 'your-secret-key-here'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB文件大小限制

    # 文件上传配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'temp', 'uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'temp', 'results')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 模板配置 - 修正为正确的路径
    STYLES_FOLDER = os.path.join(BASE_DIR, 'static', 'styles')  # 修正这里！
    AVAILABLE_STYLES = {
        'panda': 'panda_template.png',
        'mushroom': 'mushroom_template.png',
        'dragon': 'dragon_template.png'
    }

    # 图像处理配置
    FACE_SIZE = (256, 256)  # 人脸裁剪尺寸

    # 人脸检测配置
    FACE_DETECTION_CONFIDENCE = 0.05
    MIN_FACE_SIZE = 50

    # 图像处理参数
    IMAGE_ENHANCE_PARAMS = {
        'brightness': 1.65,
        'contrast': 2.0,
        'saturation': 0.0,
        'exposure': 1.5
    }


def create_directories():
    """创建必要的目录"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.RESULT_FOLDER,
        # 不再自动创建styles目录，因为文件已经存在
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 创建目录: {directory}")


def debug_template_files():
    """调试模板文件访问"""
    print(f"\n🔍 调试模板文件:")
    print(f"配置的模板目录: {Config.STYLES_FOLDER}")
    print(f"模板目录是否存在: {os.path.exists(Config.STYLES_FOLDER)}")

    if os.path.exists(Config.STYLES_FOLDER):
        print(f"📁 模板目录内容:")
        files = os.listdir(Config.STYLES_FOLDER)
        for file in files:
            file_path = os.path.join(Config.STYLES_FOLDER, file)
            print(f"   📄 {file} - 存在: {os.path.exists(file_path)}")

            # 检查文件是否可以打开
            if file_path.endswith(('.png', '.jpg', '.jpeg')):
                try:
                    img = Image.open(file_path)
                    print(f"     尺寸: {img.size}, 模式: {img.mode}")
                    img.close()
                except Exception as e:
                    print(f"     ❌ 无法打开: {e}")
    else:
        print(f"❌ 模板目录不存在!")

    # 检查每个模板文件
    print(f"\n🔍 检查配置的模板文件:")
    all_exist = True
    for style_name, filename in Config.AVAILABLE_STYLES.items():
        template_path = os.path.join(Config.STYLES_FOLDER, filename)
        exists = os.path.exists(template_path)
        print(f"   {style_name}: {filename} - 存在: {exists}")
        if exists:
            try:
                img = Image.open(template_path)
                print(f"     ✅ 可打开 - 尺寸: {img.size}")
                img.close()
            except Exception as e:
                print(f"     ❌ 打开失败: {e}")
                all_exist = False
        else:
            all_exist = False

    return all_exist


# 初始化目录
create_directories()

# 调试模板文件
templates_ok = debug_template_files()

print(f"\n🔧 配置初始化完成")
print(f"🎯 模板文件状态: {'✅ 所有模板文件就绪' if templates_ok else '❌ 模板文件有问题'}")