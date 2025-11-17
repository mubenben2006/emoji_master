from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import base64
from io import BytesIO
import traceback

from config import Config
from models.face_detection import FaceDetector
from models.image_processing import FaceProcessor
from models.style_synthesis import StyleSynthesizer
from utils.file_manager import FileManager

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)

print(f"\n🚀 启动表情包大师应用")
print(f"📁 工作目录: {os.getcwd()}")
print(f"📁 应用目录: {Config.BASE_DIR}")

# 初始化各模块
print("🔄 初始化模块...")
face_detector = FaceDetector()
face_processor = FaceProcessor()
style_synthesizer = StyleSynthesizer()
file_manager = FileManager()
print("✅ 所有模块初始化完成")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_emoji():
    """生成表情包接口"""
    print("\n" + "=" * 60)
    print("🚀 收到生成表情包请求")

    try:
        
        # 检查文件上传
        if 'photo' not in request.files:
            print("❌ 没有文件上传")
            return jsonify({
                'status': 'error',
                'message': '请选择要上传的照片'
            }), 400

        photo_file = request.files['photo']
        style = request.form.get('style', 'panda')

        print(f"📸 上传文件: {photo_file.filename}")
        print(f"🎨 选择风格: {style}")

        # 验证文件
        if photo_file.filename == '':
            print("❌ 空文件名")
            return jsonify({
                'status': 'error',
                'message': '未选择文件'
            }), 400

        if not file_manager.allowed_file(photo_file.filename):
            print("❌ 不支持的文件格式")
            return jsonify({
                'status': 'error',
                'message': '不支持的文件格式，请上传JPG、PNG或GIF格式的图片'
            }), 400

        # 保存上传的文件
        upload_path = file_manager.save_upload_file(photo_file)
        print(f"💾 文件保存到: {upload_path}")
        print(f"💾 文件是否存在: {os.path.exists(upload_path)}")

        try:
            # 1. 人脸检测
            print("\n🔍 开始人脸检测...")
            face_image, confidence = face_detector.detect_faces_with_confidence(upload_path)
            print(f"📊 人脸检测置信度: {confidence}")

            if face_image is None or confidence < Config.FACE_DETECTION_CONFIDENCE:
                # 如果增强检测失败，尝试普通检测
                print("🔄 尝试普通人脸检测...")
                face_image, face_confidence = face_detector.detect_faces_with_confidence(upload_path)
                if face_image is None:
                    print("❌ 未检测到人脸")
                    return jsonify({
                        'status': 'error',
                        'message': '未检测到清晰人脸，请上传包含清晰正面人脸的图片'
                    }), 400

            print(f"✅ 人脸检测成功: {face_image.size}")

            # 2. 人脸处理
            print("\n🎨 开始人脸处理...")
            processed_face = face_processor.process_face(face_image)
            print("✅ 人脸处理完成")

            # 3. 风格合成
            print("\n🔄 开始风格合成...")
            result_image = style_synthesizer.synthesize_style(processed_face, style)

            # 4. 转换为base64返回给前端
            buffered = BytesIO()
            result_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            print("🎉 表情包生成成功！")
            print("=" * 60)

            return jsonify({
                'status': 'success',
                'image': f"data:image/png;base64,{img_str}",
                'message': '表情包生成成功！'
            })

        except Exception as e:
            print(f"❌ 处理过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': '处理过程中出现错误，请重试'
            }), 500

        finally:
            # 清理临时文件
            file_manager.cleanup_file(upload_path)
            print(f"🧹 清理临时文件: {upload_path}")

    except Exception as e:
        print(f"💥 请求处理错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': '服务器内部错误'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载生成的表情包"""
    try:
        file_path = os.path.join(Config.RESULT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({
                'status': 'error',
                'message': '文件不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': '下载失败'
        }), 500

if __name__ == '__main__':
    print("\n🌐 启动Flask服务器...")
    app.run(debug=True, host='0.0.0.0', port=5000)
