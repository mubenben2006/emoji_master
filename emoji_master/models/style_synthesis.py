from PIL import Image, ImageEnhance
import os

from config import Config


class StyleSynthesizer:
    """风格合成模块 - 使用正确的模板路径"""

    def __init__(self):
        self.styles_folder = Config.STYLES_FOLDER
        self.available_styles = Config.AVAILABLE_STYLES

        print(f"\n🎨 风格合成器初始化")
        print(f"📁 模板目录: {self.styles_folder}")
        print(f"📁 模板目录是否存在: {os.path.exists(self.styles_folder)}")

        # 立即验证模板文件
        self._validate_templates()

    def _validate_templates(self):
        """验证所有模板文件"""
        print(f"🔍 验证模板文件:")
        for style_name, filename in self.available_styles.items():
            template_path = os.path.join(self.styles_folder, filename)
            if os.path.exists(template_path):
                try:
                    img = Image.open(template_path)
                    print(f"   ✅ {style_name}: {filename} - 就绪 ({img.size})")
                    img.close()
                except Exception as e:
                    print(f"   ❌ {style_name}: {filename} - 损坏: {e}")
            else:
                print(f"   ❌ {style_name}: {filename} - 不存在")

    def synthesize_style(self, face_image, style_name):
        """合成风格表情包"""
        try:
            print(f"\n" + "=" * 50)
            print(f"🔧 开始合成风格: {style_name}")

            # 获取模板路径
            template_path = self._get_template_path(style_name)
            if template_path is None:
                print(f"❌ 模板文件不存在: {style_name}")
                return self._create_fallback_image(face_image, style_name)

            print(f"✅ 找到模板文件: {template_path}")

            # 加载模板
            template = Image.open(template_path)
            print(f"📏 模板原始尺寸: {template.size}, 模式: {template.mode}")

            # 转换为RGBA（确保透明度支持）
            if template.mode != 'RGBA':
                template = template.convert('RGBA')
                print(f"🔄 模板转换为RGBA模式")

            # 调整人脸尺寸
            face_resized = self._resize_face_for_template(face_image, template.size)
            print(f"📏 人脸调整后尺寸: {face_resized.size}")

            # 合成图像
            result = self._blend_images(template, face_resized)
            print("🎉 合成完成")
            print("=" * 50)

            return result

        except Exception as e:
            print(f"❌ 风格合成错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_image(face_image, style_name)

    def _get_template_path(self, style_name):
        """获取模板文件路径"""
        template_filename = self.available_styles.get(style_name)
        if template_filename is None:
            print(f"❌ 未知风格: {style_name}")
            return None

        template_path = os.path.join(self.styles_folder, template_filename)

        if not os.path.exists(template_path):
            print(f"❌ 模板文件不存在: {template_path}")
            # 列出目录内容帮助调试
            if os.path.exists(self.styles_folder):
                print(f"📁 模板目录实际内容:")
                for file in os.listdir(self.styles_folder):
                    print(f"   - {file}")
            return None

        return template_path

    def _resize_face_for_template(self, face_image, template_size):
        """调整人脸尺寸以适应模板"""
        template_width, template_height = template_size

        # 计算适合模板中心区域的大小（模板大小的50-60%）
        face_size = min(template_width, template_height) * 3 // 5

        # 调整人脸尺寸，保持宽高比
        face_ratio = face_image.width / face_image.height
        if face_ratio > 1:
            # 宽图
            new_width = face_size
            new_height = int(face_size / face_ratio)
        else:
            # 高图或方图
            new_height = face_size
            new_width = int(face_size * face_ratio)

        # 确保最小尺寸
        new_width = max(new_width, 100)
        new_height = max(new_height, 100)

        face_resized = face_image.resize((new_width, new_height), Image.LANCZOS)
        return face_resized

    def _blend_images(self, template, face_image):
        """混合模板和人脸图像"""
        # 创建结果图像副本
        result = template.copy()

        # 计算人脸放置位置（居中）
        template_width, template_height = template.size
        face_width, face_height = face_image.size

        position = (
            (template_width - face_width) // 2,
            (template_height - face_height) // 2
        )

        print(f"📍 人脸放置位置: {position}")

        # 确保人脸图像是RGBA模式
        if face_image.mode != 'RGBA':
            face_rgba = face_image.convert('RGBA')
            print(f"🔄 转换人脸为RGBA模式")
        else:
            face_rgba = face_image

        # 直接粘贴（使用人脸作为蒙版）
        print("🖼️ 开始合成...")
        result.paste(face_rgba, position, face_rgba)

        return result

    def _create_fallback_image(self, face_image, style_name):
        """创建回退图像（当模板不存在时）"""
        print("🔄 使用回退方案")

        from PIL import ImageDraw

        # 创建一个简单的背景
        bg_color = {
            'panda': (200, 200, 200),  # 灰色
            'mushroom': (255, 200, 200),  # 浅红色
            'dragon': (200, 255, 200)  # 浅绿色
        }.get(style_name, (200, 200, 255))  # 默认浅蓝色

        result = Image.new('RGB', (512, 512), bg_color)
        draw = ImageDraw.Draw(result)

        # 调整人脸大小
        face_resized = face_image.resize((300, 300), Image.LANCZOS)

        # 将人脸放在中心
        position = ((512 - 300) // 2, (512 - 300) // 2)
        result.paste(face_resized, position)

        # 添加边框
        draw.rectangle([position[0] - 5, position[1] - 5,
                        position[0] + 305, position[1] + 305],
                       outline=(100, 100, 100), width=3)

        # 添加文字说明
        try:
            text = f"模板加载失败: {style_name}"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_position = ((512 - text_width) // 2, 450)
            draw.text(text_position, text, fill=(255, 0, 0))
        except:
            pass

        return result