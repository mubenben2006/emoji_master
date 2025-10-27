import os
import uuid
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from PIL import Image

from config import Config


class FileManager:
    """文件管理模块"""

    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        self.result_folder = Config.RESULT_FOLDER
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS

    def allowed_file(self, filename):
        """检查文件格式是否允许"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_upload_file(self, file):
        """保存上传的文件"""
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(self.upload_folder, unique_filename)

        # 保存文件
        file.save(file_path)
        return file_path

    def save_result_image(self, image):
        """保存结果图像"""
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_result.png"
        file_path = os.path.join(self.result_folder, unique_filename)

        # 保存图像
        image.save(file_path, 'PNG')
        return file_path

    def cleanup_file(self, file_path):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"文件清理错误: {str(e)}")

    def cleanup_old_files(self, hours=24):
        """清理超过指定时间的旧文件"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=hours)

            # 清理上传文件夹
            for folder in [self.upload_folder, self.result_folder]:
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        if file_time < cutoff_time:
                            os.remove(file_path)

        except Exception as e:
            print(f"清理旧文件错误: {str(e)}")