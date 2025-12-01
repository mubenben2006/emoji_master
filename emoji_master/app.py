from flask import Flask, render_template, request, jsonify, send_file
import os
import uuid
import base64
from io import BytesIO
import traceback
import json
from werkzeug.utils import secure_filename
from datetime import datetime

from config import Config
from models.face_detection import FaceDetector
from models.image_processing import FaceProcessor
from models.style_synthesis import StyleSynthesizer
from utils.file_manager import FileManager

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化各模块
face_detector = FaceDetector()
face_processor = FaceProcessor(face_detector)
style_synthesizer = StyleSynthesizer()
file_manager = FileManager()

# 模板管理文件路径
TEMPLATES_JSON = os.path.join(Config.STYLES_FOLDER, 'custom_templates.json')


def load_templates():
    """加载模板配置"""
    if os.path.exists(TEMPLATES_JSON):
        try:
            with open(TEMPLATES_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_templates(templates):
    """保存模板配置"""
    try:
        with open(TEMPLATES_JSON, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_emoji():
    """生成表情包接口 - 支持新参数"""
    try:
        if 'photo' not in request.files:
            return jsonify({'status': 'error', 'message': '请选择要上传的照片'}), 400

        photo_file = request.files['photo']
        style = request.form.get('style', 'panda')

        # 检查文件格式
        if photo_file.filename == '' or not file_manager.allowed_file(photo_file.filename):
            return jsonify({'status': 'error', 'message': '不支持的文件格式'}), 400

        # 保存上传的文件
        upload_path = file_manager.save_upload_file(photo_file)

        # 人脸检测
        face_image, confidence, ellipse_info = face_detector.detect_face(upload_path)
        if face_image is None or confidence < Config.FACE_DETECTION_CONFIDENCE:
            return jsonify({'status': 'error', 'message': '未检测到清晰人脸'}), 400

        # 获取处理参数 - 现在所有阈值都是0-100%
        processing_params = {
            'brighten_factor': float(request.form.get('brighten_factor', 50)),
            'darken_factor': float(request.form.get('darken_factor', 50)),
            'low_cutoff_percent': float(request.form.get('low_cutoff_percent', 30)),
            'high_cutoff_percent': float(request.form.get('high_cutoff_percent', 70)),
            'border_cleanup_pixels': int(request.form.get('border_cleanup_pixels', 2))
        }

        # 确保参数在有效范围内
        processing_params['brighten_factor'] = max(0, min(100, processing_params['brighten_factor']))
        processing_params['darken_factor'] = max(0, min(100, processing_params['darken_factor']))
        processing_params['low_cutoff_percent'] = max(0, min(100, processing_params['low_cutoff_percent']))
        processing_params['high_cutoff_percent'] = max(0, min(100, processing_params['high_cutoff_percent']))

        print(f"🎯 使用处理参数: {processing_params}")

        # 人脸处理
        processed_face = face_processor.process_face(face_image,
                                                     processing_params=processing_params,
                                                     ellipse_info=ellipse_info)

        # 风格合成
        result_image = style_synthesizer.synthesize_style(processed_face, style)

        # 转换为base64返回给前端
        buffered = BytesIO()
        result_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({
            'status': 'success',
            'image': f"data:image/png;base64,{img_str}",
            'message': '表情包生成成功！',
            'params': processing_params  # 返回使用的参数
        })

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': '处理过程中出现错误'}), 500

    finally:
        # 清理临时文件
        if 'upload_path' in locals() and os.path.exists(upload_path):
            file_manager.cleanup_file(upload_path)


@app.route('/upload_style', methods=['POST'])
def upload_style():
    """上传自定义风格模板"""
    try:
        if 'template' not in request.files:
            return jsonify({'status': 'error', 'message': '请选择模板文件'}), 400

        template_file = request.files['template']
        style_name = request.form.get('style_name', '').strip()
        description = request.form.get('description', '').strip()

        if not style_name or not template_file.filename.lower().endswith('.png'):
            return jsonify({'status': 'error', 'message': '无效的参数或文件格式'}), 400

        # 检查风格名称是否已存在
        templates = load_templates()
        if style_name in templates:
            return jsonify({'status': 'error', 'message': '该风格名称已存在'}), 400

        # 生成唯一文件名并保存
        filename = f"custom_{uuid.uuid4().hex}.png"
        template_path = os.path.join(Config.STYLES_FOLDER, filename)
        os.makedirs(Config.STYLES_FOLDER, exist_ok=True)
        template_file.save(template_path)

        # 保存模板信息
        templates[style_name] = {
            'filename': filename,
            'description': description,
            'created_at': str(datetime.now()),
            'type': 'custom'
        }

        if save_templates(templates):
            return jsonify({
                'status': 'success',
                'message': '模板上传成功',
                'style_name': style_name
            })
        else:
            if os.path.exists(template_path):
                os.remove(template_path)
            return jsonify({'status': 'error', 'message': '保存模板信息失败'}), 500

    except Exception as e:
        print(f"模板上传错误: {str(e)}")
        return jsonify({'status': 'error', 'message': f'上传失败: {str(e)}'}), 500


@app.route('/get_custom_templates', methods=['GET'])
def get_custom_templates():
    """获取所有自定义模板"""
    try:
        templates = load_templates()
        custom_templates = {}

        for style_name, info in templates.items():
            if info.get('type') == 'custom':
                file_path = os.path.join(Config.STYLES_FOLDER, info['filename'])
                if os.path.exists(file_path):
                    custom_templates[style_name] = info

        return jsonify({'status': 'success', 'templates': custom_templates})
    except Exception:
        return jsonify({'status': 'error', 'message': '获取模板失败'}), 500


@app.route('/delete_custom_template', methods=['POST'])
def delete_custom_template():
    """删除自定义模板"""
    try:
        data = request.get_json()
        style_name = data.get('style_name')

        if not style_name:
            return jsonify({'status': 'error', 'message': '缺少参数'}), 400

        templates = load_templates()

        if style_name not in templates:
            return jsonify({'status': 'error', 'message': '模板不存在'}), 404

        # 删除文件
        filename = templates[style_name]['filename']
        file_path = os.path.join(Config.STYLES_FOLDER, filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        # 从配置中删除
        del templates[style_name]
        save_templates(templates)

        return jsonify({'status': 'success', 'message': '删除成功'})

    except Exception:
        return jsonify({'status': 'error', 'message': '删除失败'}), 500


if __name__ == '__main__':
    # 确保必要的目录存在
    for folder in [Config.STYLES_FOLDER, Config.RESULT_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # 初始化自定义模板文件
    templates_file = os.path.join(Config.STYLES_FOLDER, 'custom_templates.json')
    if not os.path.exists(templates_file):
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    # 启动服务器
    host = getattr(Config, 'HOST', '0.0.0.0')
    port = getattr(Config, 'PORT', 5000)
    debug = getattr(Config, 'DEBUG', True)

    app.run(debug=debug, host=host, port=port)
