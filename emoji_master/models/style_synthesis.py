from PIL import Image, ImageEnhance
import os
import numpy as np
from config import Config

class StyleSynthesizer:
    """风格合成模块 - 优化版本"""

    def __init__(self):
        self.styles_folder = Config.STYLES_FOLDER
        self.available_styles = Config.AVAILABLE_STYLES

        print(f"\n🎨 风格合成器初始化")
        print(f"📁 模板目录: {self.styles_folder}")

        # 验证模板
        self._validate_templates()

    def _validate_templates(self):
        """验证所有模板文件"""
        print("🔍 验证模板文件:")
        valid_count = 0
        for style_name, filename in self.available_styles.items():
            template_path = os.path.join(self.styles_folder, filename)
            if os.path.exists(template_path):
                try:
                    with Image.open(template_path) as img:
                        status = f"✅ {style_name}: {filename} - 就绪 ({img.size})"
                        valid_count += 1
                except Exception as e:
                    status = f"❌ {style_name}: {filename} - 损坏: {e}"
            else:
                status = f"❌ {style_name}: {filename} - 不存在"
            print(f"   {status}")

        print(f"📊 模板验证完成: {valid_count}/{len(self.available_styles)} 个模板可用")

    def synthesize_style(self, face_image, style_name):
        """合成风格表情包 - 优化版本"""
        try:
            print(f"\n" + "=" * 50)
            print(f"🎨 开始合成风格: {style_name}")

            # 获取模板路径
            template_path = self._get_template_path(style_name)
            if template_path is None:
                print(f"❌ 模板文件不存在: {style_name}")
                return self._create_fallback_image(face_image, style_name)

            # 加载并验证模板
            template = self._load_and_validate_template(template_path)
            if template is None:
                return self._create_fallback_image(face_image, style_name)

            # 调整人脸尺寸
            face_resized = self._resize_face_for_template(face_image, template.size)

            # 使用优化的Alpha混合
            result = self._alpha_blend_images(template, face_resized)

            print("🎉 合成完成!")
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
            self._debug_template_directory()
            return None

        return template_path

    def _debug_template_directory(self):
        """调试模板目录"""
        if os.path.exists(self.styles_folder):
            print(f"📁 模板目录内容:")
            files = os.listdir(self.styles_folder)
            for file in files[:10]:  # 只显示前10个文件
                print(f"   - {file}")
            if len(files) > 10:
                print(f"   ... 还有 {len(files) - 10} 个文件")

    def _load_and_validate_template(self, template_path):
        """加载并验证模板"""
        try:
            template = Image.open(template_path)
            print(f"📏 模板尺寸: {template.size}, 模式: {template.mode}")

            # 转换为RGBA确保透明度支持
            if template.mode != 'RGBA':
                template = template.convert('RGBA')
                print("🔄 模板已转换为RGBA模式")

            return template
        except Exception as e:
            print(f"❌ 模板加载失败: {str(e)}")
            return None

    def _resize_face_for_template(self, face_image, template_size):
        """智能调整人脸尺寸"""
        template_width, template_height = template_size

        # 根据模板大小计算合适的人脸尺寸
        base_size = min(template_width, template_height) * 0.5  # 模板大小的50%

        # 保持人脸宽高比
        face_ratio = face_image.width / face_image.height
        if face_ratio > 1.2:  # 宽脸
            new_width = int(base_size)
            new_height = int(base_size / face_ratio)
        elif face_ratio < 0.8:  # 长脸
            new_height = int(base_size)
            new_width = int(base_size * face_ratio)
        else:  # 正常比例
            new_size = int(base_size)
            new_width = new_size
            new_height = new_size

        # 确保最小尺寸
        new_width = max(new_width, 80)
        new_height = max(new_height, 80)

        print(f"📐 人脸调整: {face_image.size} -> ({new_width}, {new_height})")

        face_resized = face_image.resize((new_width, new_height), Image.LANCZOS)

        # 确保RGBA模式
        if face_resized.mode != 'RGBA':
            face_resized = face_resized.convert('RGBA')

        return face_resized

    def _alpha_blend_images(self, template, face_image):
        """使用Alpha混合合成图像 - 优化版本"""
        # 转换为NumPy数组进行高效操作
        template_np = np.array(template)
        face_np = np.array(face_image)

        # 创建结果副本
        result_np = template_np.copy()

        # 计算放置位置（居中）
        template_h, template_w = template_np.shape[:2]
        face_h, face_w = face_np.shape[:2]

        pos_x = (template_w - face_w) // 2
        pos_y = (template_h - face_h) // 2

        print(f"📍 合成位置: ({pos_x}, {pos_y})")
        print(f"🔍 人脸Alpha范围: {face_np[:, :, 3].min()} - {face_np[:, :, 3].max()}")

        # 计算有效区域（防止越界）
        start_x = max(0, pos_x)
        start_y = max(0, pos_y)
        end_x = min(template_w, pos_x + face_w)
        end_y = min(template_h, pos_y + face_h)

        # 计算对应的face区域
        face_start_x = max(0, -pos_x)
        face_start_y = max(0, -pos_y)
        face_end_x = face_start_x + (end_x - start_x)
        face_end_y = face_start_y + (end_y - start_y)

        # 提取有效区域
        template_region = result_np[start_y:end_y, start_x:end_x]
        face_region = face_np[face_start_y:face_end_y, face_start_x:face_end_x]

        # 归一化alpha通道
        face_alpha = face_region[:, :, 3] / 255.0
        template_alpha = template_region[:, :, 3] / 255.0

        # Alpha混合公式
        for channel in range(3):  # RGB通道
            template_region[:, :, channel] = (
                    face_region[:, :, channel] * face_alpha +
                    template_region[:, :, channel] * (1 - face_alpha)
            )

        # 合并alpha通道
        combined_alpha = np.maximum(template_alpha, face_alpha) * 255
        template_region[:, :, 3] = combined_alpha.astype(np.uint8)

        # 更新结果
        result_np[start_y:end_y, start_x:end_x] = template_region

        return Image.fromarray(result_np)

    def _create_fallback_image(self, face_image, style_name):
        """创建回退图像"""
        print("🔄 使用回退方案")

        # 创建简单背景
        bg_colors = {
            'panda': (240, 240, 240),
            'mushroom': (255, 230, 230),
            'dragon': (230, 255, 230)
        }
        bg_color = bg_colors.get(style_name, (230, 230, 255))

        result = Image.new('RGBA', (512, 512), (*bg_color, 255))
        draw = ImageDraw.Draw(result)

        # 调整人脸大小
        face_size = min(300, face_image.width, face_image.height)
        face_resized = face_image.resize((face_size, face_size), Image.LANCZOS)

        # 放置人脸
        position = ((512 - face_size) // 2, (512 - face_size) // 2)
        result.paste(face_resized, position, face_resized)

        # 添加边框和文字
        draw.rectangle(
            [position[0] - 5, position[1] - 5, position[0] + face_size + 5, position[1] + face_size + 5],
            outline=(100, 100, 100, 255), width=2
        )

        # 添加说明文字
        try:
            text = f"{style_name} - 模板加载失败"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_position = ((512 - text_width) // 2, 450)
            draw.text(text_position, text, fill=(255, 0, 0, 255))
        except:
            pass

        return result
