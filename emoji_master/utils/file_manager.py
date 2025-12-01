import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from config import Config


class FileManager:
    """文件管理类 - 处理文件上传、保存和清理"""

    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER  # 这是字符串
        self.result_folder = Config.RESULT_FOLDER  # 这是字符串
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS

    def allowed_file(self, filename):
        """检查文件扩展名是否允许"""
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions

    def generate_unique_filename(self, original_filename):
        """生成唯一的文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
        return f"{timestamp}_{unique_id}.{extension}"

    def save_upload_file(self, file):
        """保存上传的文件"""
        try:
            if not self.allowed_file(file.filename):
                raise ValueError(f"不支持的文件类型: {file.filename}")

            # 生成安全且唯一的文件名
            original_filename = secure_filename(file.filename)
            unique_filename = self.generate_unique_filename(original_filename)

            # 使用 os.path.join 而不是 /
            file_path = os.path.join(self.upload_folder, unique_filename)

            # 确保目录存在
            os.makedirs(self.upload_folder, exist_ok=True)

            # 保存文件
            file.save(file_path)

            # 验证文件是否保存成功
            if not os.path.exists(file_path):
                raise IOError(f"文件保存失败: {file_path}")

            print(f"✅ 文件保存成功: {file_path}")
            return file_path

        except Exception as e:
            print(f"❌ 文件保存失败: {e}")
            raise

    def save_result_file(self, image, style_name):
        """保存生成的结果文件"""
        try:
            # 生成结果文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"emoji_{style_name}_{timestamp}.png"

            # 使用 os.path.join 而不是 /
            file_path = os.path.join(self.result_folder, filename)

            # 确保目录存在
            os.makedirs(self.result_folder, exist_ok=True)

            # 保存图像
            image.save(file_path, format='PNG')

            print(f"✅ 结果文件保存成功: {file_path}")
            return filename

        except Exception as e:
            print(f"❌ 结果文件保存失败: {e}")
            raise

    def cleanup_file(self, file_path, max_age_hours=24):
        """清理文件"""
        try:
            if isinstance(file_path, (str, Path)):
                file_path = str(file_path)  # 确保是字符串

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🧹 文件已清理: {file_path}")
                return True
            return False

        except Exception as e:
            print(f"⚠️ 文件清理失败: {e}")
            return False

    def cleanup_old_files(self, folder, max_age_hours=24):
        """清理指定文件夹中的旧文件"""
        try:
            if isinstance(folder, Path):
                folder = str(folder)

            if not os.path.exists(folder):
                return 0

            deleted_count = 0
            current_time = datetime.now()

            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    # 检查文件年龄
                    file_age = current_time - datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_age.total_seconds() > max_age_hours * 3600:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"🧹 清理旧文件: {file_path}")
                        except Exception as e:
                            print(f"⚠️ 无法删除文件 {file_path}: {e}")

            return deleted_count

        except Exception as e:
            print(f"❌ 清理旧文件失败: {e}")
            return 0

    def get_file_info(self, file_path):
        """获取文件信息"""
        try:
            if isinstance(file_path, Path):
                file_path = str(file_path)

            if not os.path.exists(file_path):
                return None

            stat_info = os.stat(file_path)
            return {
                'filename': os.path.basename(file_path),
                'size': stat_info.st_size,
                'created': datetime.fromtimestamp(stat_info.st_ctime),
                'modified': datetime.fromtimestamp(stat_info.st_mtime),
                'path': file_path
            }

        except Exception as e:
            print(f"❌ 获取文件信息失败: {e}")
            return None
