class EmojiMaster {
    constructor() {
        this.currentResultImage = null;
        this.currentFile = null;
        this.originalFile = null;
        this.originalStyle = null;
        this.brightenFactor = 50; // 默认50%
        this.darkenFactor = 50;   // 默认50%
        this.lowCutoffPercent = 30; // 暗阈值百分比 0-100%
        this.highCutoffPercent = 20; // 亮阈值百分比 0-100%
        this.borderCleanupPixels = 2;
        this.isAdvancedOpen = false;
        this.customStyles = new Map();
        this.editingStyle = null;
        this.rotation = 0;
        this.scale = 1;
        this.currentStyle = 'panda'; // 默认选中熊猫风格

        this.initializeEventListeners();
        this.loadCustomStyles();

        // 初始选择熊猫风格
        setTimeout(() => {
            const defaultStyleOption = document.querySelector('.style-option[data-style="panda"]');
            if (defaultStyleOption) {
                defaultStyleOption.classList.add('active');
            }
        }, 100);
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const photoInput = document.getElementById('photoInput');
        const generateBtn = document.getElementById('generateBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const newImageBtn = document.getElementById('newImageBtn');
        const resetBtn = document.getElementById('resetBtn');
        const retryBtn = document.getElementById('retryBtn');

        // 滑块控件
        const brightenSlider = document.getElementById('brightenSlider');
        const darkenSlider = document.getElementById('darkenSlider');
        const lowThresholdSlider = document.getElementById('lowThresholdSlider');
        const highThresholdSlider = document.getElementById('highThresholdSlider');
        const borderCleanupSlider = document.getElementById('borderCleanupSlider');

        // 高级控制面板
        const advancedControls = document.querySelector('.advanced-controls');
        const presetButtons = document.querySelectorAll('.preset-btn');

        // 图片操作按钮
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        const rotateBtn = document.getElementById('rotateBtn');

        // 自定义模板上传相关元素
        const addStyleBtn = document.getElementById('addStyleBtn');
        const styleUploadModal = document.getElementById('styleUploadModal');
        const closeModal = document.getElementById('closeModal');
        const cancelUpload = document.getElementById('cancelUpload');
        const templateUploadArea = document.getElementById('templateUploadArea');
        const templateInput = document.getElementById('templateInput');
        const templatePreview = document.getElementById('templatePreview');
        const templatePreviewImage = document.getElementById('templatePreviewImage');
        const templateSizeInfo = document.getElementById('templateSizeInfo');
        const styleName = document.getElementById('styleName');
        const styleDescription = document.getElementById('styleDescription');
        const confirmUpload = document.getElementById('confirmUpload');
        const changeTemplateBtn = document.getElementById('changeTemplateBtn');

        // 图片查看器
        const closeViewer = document.getElementById('closeViewer');
        const zoomInViewer = document.getElementById('zoomInViewer');
        const zoomOutViewer = document.getElementById('zoomOutViewer');
        const rotateViewer = document.getElementById('rotateViewer');
        const downloadViewer = document.getElementById('downloadViewer');

        // 结果区域调整相关元素
        const adjustBtn = document.getElementById('adjustBtn');
        const resultAdjustSection = document.getElementById('resultAdjustSection');
        const closeAdjust = document.getElementById('closeAdjust');
        const regenerateBtn = document.getElementById('regenerateBtn');
        const cancelAdjustBtn = document.getElementById('cancelAdjustBtn');

        // 结果区域滑块
        const resultBrightenSlider = document.getElementById('resultBrightenSlider');
        const resultDarkenSlider = document.getElementById('resultDarkenSlider');
        const resultLowThresholdSlider = document.getElementById('resultLowThresholdSlider');
        const resultHighThresholdSlider = document.getElementById('resultHighThresholdSlider');
        const resultBorderCleanupSlider = document.getElementById('resultBorderCleanupSlider');

        // ====== 核心功能事件 ======

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

        // 生成按钮
        generateBtn.addEventListener('click', () => {
            this.generateEmoji();
        });

        // 下载按钮
        downloadBtn.addEventListener('click', () => {
            this.downloadResult();
        });

        // 新图片按钮 - 修复：清除所有状态
        newImageBtn.addEventListener('click', () => {
            this.resetToUploadSection();
        });

        // 重置按钮
        resetBtn.addEventListener('click', () => {
            this.resetAllParameters();
            this.showSuccess('参数已重置为默认值');
        });

        // 重试按钮（仅用于错误情况）
        retryBtn.addEventListener('click', () => {
            if (this.currentFile) {
                this.generateEmoji();
            } else {
                this.resetToUploadSection();
            }
        });

        // ====== 风格选择事件 ======
        // 初始化系统风格选项的点击事件
        this.initializeStyleOptions();

        // ====== 滑块事件 ======
        brightenSlider.addEventListener('input', (e) => {
            this.brightenFactor = parseInt(e.target.value);
            document.getElementById('brightenValue').textContent = this.brightenFactor + '%';
        });

        darkenSlider.addEventListener('input', (e) => {
            this.darkenFactor = parseInt(e.target.value);
            document.getElementById('darkenValue').textContent = this.darkenFactor + '%';
        });

        lowThresholdSlider.addEventListener('input', (e) => {
            this.lowCutoffPercent = parseInt(e.target.value);
            document.getElementById('lowThresholdValue').textContent = this.lowCutoffPercent + '%';
        });

        highThresholdSlider.addEventListener('input', (e) => {
            this.highCutoffPercent = parseInt(e.target.value);
            document.getElementById('highThresholdValue').textContent = this.highCutoffPercent + '%';
        });

        borderCleanupSlider.addEventListener('input', (e) => {
            this.borderCleanupPixels = parseInt(e.target.value);
            document.getElementById('borderCleanupValue').textContent = this.borderCleanupPixels + 'px';
        });

        // 预设按钮 - 移除预设功能
        presetButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // 只保留重置功能
                this.resetAllParameters();
            });
        });

        // 高级控制面板切换
        advancedControls.addEventListener('click', (e) => {
            if (e.target.closest('.controls-header')) {
                this.toggleAdvancedControls();
            }
        });

        // ====== 图片操作事件 ======
        zoomInBtn?.addEventListener('click', () => {
            this.zoomImage(1.2);
        });

        zoomOutBtn?.addEventListener('click', () => {
            this.zoomImage(0.8);
        });

        rotateBtn?.addEventListener('click', () => {
            this.rotateImage(90);
        });

        // 图片点击下载
        document.getElementById('resultImage')?.addEventListener('click', () => {
            this.downloadResult();
        });

        // ====== 自定义模板管理事件 ======
        addStyleBtn.addEventListener('click', () => {
            this.openStyleUploadModal();
        });

        closeModal.addEventListener('click', () => {
            this.closeStyleUploadModal();
        });

        cancelUpload.addEventListener('click', () => {
            this.closeStyleUploadModal();
        });

        // 模板上传区域事件
        templateUploadArea.addEventListener('click', () => {
            templateInput.click();
        });

        templateInput.addEventListener('change', (e) => {
            this.handleTemplateSelect(e);
        });

        // 更换模板按钮
        changeTemplateBtn?.addEventListener('click', () => {
            templateInput.click();
        });

        // 模板设置表单事件
        styleName.addEventListener('input', () => {
            this.validateTemplateForm();
        });

        // 确认上传事件
        confirmUpload.addEventListener('click', () => {
            if (this.editingStyle) {
                this.updateCustomTemplate();
            } else {
                this.saveCustomTemplate();
            }
        });

        // 点击模态框外部关闭
        styleUploadModal.addEventListener('click', (e) => {
            if (e.target === styleUploadModal) {
                this.closeStyleUploadModal();
            }
        });

        // ====== 图片查看器事件 ======
        closeViewer?.addEventListener('click', () => {
            this.closeImageViewer();
        });

        zoomInViewer?.addEventListener('click', () => {
            this.zoomImage(1.2, true);
        });

        zoomOutViewer?.addEventListener('click', () => {
            this.zoomImage(0.8, true);
        });

        rotateViewer?.addEventListener('click', () => {
            this.rotateImage(90, true);
        });

        downloadViewer?.addEventListener('click', () => {
            this.downloadResult();
        });

        // 图片查看器点击外部关闭
        document.getElementById('imageViewer')?.addEventListener('click', (e) => {
            if (e.target.id === 'imageViewer') {
                this.closeImageViewer();
            }
        });

        // ====== 结果区域调整事件 ======
        adjustBtn?.addEventListener('click', () => {
            this.showAdjustPanel();
        });

        closeAdjust?.addEventListener('click', () => {
            this.hideAdjustPanel();
        });

        cancelAdjustBtn?.addEventListener('click', () => {
            this.hideAdjustPanel();
        });

        regenerateBtn?.addEventListener('click', () => {
            this.regenerateWithAdjustedParams();
        });

        // 结果区域滑块事件
        resultBrightenSlider?.addEventListener('input', (e) => {
            this.brightenFactor = parseInt(e.target.value);
            document.getElementById('resultBrightenValue').textContent = this.brightenFactor + '%';
        });

        resultDarkenSlider?.addEventListener('input', (e) => {
            this.darkenFactor = parseInt(e.target.value);
            document.getElementById('resultDarkenValue').textContent = this.darkenFactor + '%';
        });

        resultLowThresholdSlider?.addEventListener('input', (e) => {
            this.lowCutoffPercent = parseInt(e.target.value);
            document.getElementById('resultLowThresholdValue').textContent = this.lowCutoffPercent + '%';
        });

        resultHighThresholdSlider?.addEventListener('input', (e) => {
            this.highCutoffPercent = parseInt(e.target.value);
            document.getElementById('resultHighThresholdValue').textContent = this.highCutoffPercent + '%';
        });

        resultBorderCleanupSlider?.addEventListener('input', (e) => {
            this.borderCleanupPixels = parseInt(e.target.value);
            document.getElementById('resultBorderCleanupValue').textContent = this.borderCleanupPixels + 'px';
        });

        // 结果区域预设按钮 - 移除预设功能
        document.querySelectorAll('#resultAdjustSection .preset-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // 只保留重置功能
                this.resetAllParameters();
                this.showSuccess('参数已重置为默认值');
            });
        });

        // 结果区域高级控制面板切换
        const resultAdvancedControls = document.querySelector('#resultAdjustSection .advanced-controls');
        if (resultAdvancedControls) {
            resultAdvancedControls.addEventListener('click', (e) => {
                if (e.target.closest('.controls-header')) {
                    this.toggleResultAdvancedControls();
                }
            });
        }
    }

    // ====== 风格选择方法 ======
    initializeStyleOptions() {
        const styleOptions = document.querySelectorAll('.style-option:not(.custom)');
        styleOptions.forEach(option => {
            const newOption = option.cloneNode(true);
            option.parentNode.replaceChild(newOption, option);

            newOption.addEventListener('click', (e) => {
                if (!e.target.closest('.style-actions')) {
                    this.selectStyleOption(newOption);
                }
            });
        });
    }

    selectStyleOption(selectedOption) {
        document.querySelectorAll('.style-option').forEach(option => {
            option.classList.remove('active');
        });

        selectedOption.classList.add('active');
        this.currentStyle = selectedOption.dataset.style;

        const styleName = selectedOption.querySelector('span').textContent;
        console.log(`🎨 选择风格: ${this.currentStyle}`);
    }

    // ====== 核心功能方法 ======
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
        this.showSuccess(`已选择文件: ${file.name}`);
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

            const newPhotoInput = uploadArea.querySelector('#photoInput');
            newPhotoInput.addEventListener('change', (e) => {
                this.handleFileSelect(e);
            });

            this.initializeStyleOptions();
        };
        reader.readAsDataURL(file);
    }

    // 修复：重置到上传界面的方法
    resetToUploadSection() {
        // 重置所有状态
        this.currentFile = null;
        this.originalFile = null;
        this.currentResultImage = null;
        this.rotation = 0;
        this.scale = 1;

        // 重置参数到默认值
        this.resetAllParameters();

        // 显示上传界面
        this.showUploadSection();

        // 隐藏调整面板
        this.hideAdjustPanel();

        // 重置文件输入
        const photoInput = document.getElementById('photoInput');
        if (photoInput) {
            photoInput.value = '';
        }

        console.log('🔄 已重置到上传界面');
    }

    resetAllParameters() {
        this.brightenFactor = 50;
        this.darkenFactor = 50;
        this.lowCutoffPercent = 30;
        this.highCutoffPercent = 20;
        this.borderCleanupPixels = 2;

        document.getElementById('brightenSlider').value = this.brightenFactor;
        document.getElementById('darkenSlider').value = this.darkenFactor;
        document.getElementById('lowThresholdSlider').value = this.lowCutoffPercent;
        document.getElementById('highThresholdSlider').value = this.highCutoffPercent;
        document.getElementById('borderCleanupSlider').value = this.borderCleanupPixels;

        document.getElementById('brightenValue').textContent = this.brightenFactor + '%';
        document.getElementById('darkenValue').textContent = this.darkenFactor + '%';
        document.getElementById('lowThresholdValue').textContent = this.lowCutoffPercent + '%';
        document.getElementById('highThresholdValue').textContent = this.highCutoffPercent + '%';
        document.getElementById('borderCleanupValue').textContent = this.borderCleanupPixels + 'px';

        // 同时更新结果区域的滑块
        if (document.getElementById('resultBrightenSlider')) {
            document.getElementById('resultBrightenSlider').value = this.brightenFactor;
            document.getElementById('resultDarkenSlider').value = this.darkenFactor;
            document.getElementById('resultLowThresholdSlider').value = this.lowCutoffPercent;
            document.getElementById('resultHighThresholdSlider').value = this.highCutoffPercent;
            document.getElementById('resultBorderCleanupSlider').value = this.borderCleanupPixels;

            document.getElementById('resultBrightenValue').textContent = this.brightenFactor + '%';
            document.getElementById('resultDarkenValue').textContent = this.darkenFactor + '%';
            document.getElementById('resultLowThresholdValue').textContent = this.lowCutoffPercent + '%';
            document.getElementById('resultHighThresholdValue').textContent = this.highCutoffPercent + '%';
            document.getElementById('resultBorderCleanupValue').textContent = this.borderCleanupPixels + 'px';
        }
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

        console.log('🎨 开始生成表情包...');
        console.log('🎨 选择风格:', this.getSelectedStyle());
        console.log('🔧 参数设置:', {
            亮部增强: this.brightenFactor + '%',
            暗部减弱: this.darkenFactor + '%',
            暗阈值: this.lowCutoffPercent + '%',
            亮阈值: this.highCutoffPercent + '%',
            边界清理: this.borderCleanupPixels + 'px'
        });

        this.showLoading('AI正在创作中...');
        this.startLoadingAnimation();

        const formData = new FormData();
        formData.append('photo', this.currentFile);
        formData.append('style', this.getSelectedStyle());
        formData.append('brighten_factor', this.brightenFactor);
        formData.append('darken_factor', this.darkenFactor);
        formData.append('low_cutoff_percent', this.lowCutoffPercent);
        formData.append('high_cutoff_percent', this.highCutoffPercent);
        formData.append('border_cleanup_pixels', this.borderCleanupPixels);

        try {
            const startTime = Date.now();
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            const endTime = Date.now();
            const timeTaken = ((endTime - startTime) / 1000).toFixed(1);

            if (result.status === 'success') {
                this.showResult(result.image, timeTaken);
                this.showSuccess('表情包生成成功！');
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('生成表情包失败:', error);
            this.showError('网络错误，请稍后重试');
        }
    }

    startLoadingAnimation() {
        let progress = 0;
        const steps = ['人脸检测', '图像处理', '风格合成', '完成生成'];
        const tips = [
            '正在检测人脸位置和特征...',
            '正在应用亮暗调整算法...',
            '正在应用选择的风格模板...',
            '正在生成最终的表情包...'
        ];

        const progressInterval = setInterval(() => {
            if (progress < 100) {
                progress += Math.random() * 10 + 5;
                if (progress > 100) progress = 100;

                const progressFill = document.querySelector('.progress-fill');
                const progressText = document.getElementById('progressText');
                const stepIndex = Math.floor(progress / 25);

                if (progressFill) progressFill.style.width = progress + '%';
                if (progressText) progressText.textContent = Math.round(progress) + '%';

                document.querySelectorAll('.loading-step').forEach((step, index) => {
                    if (index <= stepIndex) {
                        step.classList.add('active');
                    } else {
                        step.classList.remove('active');
                    }
                });

                const loadingTip = document.getElementById('loadingTip');
                if (loadingTip && tips[stepIndex]) {
                    loadingTip.textContent = tips[stepIndex];
                }
            } else {
                clearInterval(progressInterval);
            }
        }, 500);
    }

    showResult(imageData, timeTaken) {
        this.hideAllSections();

        const resultSection = document.getElementById('resultSection');
        const resultImage = document.getElementById('resultImage');
        const generationTime = document.getElementById('generationTime');
        const generationDate = document.getElementById('generationDate');
        const usedStyle = document.getElementById('usedStyle');
        const imageDimensions = document.getElementById('imageDimensions');
        const imageSize = document.getElementById('imageSize');

        resultImage.src = imageData;
        this.currentResultImage = imageData;
        this.rotation = 0;
        this.scale = 1;

        // 保存当前文件供重新生成使用
        this.originalFile = this.currentFile;
        this.originalStyle = this.getSelectedStyle();

        if (generationTime) generationTime.textContent = timeTaken;
        if (generationDate) generationDate.textContent = new Date().toLocaleString('zh-CN');

        const activeStyleOption = document.querySelector('.style-option.active');
        const styleName = activeStyleOption ? activeStyleOption.querySelector('span').textContent : '熊猫头';
        if (usedStyle) usedStyle.textContent = styleName;

        const img = new Image();
        img.onload = () => {
            if (imageDimensions) imageDimensions.textContent = `${img.width}×${img.height} px`;
            if (imageSize) {
                const sizeKB = Math.round((imageData.length * 3) / 4 / 1024);
                imageSize.textContent = `${sizeKB} KB`;
            }
        };
        img.src = imageData;

        resultSection.style.display = 'block';

        // 自动显示调整面板
        this.showAdjustPanel();

        resultSection.classList.add('fade-in');
        setTimeout(() => {
            resultSection.classList.remove('fade-in');
        }, 500);
    }

    showUploadSection() {
        this.hideAllSections();
        this.hideAdjustPanel();

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

        const newPhotoInput = uploadArea.querySelector('#photoInput');
        newPhotoInput.addEventListener('change', (e) => {
            this.handleFileSelect(e);
        });

        document.getElementById('uploadSection').style.display = 'block';
        document.getElementById('generateBtn').disabled = true;

        this.initializeStyleOptions();
    }

    // ====== 自定义模板管理方法 ======
    loadCustomStyles() {
        console.log('🔄 加载自定义风格...');
        fetch('/get_custom_templates')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.customStyles = new Map(Object.entries(data.templates));
                    this.renderCustomStyles();
                    console.log(`✅ 加载了 ${Object.keys(data.templates).length} 个自定义风格`);
                } else {
                    console.warn('⚠️ 加载自定义风格失败:', data.message);
                }
            })
            .catch(error => {
                console.error('❌ 加载自定义风格失败:', error);
            });
    }

    renderCustomStyles() {
        const styleGrid = document.getElementById('styleGrid');
        const customOptions = styleGrid.querySelectorAll('.style-option.custom');

        customOptions.forEach(option => option.remove());

        this.customStyles.forEach((styleData, styleName) => {
            const styleOption = this.createStyleOption(styleName, styleData);
            styleGrid.appendChild(styleOption);
        });
    }

    createStyleOption(styleName, styleData) {
        const styleOption = document.createElement('div');
        styleOption.className = 'style-option custom';
        styleOption.dataset.style = styleName;
        styleOption.title = styleData.description || styleName;

        styleOption.innerHTML = `
            <div class="style-icon">🎨</div>
            <span>${styleName}</span>
            <div class="style-badge">自定义</div>
            <div class="style-actions">
                <button class="edit-style-btn" title="编辑">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="delete-style-btn" title="删除">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="style-tooltip">${styleData.description || '无描述'}</div>
        `;

        styleOption.addEventListener('click', (e) => {
            if (!e.target.closest('.style-actions')) {
                this.selectStyleOption(styleOption);
            }
        });

        const editBtn = styleOption.querySelector('.edit-style-btn');
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.openStyleUploadModal(styleName);
        });

        const deleteBtn = styleOption.querySelector('.delete-style-btn');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteCustomTemplate(styleName);
        });

        return styleOption;
    }

    openStyleUploadModal(styleName = null) {
        this.editingStyle = styleName;
        const modal = document.getElementById('styleUploadModal');
        const modalTitle = document.getElementById('modalTitle');
        const confirmBtn = document.getElementById('confirmUpload');

        document.getElementById('styleName').value = '';
        document.getElementById('styleDescription').value = '';
        document.getElementById('templatePreview').style.display = 'none';
        document.getElementById('templatePreviewImage').src = '';
        confirmBtn.disabled = true;

        if (styleName) {
            modalTitle.innerHTML = '<i class="fas fa-edit"></i> 编辑模板';
            confirmBtn.innerHTML = '<i class="fas fa-save"></i> 保存修改';

            const styleData = this.customStyles.get(styleName);
            if (styleData) {
                document.getElementById('styleName').value = styleName;
                document.getElementById('styleDescription').value = styleData.description || '';
                this.showTemplatePreviewFromServer(styleData.filename);
            }
        } else {
            modalTitle.innerHTML = '<i class="fas fa-upload"></i> 上传自定义模板';
            confirmBtn.innerHTML = '<i class="fas fa-save"></i> 保存模板';
        }

        modal.style.display = 'flex';
    }

    closeStyleUploadModal() {
        document.getElementById('styleUploadModal').style.display = 'none';
        this.editingStyle = null;
        this.resetTemplateForm();
    }

    resetTemplateForm() {
        document.getElementById('styleName').value = '';
        document.getElementById('styleDescription').value = '';
        document.getElementById('templatePreview').style.display = 'none';
        document.getElementById('templatePreviewImage').src = '';
        document.getElementById('confirmUpload').disabled = true;

        const templateInput = document.getElementById('templateInput');
        templateInput.value = '';
    }

    handleTemplateSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.type.includes('png')) {
            this.showError('请选择PNG格式的图片');
            return;
        }

        if (file.size > 2 * 1024 * 1024) {
            this.showError('文件大小不能超过2MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('templatePreview');
            const previewImage = document.getElementById('templatePreviewImage');
            const sizeInfo = document.getElementById('templateSizeInfo');

            previewImage.src = e.target.result;
            sizeInfo.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            preview.style.display = 'flex';

            this.validateTemplateForm();
        };
        reader.readAsDataURL(file);
    }

    validateTemplateForm() {
        const styleName = document.getElementById('styleName').value.trim();
        const hasTemplate = document.getElementById('templatePreview').style.display !== 'none';
        const confirmBtn = document.getElementById('confirmUpload');

        let isValid = hasTemplate && styleName.length > 0;

        if (this.editingStyle) {
            isValid = styleName.length > 0;
        }

        confirmBtn.disabled = !isValid;
    }

    async saveCustomTemplate() {
        const styleName = document.getElementById('styleName').value.trim();
        const description = document.getElementById('styleDescription').value.trim();
        const templateFile = document.getElementById('templateInput').files[0];

        if (!styleName) {
            this.showError('请输入风格名称');
            return;
        }

        if (!this.editingStyle && this.customStyles.has(styleName)) {
            this.showError('该风格名称已存在');
            return;
        }

        const formData = new FormData();
        formData.append('style_name', styleName);
        formData.append('description', description);

        if (templateFile) {
            formData.append('template', templateFile);
        }

        try {
            const response = await fetch('/upload_style', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.loadCustomStyles();
                this.closeStyleUploadModal();
                this.showSuccess(this.editingStyle ? '模板更新成功' : '模板上传成功');

                setTimeout(() => {
                    const newOption = document.querySelector(`.style-option[data-style="${styleName}"]`);
                    if (newOption) {
                        this.selectStyleOption(newOption);
                    }
                }, 500);
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('保存模板失败:', error);
            this.showError('保存失败，请检查网络连接');
        }
    }

    async deleteCustomTemplate(styleName) {
        if (!confirm(`确定要删除 "${styleName}" 风格吗？`)) {
            return;
        }

        try {
            const response = await fetch('/delete_custom_template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ style_name: styleName })
            });

            const result = await response.json();

            if (result.status === 'success') {
                const styleOption = document.querySelector(`.style-option[data-style="${styleName}"]`);
                if (styleOption) {
                    styleOption.remove();
                }

                this.customStyles.delete(styleName);

                if (this.getSelectedStyle() === styleName) {
                    const defaultOption = document.querySelector('.style-option[data-style="panda"]');
                    if (defaultOption) {
                        this.selectStyleOption(defaultOption);
                    }
                }

                this.showSuccess('风格已删除');
            } else {
                this.showError(result.message);
            }
        } catch (error) {
            console.error('删除模板失败:', error);
            this.showError('删除失败，请重试');
        }
    }

    showTemplatePreviewFromServer(filename) {
        const preview = document.getElementById('templatePreview');
        const previewImage = document.getElementById('templatePreviewImage');
        const sizeInfo = document.getElementById('templateSizeInfo');

        previewImage.src = `/static/styles/${filename}?t=${new Date().getTime()}`;
        sizeInfo.textContent = '自定义模板';
        preview.style.display = 'flex';
        this.validateTemplateForm();
    }

    // ====== 结果区域调整方法 ======
    showAdjustPanel() {
        this.syncParamsToResultPanel();

        const adjustSection = document.getElementById('resultAdjustSection');
        if (adjustSection) {
            adjustSection.style.display = 'block';

            // 确保调整面板展开
            const controlsContent = document.querySelector('#resultAdjustSection .controls-content');
            if (controlsContent) {
                controlsContent.style.display = 'grid';
            }

            adjustSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    hideAdjustPanel() {
        const adjustSection = document.getElementById('resultAdjustSection');
        if (adjustSection) {
            adjustSection.style.display = 'none';
        }
    }

    syncParamsToResultPanel() {
        document.getElementById('resultBrightenSlider').value = this.brightenFactor;
        document.getElementById('resultDarkenSlider').value = this.darkenFactor;
        document.getElementById('resultLowThresholdSlider').value = this.lowCutoffPercent;
        document.getElementById('resultHighThresholdSlider').value = this.highCutoffPercent;
        document.getElementById('resultBorderCleanupSlider').value = this.borderCleanupPixels;

        document.getElementById('resultBrightenValue').textContent = this.brightenFactor + '%';
        document.getElementById('resultDarkenValue').textContent = this.darkenFactor + '%';
        document.getElementById('resultLowThresholdValue').textContent = this.lowCutoffPercent + '%';
        document.getElementById('resultHighThresholdValue').textContent = this.highCutoffPercent + '%';
        document.getElementById('resultBorderCleanupValue').textContent = this.borderCleanupPixels + 'px';
    }

    syncParamsFromResultPanel() {
        this.brightenFactor = parseInt(document.getElementById('resultBrightenSlider').value);
        this.darkenFactor = parseInt(document.getElementById('resultDarkenSlider').value);
        this.lowCutoffPercent = parseInt(document.getElementById('resultLowThresholdSlider').value);
        this.highCutoffPercent = parseInt(document.getElementById('resultHighThresholdSlider').value);
        this.borderCleanupPixels = parseInt(document.getElementById('resultBorderCleanupSlider').value);
    }

    async regenerateWithAdjustedParams() {
        if (!this.originalFile) {
            this.showError('没有找到原始图片，请重新上传');
            return;
        }

        this.syncParamsFromResultPanel();

        console.log('🔄 使用新参数重新生成...');
        console.log('🔧 新参数:', {
            亮部增强: this.brightenFactor + '%',
            暗部减弱: this.darkenFactor + '%',
            暗阈值: this.lowCutoffPercent + '%',
            亮阈值: this.highCutoffPercent + '%',
            边界清理: this.borderCleanupPixels + 'px'
        });

        this.showLoading('正在重新生成表情包...');

        const formData = new FormData();
        formData.append('photo', this.originalFile);
        formData.append('style', this.originalStyle);
        formData.append('brighten_factor', this.brightenFactor);
        formData.append('darken_factor', this.darkenFactor);
        formData.append('low_cutoff_percent', this.lowCutoffPercent);
        formData.append('high_cutoff_percent', this.highCutoffPercent);
        formData.append('border_cleanup_pixels', this.borderCleanupPixels);

        try {
            const startTime = Date.now();
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            const endTime = Date.now();
            const timeTaken = ((endTime - startTime) / 1000).toFixed(1);

            if (result.status === 'success') {
                this.showResult(result.image, timeTaken);
                this.showSuccess('表情包已重新生成！');
            } else {
                this.showError(result.message);
                this.showResultSection();
            }
        } catch (error) {
            console.error('重新生成失败:', error);
            this.showError('重新生成失败，请重试');
            this.showResultSection();
        }
    }

    toggleResultAdvancedControls() {
        const controlsContent = document.querySelector('#resultAdjustSection .controls-content');
        const toggleArrow = document.querySelector('#resultAdjustSection .toggle-arrow i');

        if (controlsContent.style.display === 'none' || controlsContent.style.display === '') {
            controlsContent.style.display = 'grid';
            toggleArrow.style.transform = 'rotate(180deg)';
        } else {
            controlsContent.style.display = 'none';
            toggleArrow.style.transform = 'rotate(0deg)';
        }
    }

    // ====== 图片操作方法 ======
    zoomImage(factor, isViewer = false) {
        const image = isViewer ?
            document.getElementById('viewerImage') :
            document.getElementById('resultImage');

        this.scale *= factor;
        if (this.scale < 0.1) this.scale = 0.1;
        if (this.scale > 5) this.scale = 5;

        if (image) {
            image.style.transform = `rotate(${this.rotation}deg) scale(${this.scale})`;
        }
    }

    rotateImage(degrees, isViewer = false) {
        const image = isViewer ?
            document.getElementById('viewerImage') :
            document.getElementById('resultImage');

        this.rotation = (this.rotation + degrees) % 360;

        if (image) {
            image.style.transform = `rotate(${this.rotation}deg) scale(${this.scale})`;
        }
    }

    // ====== 通用工具方法 ======
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

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showLoading(message = 'AI正在创作中...') {
        this.hideAllSections();
        const loadingSection = document.getElementById('loadingSection');
        const loadingText = loadingSection.querySelector('h3');
        loadingText.textContent = message;
        loadingSection.style.display = 'block';
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

    showSuccess(message) {
        const toast = document.getElementById('successToast');
        const toastMessage = document.getElementById('toastMessage');

        toastMessage.textContent = message;
        toast.style.display = 'block';

        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
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

    showResultSection() {
        this.hideAllSections();
        const resultSection = document.getElementById('resultSection');
        if (resultSection) {
            resultSection.style.display = 'block';
        }
    }

    downloadResult() {
        if (!this.currentResultImage) return;

        const link = document.createElement('a');
        link.href = this.currentResultImage;
        link.download = `表情包_${new Date().getTime()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.showSuccess('表情包下载成功！');
    }

    closeImageViewer() {
        document.getElementById('imageViewer').style.display = 'none';
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.emojiMaster = new EmojiMaster();
    console.log('🚀 表情包大师初始化完成');
});
