import os
import json
import numpy as np
from PIL import Image, ImageDraw
from config import Config
from datetime import datetime
from pathlib import Path


class StyleSynthesizer:
    """风格合成模块 - 支持自定义模板"""

    def __init__(self):
        # 将路径转换为Path对象以便使用/运算符
        self.styles_folder = Path(Config.STYLES_FOLDER)  # 转换为Path对象
        self.available_styles = Config.AVAILABLE_STYLES
        self.synthesis_config = Config.STYLE_SYNTHESIS
        self.custom_templates_file = self.styles_folder / 'custom_templates.json'

    def synthesize_style(self, face_image, style_name):
        """合成风格表情包 - 支持系统模板和自定义模板"""
        try:
            # 获取模板
            template = self._load_template(style_name)
            if template is None:
                print(f"❌ 模板加载失败: {style_name}")
                return self._create_fallback(face_image, style_name)

            # 调整人脸尺寸 - 使用新的尺寸计算方法
            face_resized = self._resize_face_for_template_new(face_image, template.size)

            # 合成图像
            result = self._blend_images(template, face_resized)

            print(f"✅ 风格合成成功: {style_name}")
            return result

        except Exception as e:
            print(f"❌ 风格合成错误: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback(face_image, style_name)

    def _load_template(self, style_name):
        """加载风格模板 - 支持系统模板和自定义模板"""
        # 先检查是否是系统模板
        if style_name in self.available_styles:
            template_filename = self.available_styles[style_name]
            template_path = self.styles_folder / template_filename
        else:
            # 检查是否是自定义模板
            template_path = self._get_custom_template_path(style_name)
            if not template_path:
                print(f"❌ 未找到模板: {style_name}")
                return None

        if not template_path.exists():
            print(f"❌ 模板文件不存在: {template_path}")
            return None

        try:
            template = Image.open(str(template_path))
            if template.mode != 'RGBA':
                template = template.convert('RGBA')
            print(f"✅ 加载模板成功: {style_name} ({template.size})")
            return template
        except Exception as e:
            print(f"❌ 模板加载失败 {template_path}: {e}")
            return None

    def _get_custom_template_path(self, style_name):
        """获取自定义模板路径"""
        if not self.custom_templates_file.exists():
            return None

        try:
            with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)

            if style_name in templates:
                filename = templates[style_name]['filename']
                return self.styles_folder / filename
        except Exception as e:
            print(f"❌ 读取自定义模板配置失败: {e}")

        return None

    def _resize_face_for_template_new(self, face_image, template_size):
        """新的调整人脸尺寸方法，防止人脸过大"""
        template_width, template_height = template_size

        # 使用更小的比例，防止人脸过大
        base_size = int(min(template_width, template_height) * self.synthesis_config['face_size_ratio'])

        # 限制最大尺寸
        max_face_size = Config.MAX_FACE_SIZE
        if base_size > max_face_size:
            base_size = max_face_size

        print(f"📏 基础尺寸计算: 模板{template_size} -> 基础{base_size}")

        # 保持宽高比
        face_ratio = face_image.width / face_image.height
        if face_ratio > 1.2:  # 宽脸
            new_width = base_size
            new_height = int(base_size / face_ratio)
        elif face_ratio < 0.8:  # 长脸
            new_height = base_size
            new_width = int(base_size * face_ratio)
        else:  # 正常比例
            new_width = new_height = base_size

        # 确保最小尺寸
        new_width = max(new_width, self.synthesis_config['min_face_size'])
        new_height = max(new_height, self.synthesis_config['min_face_size'])

        # 额外限制：不能超过模板的60%
        max_template_percent = 0.6
        new_width = min(new_width, int(template_width * max_template_percent))
        new_height = min(new_height, int(template_height * max_template_percent))

        face_resized = face_image.resize((new_width, new_height), Image.LANCZOS)

        # 确保RGBA模式
        if face_resized.mode != 'RGBA':
            face_resized = face_resized.convert('RGBA')

        print(f"📏 人脸调整尺寸: {face_image.size} -> {face_resized.size}")
        return face_resized

    def _resize_face_for_template(self, face_image, template_size):
        """调整人脸尺寸以适应模板 - 保留旧方法兼容性"""
        return self._resize_face_for_template_new(face_image, template_size)

    def _blend_images(self, template, face_image):
        """混合模板和人脸图像"""
        try:
            # 确保模板和人脸都是RGBA
            if template.mode != 'RGBA':
                template = template.convert('RGBA')
            if face_image.mode != 'RGBA':
                face_image = face_image.convert('RGBA')

            # 创建新的合成图像
            result = template.copy()

            # 计算放置位置（居中）
            template_width, template_height = template.size
            face_width, face_height = face_image.size

            pos_x = (template_width - face_width) // 2
            pos_y = (template_height - face_height) // 2

            # 确保位置有效
            pos_x = max(0, pos_x)
            pos_y = max(0, pos_y)

            # 创建临时图像用于混合
            temp_image = Image.new('RGBA', template.size, (0, 0, 0, 0))
            temp_image.paste(face_image, (pos_x, pos_y))

            # Alpha混合
            result = Image.alpha_composite(result, temp_image)

            print("✅ 图像混合成功")
            return result

        except Exception as e:
            print(f"❌ 图像混合失败: {e}")
            # 如果混合失败，返回简单叠加
            result = template.copy()
            pos_x = (template.width - face_image.width) // 2
            pos_y = (template.height - face_image.height) // 2
            result.paste(face_image, (pos_x, pos_y), mask=face_image)
            return result

    def _create_fallback(self, face_image, style_name):
        """创建回退图像"""
        print(f"⚠️ 创建回退图像: {style_name}")
        width, height = self.synthesis_config['fallback_size']
        result = Image.new('RGB', (width, height), color=(240, 240, 240))

        # 调整人脸大小并居中放置
        face_size = min(200, face_image.width, face_image.height)  # 减小回退图像中的人脸尺寸
        face_resized = face_image.resize((face_size, face_size), Image.LANCZOS)
        position = ((width - face_size) // 2, (height - face_size) // 2)

        if face_resized.mode == 'RGBA':
            result.paste(face_resized, position, mask=face_resized)
        else:
            result.paste(face_resized, position)

        return result

    def save_custom_template(self, template_file, style_name, description=""):
        """保存自定义模板"""
        try:
            # 确保目录存在
            self.styles_folder.mkdir(exist_ok=True)

            # 生成唯一文件名
            import uuid
            filename = f"custom_{uuid.uuid4().hex}.png"
            template_path = self.styles_folder / filename

            # 保存模板文件（PIL的save方法）
            template_file.save(str(template_path))

            # 更新配置文件
            templates = {}
            if self.custom_templates_file.exists():
                with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)

            templates[style_name] = {
                'filename': filename,
                'description': description,
                'created_at': str(datetime.now()),
                'type': 'custom'
            }

            with open(self.custom_templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)

            print(f"✅ 自定义模板保存成功: {style_name}")
            return True

        except Exception as e:
            print(f"❌ 保存自定义模板失败: {e}")
            return False

    def get_custom_templates(self):
        """获取所有自定义模板"""
        if not self.custom_templates_file.exists():
            return {}

        try:
            with open(self.custom_templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取自定义模板失败: {e}")
            return {}
