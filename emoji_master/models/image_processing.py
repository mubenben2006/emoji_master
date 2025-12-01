import numpy as np
from PIL import Image, ImageEnhance
from config import Config


class FaceProcessor:
    """完整的人脸处理模块 - 支持双端像素调整和透明背景"""

    def __init__(self, face_detector):
        self.face_detector = face_detector
        self.enhance_params = Config.IMAGE_ENHANCE_PARAMS

    def process_face(self, face_image, processing_params=None, ellipse_info=None):
        """处理人脸图像 - 完全支持亮暗参数调整"""
        if processing_params is None:
            processing_params = Config.DEFAULT_PROCESS_PARAMS.copy()

        try:
            print(f"🎨 开始人脸处理: 输入尺寸{face_image.size}")
            print(f"📊 处理参数: {processing_params}")

            # 确保RGBA格式以保持透明度
            if face_image.mode != 'RGBA':
                face_image = face_image.convert('RGBA')

            # 分离RGB和Alpha通道
            rgb_image = face_image.convert('RGB')
            alpha_channel = face_image.getchannel('A')

            # 步骤1: 应用新的亮暗调整算法
            adjusted_rgb = self._new_brightness_adjustment(
                rgb_image,
                brighten_factor=processing_params['brighten_factor'],
                darken_factor=processing_params['darken_factor'],
                low_cutoff_percent=processing_params['low_cutoff_percent'],
                high_cutoff_percent=processing_params['high_cutoff_percent']
            )

            # 步骤2: 应用完整图像增强
            enhanced_rgb = self._enhance_image(adjusted_rgb)

            # 步骤3: 转换为黑白表情包风格
            bw_rgb = self._convert_to_emoji_style(enhanced_rgb)

            # 重新组合RGB和Alpha通道
            bw_rgba = Image.merge('RGBA', (*bw_rgb.split(), alpha_channel))

            # 步骤4: 应用边界清理
            border_pixels = processing_params.get('border_cleanup_pixels', 2)
            if ellipse_info and border_pixels > 0:
                final_face = self.face_detector.apply_border_cleanup(
                    bw_rgba, ellipse_info, border_pixels
                )
                print(f"✅ 边界清理完成: {border_pixels}像素")
            else:
                final_face = bw_rgba
                print("⚠️ 未进行边界清理")

            print(f"✅ 人脸处理完成: 输出尺寸{final_face.size}")
            return final_face

        except Exception as e:
            print(f"❌ 人脸处理错误: {e}")
            import traceback
            traceback.print_exc()
            return face_image

    def _new_brightness_adjustment(self, image, low_cutoff_percent=30, high_cutoff_percent=20,
                                   darken_factor=50, brighten_factor=50):
        """新的亮暗调整算法：按公式调整像素值"""
        try:
            print("🎯 应用新的亮暗调整算法...")
            print(f"📊 使用参数:")
            print(f"   - 暗比例: {darken_factor}%")
            print(f"   - 亮比例: {brighten_factor}%")
            print(f"   - 暗阈值: {low_cutoff_percent}% (最暗的像素百分比)")
            print(f"   - 亮阈值: {high_cutoff_percent}% (最亮的像素百分比)")

            # 转换为numpy数组并转为float类型
            img_array = np.array(image).astype(np.float32)

            # 计算灰度值
            gray = np.mean(img_array, axis=2)

            # 计算阈值 - 暗阈值：最暗的low_cutoff_percent%像素
            # 亮阈值：最亮的high_cutoff_percent%像素
            flat_gray = gray.flatten()

            # 暗阈值：计算最暗的low_cutoff_percent%像素的阈值
            dark_threshold = np.percentile(flat_gray, low_cutoff_percent)

            # 亮阈值：计算最亮的high_cutoff_percent%像素的阈值
            # 注意：percentile的第100-high_cutoff_percent百分位表示最亮的high_cutoff_percent%像素
            bright_threshold = np.percentile(flat_gray, 100 - high_cutoff_percent)

            # 创建结果数组
            result = img_array.copy()

            # 将参数转换为0-1的小数
            darken_factor_dec = darken_factor / 100.0
            brighten_factor_dec = brighten_factor / 100.0

            # 应用调整公式
            for c in range(3):  # 对每个RGB通道
                channel = img_array[:, :, c]

                # 对暗部区域：暗参数 × (像素值 - 0)
                # 只处理最暗的low_cutoff_percent%像素
                dark_mask = gray <= dark_threshold
                if np.any(dark_mask):
                    dark_adjustment = channel[dark_mask] * darken_factor_dec
                    result[dark_mask, c] = np.clip(channel[dark_mask] - dark_adjustment, 0, 255)

                # 对亮部区域：亮参数 × (255 - 像素值)
                # 只处理最亮的high_cutoff_percent%像素
                bright_mask = gray >= bright_threshold
                if np.any(bright_mask):
                    bright_adjustment = (255 - channel[bright_mask]) * brighten_factor_dec
                    result[bright_mask, c] = np.clip(channel[bright_mask] + bright_adjustment, 0, 255)

            # 限制在0-255范围内并转换回uint8
            result = np.clip(result, 0, 255).astype(np.uint8)

            # 转换为PIL图像
            result_image = Image.fromarray(result)

            print(f"📊 新亮暗调整完成:")
            print(f"   - 暗阈值: {dark_threshold:.1f} (最暗的{low_cutoff_percent}%像素)")
            print(f"   - 亮阈值: {bright_threshold:.1f} (最亮的{high_cutoff_percent}%像素)")
            print(f"   - 变暗像素数: {np.sum(dark_mask)}")
            print(f"   - 变亮像素数: {np.sum(bright_mask)}")

            # 检查是否有重叠区域
            overlap_mask = dark_mask & bright_mask
            if np.any(overlap_mask):
                print(f"   ⚠️ 注意: 有{np.sum(overlap_mask)}个像素同时属于暗部和亮部区域")
                print(f"     暗阈值: {dark_threshold:.1f}, 亮阈值: {bright_threshold:.1f}")

            return result_image

        except Exception as e:
            print(f"⚠️ 亮暗调整失败: {e}")
            import traceback
            traceback.print_exc()
            return image

    def _enhance_image(self, image):
        """增强图像质量 - 使用配置中的所有参数"""
        print("🎨 应用图像增强...")
        print(f"📊 使用参数: {self.enhance_params}")

        # 亮度调整
        if self.enhance_params['brightness'] != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.enhance_params['brightness'])
            print(f"   ✅ 亮度调整: {self.enhance_params['brightness']}")

        # 曝光调整
        if self.enhance_params['exposure'] != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.enhance_params['exposure'])
            print(f"   ✅ 曝光调整: {self.enhance_params['exposure']}")

        # 对比度调整
        if self.enhance_params['contrast'] != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.enhance_params['contrast'])
            print(f"   ✅ 对比度调整: {self.enhance_params['contrast']}")

        # 饱和度调整
        if self.enhance_params['saturation'] != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(self.enhance_params['saturation'])
            print(f"   ✅ 饱和度调整: {self.enhance_params['saturation']}")

        # 自然饱和度调整
        if self.enhance_params['vibrance'] != 0:
            image = self._adjust_vibrance(image, self.enhance_params['vibrance'])
            print(f"   ✅ 自然饱和度调整: {self.enhance_params['vibrance']}")

        # 色温调整
        if self.enhance_params['temperature'] != 0:
            image = self._adjust_color_temperature(image, self.enhance_params['temperature'])
            print(f"   ✅ 色温调整: {self.enhance_params['temperature']}")

        # 色调调整
        if self.enhance_params['hue'] != 0:
            image = self._adjust_hue(image, self.enhance_params['hue'])
            print(f"   ✅ 色调调整: {self.enhance_params['hue']}")

        # 光感调整
        if self.enhance_params['lightness'] != 1.0:
            image = self._adjust_lightness(image, self.enhance_params['lightness'])
            print(f"   ✅ 光感调整: {self.enhance_params['lightness']}")

        print("✅ 图像增强完成")
        return image

    def _convert_to_emoji_style(self, image):
        """转换为表情包风格：黑白+增强对比度"""
        print("⚫⚪ 转换为黑白表情包风格...")

        # 转换为灰度
        bw_image = image.convert('L')

        # 增强对比度
        enhancer = ImageEnhance.Contrast(bw_image)
        bw_image = enhancer.enhance(1.2)

        # 转换为RGB（三通道黑白）
        bw_rgb = bw_image.convert('RGB')

        print("✅ 黑白转换完成")
        return bw_rgb

    def _adjust_vibrance(self, image, vibrance_change):
        """调整自然饱和度"""
        if vibrance_change != 0:
            hsv_image = image.convert('HSV')
            h, s, v = hsv_image.split()

            s_array = np.array(s, dtype=np.float32) / 255.0

            enhanced_s = np.where(
                s_array < 0.5,
                s_array * (1 + vibrance_change / 100),
                s_array * (1 + vibrance_change / 200)
            )

            enhanced_s = np.clip(enhanced_s, 0, 1) * 255
            enhanced_s = Image.fromarray(enhanced_s.astype(np.uint8))

            enhanced_hsv = Image.merge('HSV', (h, enhanced_s, v))
            return enhanced_hsv.convert('RGB')
        return image

    def _adjust_color_temperature(self, image, temp_change):
        """调整色温"""
        if temp_change == 0:
            return image

        img_array = np.array(image)
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

        r = np.clip(r.astype('float') + temp_change, 0, 255)
        g = np.clip(g.astype('float') + temp_change * 0.3, 0, 255)
        b = np.clip(b.astype('float') - temp_change * 0.5, 0, 255)

        img_array[:, :, 0] = r.astype('uint8')
        img_array[:, :, 1] = g.astype('uint8')
        img_array[:, :, 2] = b.astype('uint8')

        return Image.fromarray(img_array)

    def _adjust_hue(self, image, hue_change):
        """调整色调"""
        if hue_change == 0:
            return image

        hsv_image = image.convert('HSV')
        h, s, v = hsv_image.split()

        hue_shift = int(hue_change * 255 / 100)
        h = h.point(lambda x: (x + hue_shift) % 256)

        return Image.merge('HSV', (h, s, v)).convert('RGB')

    def _adjust_lightness(self, image, lightness_change):
        """调整光感"""
        if lightness_change == 1.0:
            return image

        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(lightness_change)
