from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
from config import Config


class FaceProcessor:
    """人脸处理模块"""

    def __init__(self, face_detector):
        self.enhance_params = Config.IMAGE_ENHANCE_PARAMS
        self.face_detector = face_detector

    def process_face(self, face_image, brighten_factor=0.8, darken_factor=0.5,
                     low_cutoff_percent=40, high_cutoff_percent=80, ellipse_info=None,
                     border_cleanup_pixels=3):
        """处理人脸图像 - 在最后阶段进行边界清理"""
        try:
            # 转换为RGB（确保格式正确）
            if face_image.mode != 'RGB':
                face_image = face_image.convert('RGB')

            # 应用平滑双端像素调整，使用所有传入的参数
            processed_face = self._smooth_dual_adjustment(
                face_image,
                brighten_factor=brighten_factor,
                darken_factor=darken_factor,
                low_cutoff_percent=low_cutoff_percent,
                high_cutoff_percent=high_cutoff_percent
            )

            # 应用图像增强
            enhanced_face = self._enhance_image(processed_face)

            # 转换为黑白表情包风格
            bw_face = self._convert_to_emoji_style(enhanced_face)

            # 在最终图像上应用边界清理
            if ellipse_info and border_cleanup_pixels > 0:
                final_face = self.face_detector.apply_final_border_cleanup(
                    bw_face, ellipse_info, border_cleanup_pixels
                )
                print(f"✅ 最终边界清理完成: {border_cleanup_pixels}像素")
            else:
                final_face = bw_face
                print("⚠️ 未进行最终边界清理")

            return final_face

        except Exception as e:
            print(f"人脸处理错误: {str(e)}")
            return face_image  # 出错时返回原图

    def _convert_to_emoji_style(self, image):
        """转换为表情包风格：黑白+增强对比度"""
        print("⚫⚪ 转换为黑白表情包风格...")

        # 转换为灰度
        bw_image = image.convert('L')

        # 增强对比度
        enhancer = ImageEnhance.Contrast(bw_image)
        bw_image = enhancer.enhance(1.2)

        print("✅ 黑白转换完成")
        return bw_image

    def _smooth_dual_adjustment(self, image, low_cutoff_percent=40, high_cutoff_percent=10,
                                darken_factor=0.50, brighten_factor=0.80):
        """平滑双端像素调整：暗部按比例变暗，亮部按比例变亮"""
        try:
            print("🎯 应用平滑双端像素调整...")
            print(f"📊 使用参数:")
            print(f"   - 暗比例: {darken_factor}")
            print(f"   - 亮比例: {brighten_factor}")
            print(f"   - 暗阈值: {low_cutoff_percent}%")
            print(f"   - 亮阈值: {high_cutoff_percent}%")

            # 转换为numpy数组并转为float类型
            img_array = np.array(image).astype(np.float32)

            # 计算灰度值
            gray = np.mean(img_array, axis=2)

            # 计算阈值
            flat_gray = gray.flatten()
            low_threshold = np.percentile(flat_gray, low_cutoff_percent)
            high_threshold = np.percentile(flat_gray, 100 - high_cutoff_percent)

            # 创建结果数组
            result = img_array.copy()

            # 对低亮度区域进行平滑变暗
            low_mask = gray < low_threshold
            if np.any(low_mask):
                result[low_mask] = result[low_mask] * (1.0 - darken_factor)

            # 对高亮度区域进行平滑变亮
            high_mask = gray > high_threshold
            if np.any(high_mask):
                result[high_mask] = result[high_mask] + (255 - result[high_mask]) * brighten_factor

            # 限制在0-255范围内并转换回uint8
            result = np.clip(result, 0, 255).astype(np.uint8)

            # 转换为PIL图像
            result_image = Image.fromarray(result)

            print(f"📊 平滑双端调整完成:")
            print(f"   - 低阈值: {low_threshold:.1f} (最低{low_cutoff_percent}%平滑变暗)")
            print(f"   - 高阈值: {high_threshold:.1f} (最高{high_cutoff_percent}%平滑变亮)")
            print(f"   - 变暗强度: {darken_factor}, 变亮强度: {brighten_factor}")
            print(f"   - 影响像素: 变暗={np.sum(low_mask)}, 变亮={np.sum(high_mask)}")

            return result_image

        except Exception as e:
            print(f"⚠️ 平滑双端调整失败: {e}")
            return image

    def _enhance_image(self, image):
        """增强图像质量 - 使用配置中的所有参数"""
        print("🎨 应用图像增强...")
        print(f"📊 使用参数: {self.enhance_params}")

        # 亮度调整
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.enhance_params['brightness'])
        print(f"   ✅ 亮度调整: {self.enhance_params['brightness']}")

        # 曝光调整
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(self.enhance_params['exposure'])
        print(f"   ✅ 曝光调整: {self.enhance_params['exposure']}")

        # 对比度调整
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(self.enhance_params['contrast'])
        print(f"   ✅ 对比度调整: {self.enhance_params['contrast']}")

        # 饱和度调整
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(self.enhance_params['saturation'])
        print(f"   ✅ 饱和度调整: {self.enhance_params['saturation']}")

        # 自然饱和度调整
        image = self._adjust_vibrance(image, self.enhance_params['vibrance'])
        print(f"   ✅ 自然饱和度调整: {self.enhance_params['vibrance']}")

        # 色温调整
        image = self._adjust_color_temperature(image, self.enhance_params['temperature'])
        print(f"   ✅ 色温调整: {self.enhance_params['temperature']}")

        # 色调调整
        image = self._adjust_hue(image, self.enhance_params['hue'])
        print(f"   ✅ 色调调整: {self.enhance_params['hue']}")

        # 光感调整
        image = self._adjust_lightness(image, self.enhance_params['lightness'])
        print(f"   ✅ 光感调整: {self.enhance_params['lightness']}")

        print("✅ 图像增强完成")
        return image

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
