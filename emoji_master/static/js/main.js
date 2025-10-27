class EmojiMaster {
    constructor() {
        this.initializeEventListeners();
        this.currentResultImage = null;
        this.currentFile = null; // 添加这个属性来保存当前文件
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const photoInput = document.getElementById('photoInput');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const regenerateBtn = document.getElementById('regenerateBtn');

        // 上传区域点击事件
        uploadArea.addEventListener('click', () => {
            photoInput.click();
        });

        // 文件选择事件
        photoInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });

        // 拖拽事件
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileDrop(e);
        });

        // 生成按钮事件
        generateBtn.addEventListener('click', () => {
            this.generateEmoji();
        });

        // 下载按钮事件
        downloadBtn.addEventListener('click', () => {
            this.downloadResult();
        });

        // 重新生成按钮事件
        regenerateBtn.addEventListener('click', () => {
            this.showUploadSection();
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.validateAndSetFile(file);
        }
    }

    handleFileDrop(event) {
        const file = event.dataTransfer.files[0];
        if (file) {
            this.validateAndSetFile(file);
        }
    }

    validateAndSetFile(file) {
        // 验证文件类型
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('请上传 JPG、PNG 或 GIF 格式的图片');
            return;
        }

        // 验证文件大小 (5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showError('文件大小不能超过 5MB');
            return;
        }

        // 保存当前文件
        this.currentFile = file;

        // 显示文件预览
        this.displayFilePreview(file);

        // 启用生成按钮
        document.getElementById('generateBtn').disabled = false;
    }

    displayFilePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const uploadArea = document.getElementById('uploadArea');
            // 保留文件输入元素，只是更新显示内容
            uploadArea.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">✅</div>
                    <h3>文件已选择</h3>
                    <p>${file.name}</p>
                    <p style="font-size: 0.8em; color: #666;">点击重新选择</p>
                </div>
                <input type="file" id="photoInput" accept=".jpg,.jpeg,.png,.gif" hidden>
            `;

            // 重新绑定文件输入事件
            const newPhotoInput = document.getElementById('photoInput');
            newPhotoInput.addEventListener('change', (e) => {
                this.handleFileSelect(e);
            });
        };
        reader.readAsDataURL(file);
    }

    async generateEmoji() {
        // 使用保存的 currentFile，而不是从 DOM 获取
        if (!this.currentFile) {
            this.showError('请先选择照片');
            return;
        }

        const styleSelect = document.getElementById('styleSelect');

        // 显示加载状态
        this.showLoading();

        const formData = new FormData();
        formData.append('photo', this.currentFile);
        formData.append('style', styleSelect.value);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showResult(result.image);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('生成表情包失败:', error);
            this.showError('网络错误，请稍后重试');
        }
    }

    showLoading() {
        this.hideAllSections();
        document.getElementById('loadingSection').style.display = 'block';
    }

    showResult(imageData) {
        this.hideAllSections();

        const resultSection = document.getElementById('resultSection');
        const resultImage = document.getElementById('resultImage');

        resultImage.src = imageData;
        this.currentResultImage = imageData;

        resultSection.style.display = 'block';
    }

    showError(message) {
        this.hideAllSections();

        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        errorMessage.textContent = message;
        errorSection.style.display = 'block';

        // 3秒后自动隐藏错误信息
        setTimeout(() => {
            errorSection.style.display = 'none';
        }, 3000);
    }

    showUploadSection() {
        this.hideAllSections();

        // 重置上传区域
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <div class="upload-icon">📁</div>
            <h3>点击或拖拽上传照片</h3>
            <p>支持 JPG、PNG 格式，文件大小 ≤ 5MB</p>
            <input type="file" id="photoInput" accept=".jpg,.jpeg,.png,.gif" hidden>
        `;

        // 重新绑定文件输入事件
        const newPhotoInput = document.getElementById('photoInput');
        newPhotoInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });

        // 重置状态
        this.currentFile = null;
        document.getElementById('generateBtn').disabled = true;
    }

    hideAllSections() {
        const sections = [
            'uploadSection',
            'resultSection',
            'loadingSection',
            'errorSection'
        ];

        sections.forEach(section => {
            const element = document.getElementById(section);
            if (element) {
                element.style.display = 'none';
            }
        });
    }

    downloadResult() {
        if (!this.currentResultImage) return;

        const link = document.createElement('a');
        link.href = this.currentResultImage;
        link.download = `表情包_${new Date().getTime()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new EmojiMaster();
});