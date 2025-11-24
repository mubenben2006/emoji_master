
class EmojiMaster {
    constructor() {
        this.initializeEventListeners();
        this.currentResultImage = null;
        this.currentFile = null;
        this.brightenFactor = 0.8;
        this.darkenFactor = 0.5;
        this.lowCutoffPercent = 40;
        this.highCutoffPercent = 80;
        this.borderCleanupPixels = 3; // 默认3像素清理
        this.isAdvancedOpen = false;
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const photoInput = document.getElementById('photoInput');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const regenerateBtn = document.getElementById('regenerateBtn');
        const brightenSlider = document.getElementById('brightenSlider');
        const darkenSlider = document.getElementById('darkenSlider');
        const lowThresholdSlider = document.getElementById('lowThresholdSlider');
        const highThresholdSlider = document.getElementById('highThresholdSlider');
        const borderCleanupSlider = document.getElementById('borderCleanupSlider');
        const advancedControls = document.querySelector('.advanced-controls');
        const styleOptions = document.querySelectorAll('.style-option');

        // 上传区域事件
        uploadArea.addEventListener('click', () => {
            photoInput.click();
        });

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

        // 风格选择事件
        styleOptions.forEach(option => {
            option.addEventListener('click', () => {
                styleOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
            });
        });

        // 滑块事件
        brightenSlider.addEventListener('input', (e) => {
            this.brightenFactor = parseFloat(e.target.value);
            document.getElementById('brightenValue').textContent = this.brightenFactor.toFixed(1);
        });

        darkenSlider.addEventListener('input', (e) => {
            this.darkenFactor = parseFloat(e.target.value);
            document.getElementById('darkenValue').textContent = this.darkenFactor.toFixed(1);
        });

        lowThresholdSlider.addEventListener('input', (e) => {
            this.lowCutoffPercent = parseInt(e.target.value);
            document.getElementById('lowThresholdValue').textContent = this.lowCutoffPercent + '%';
        });

        highThresholdSlider.addEventListener('input', (e) => {
            this.highCutoffPercent = parseInt(e.target.value);
            document.getElementById('highThresholdValue').textContent = this.highCutoffPercent + '%';
        });

        // 边界清理滑块事件
        borderCleanupSlider.addEventListener('input', (e) => {
            this.borderCleanupPixels = parseInt(e.target.value);
            document.getElementById('borderCleanupValue').textContent = this.borderCleanupPixels + 'px';
        });

        // 高级控制面板切换
        advancedControls.addEventListener('click', (e) => {
            if (e.target.closest('.controls-header')) {
                this.toggleAdvancedControls();
            }
        });

        // 按钮事件
        generateBtn.addEventListener('click', () => {
            this.generateEmoji();
        });

        downloadBtn.addEventListener('click', () => {
            this.downloadResult();
        });

        regenerateBtn.addEventListener('click', () => {
            this.showUploadSection();
        });

        // 图片点击下载
        document.getElementById('resultImage')?.addEventListener('click', () => {
            this.downloadResult();
        });
    }

    toggleAdvancedControls() {
        const controlsContent = document.querySelector('.controls-content');
        const toggleArrow = document.querySelector('.toggle-arrow i');
        
        this.isAdvancedOpen = !this.isAdvancedOpen;
        
        if (this.isAdvancedOpen) {
            controlsContent.style.display = 'grid';
            toggleArrow.style.transform = 'rotate(180deg)';
        } else {
            controlsContent.style.display = 'none';
            toggleArrow.style.transform = 'rotate(0deg)';
        }
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
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('请上传 JPG、PNG 或 GIF 格式的图片');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            this.showError('文件大小不能超过 5MB');
            return;
        }

        this.currentFile = file;
        this.displayFilePreview(file);
        document.getElementById('generateBtn').disabled = false;
    }

    displayFilePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const uploadArea = document.getElementById('uploadArea');
            uploadArea.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px; color: #4facfe;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h3>文件已选择</h3>
                    <p style="margin-bottom: 10px;">${file.name}</p>
                    <div class="file-info">
                        <i class="fas fa-info-circle"></i>
                        <span>点击重新选择</span>
                    </div>
                </div>
                <input type="file" id="photoInput" accept=".jpg,.jpeg,.png,.gif" hidden>
            `;

            const newPhotoInput = document.getElementById('photoInput');
            newPhotoInput.addEventListener('change', (e) => {
                this.handleFileSelect(e);
            });
        };
        reader.readAsDataURL(file);
    }

    getSelectedStyle() {
        const activeOption = document.querySelector('.style-option.active');
        return activeOption ? activeOption.dataset.style : 'panda';
    }

    async generateEmoji() {
        if (!this.currentFile) {
            this.showError('请先选择照片');
            return;
        }

        console.log('🔍 前端调试 - 边界清理像素:', this.borderCleanupPixels);

        this.showLoading();

        const formData = new FormData();
        formData.append('photo', this.currentFile);
        formData.append('style', this.getSelectedStyle());
        formData.append('brighten_factor', this.brightenFactor);
        formData.append('darken_factor', this.darkenFactor);
        formData.append('low_cutoff_percent', this.lowCutoffPercent);
        formData.append('high_cutoff_percent', this.highCutoffPercent);
        formData.append('border_cleanup_pixels', this.borderCleanupPixels);

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

        setTimeout(() => {
            errorSection.style.display = 'none';
        }, 5000);
    }

    showUploadSection() {
        this.hideAllSections();

        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <h3>上传照片开始创作</h3>
            <p>拖拽或点击上传 JPG、PNG 格式图片</p>
            <div class="file-info">
                <i class="fas fa-info-circle"></i>
                <span>文件大小 ≤ 5MB</span>
            </div>
            <input type="file" id="photoInput" accept=".jpg,.jpeg,.png,.gif" hidden>
        `;

        const newPhotoInput = document.getElementById('photoInput');
        newPhotoInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });

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
