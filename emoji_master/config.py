'''
emoji_master/
├── app.py
├── static/
│   ├── style.css
│   ├── main.js
│   └── styles/
├── temp/
│   ├── results/
│   └── uploads/
├── templates/
│   └── index.html
├── models/
│   ├── face_detection.py
│   ├── image_processing.py
│   └── style_synthesis.py
└── utils/
    ├── file_manager.py
    └── image_utils.py
'''
import os


class Config:
    """应用配置类 - 修正为正确的项目结构"""

    # config.py在项目根目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 修正：只需要dirname一次

    print(f"🔧 Config初始化 - 检测路径:")
    print(f"  config.py位置: {os.path.abspath(__file__)}")
    print(f"  BASE_DIR计算为: {BASE_DIR}")

    # Flask静态文件夹路径
    STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
    STYLES_FOLDER = os.path.join(STATIC_FOLDER, 'styles')  # 图片模板在这里

    # 临时文件夹 - 根据你的要求，uploads和results在temp文件夹里
    TEMP_FOLDER = os.path.join(BASE_DIR, 'temp')
    UPLOAD_FOLDER = os.path.join(TEMP_FOLDER, 'uploads')  # 上传文件
    RESULT_FOLDER = os.path.join(TEMP_FOLDER, 'results')  # 生成结果

    # 创建必要的目录
    for folder in [UPLOAD_FOLDER, RESULT_FOLDER, STYLES_FOLDER]:
        os.makedirs(folder, exist_ok=True)
        print(f"  📁 确保目录存在: {folder}")

    # 可用风格模板
    AVAILABLE_STYLES = {
        'panda': 'panda_template.png',
        'mushroom': 'mushroom_template.png',
        'dragon': 'dragon_template.png'
    }

    # 其他配置
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # 人脸检测相关配置 - 修复人脸过大的问题
    FACE_DETECTION_CONFIDENCE = 0.3
    MAX_FACE_SIZE = 256  # 减小最大尺寸，防止人脸过大

    IMAGE_ENHANCE_PARAMS = {
        'brightness': 1.1,  # 亮度
        'exposure': 1.0,  # 曝光
        'contrast': 1.2,  # 对比度
        'saturation': 1.1,  # 饱和度
        'vibrance': 10,  # 自然饱和度
        'temperature': 5,  # 色温
        'hue': 0,  # 色调
        'lightness': 1.1  # 光感
    }

    # 默认处理参数 - 更新为0-100%范围
    DEFAULT_PROCESS_PARAMS = {
        'brighten_factor': 50,  # 亮部增强比例 (0-100%)
        'darken_factor': 50,    # 暗部减弱比例 (0-100%)
        'low_cutoff_percent': 30,  # 暗部阈值百分比 (0-100%)
        'high_cutoff_percent': 20,  # 亮部阈值百分比 (0-100%)
        'border_cleanup_pixels': 2  # 边界清理像素数
    }

    # 风格合成配置 - 调整人脸尺寸比例，防止人脸过大
    STYLE_SYNTHESIS = {
        'face_size_ratio': 0.5,  # 减小比例，防止人脸过大
        'min_face_size': 80,
        'fallback_size': (512, 512)
    }

    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True

    @classmethod
    def validate_template_files(cls):
        """验证模板文件是否正确"""
        print(f"\n🔍 验证模板文件:")
        print(f"  STYLES_FOLDER: {cls.STYLES_FOLDER}")
        print(f"  目录是否存在: {os.path.exists(cls.STYLES_FOLDER)}")

        if not os.path.exists(cls.STYLES_FOLDER):
            print(f"  ❌ 模板目录不存在！")
            return False

        # 列出目录内容
        print(f"\n  📁 static/styles目录内容:")
        try:
            for item in os.listdir(cls.STYLES_FOLDER):
                item_path = os.path.join(cls.STYLES_FOLDER, item)
                status = "📄 文件" if os.path.isfile(item_path) else "📁 目录"
                print(f"    {status}: {item}")
        except Exception as e:
            print(f"    无法列出目录内容: {e}")

        # 检查每个系统模板
        print(f"\n  🔍 检查系统模板:")
        all_exist = True
        for style_name, filename in cls.AVAILABLE_STYLES.items():
            file_path = os.path.join(cls.STYLES_FOLDER, filename)
            exists = os.path.exists(file_path)
            status = "✅ 存在" if exists else "❌ 缺失"
            print(f"    {style_name} ({filename}): {status}")

            if exists:
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    print(f"      尺寸: {img.size}, 模式: {img.mode}")
                    img.close()
                except Exception as e:
                    print(f"      ⚠️ 无法打开: {e}")
            else:
                all_exist = False

        return all_exist

# 启动时验证
print(f"\n" + "=" * 60)
if Config.validate_template_files():
    print(f"\n🎉 所有系统模板就绪！")
else:
    print(f"\n⚠️ 系统模板文件不完整，请检查 static/styles/ 目录")
print("=" * 60)
