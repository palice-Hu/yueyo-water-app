import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QGroupBox, QLineEdit, QSpinBox, QColorDialog
from PyQt5.QtWidgets import QComboBox, QSlider, QFormLayout, QCheckBox, QTabWidget, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QColor

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_handler import FileHandler
from modules.text_watermark import TextWatermark
from modules.image_watermark import ImageWatermark
from PIL import Image

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileHandler()
        self.text_watermark = TextWatermark()
        self.image_watermark = ImageWatermark()
        self.image_files = []  # 存储导入的图片文件路径
        self.current_image = None  # 当前选中的图片
        self.current_watermark_image_path = None  # 当前水印图片路径
        self.watermark_type = "text"  # 水印类型：text 或 image
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('水印工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 图片列表和导入导出按钮
        left_panel = QVBoxLayout()
        
        # 图片导入区域
        import_group = QGroupBox("图片导入")
        import_layout = QVBoxLayout()
        self.import_btn = QPushButton("导入图片")
        self.import_btn.clicked.connect(self.import_images)
        self.import_folder_btn = QPushButton("导入文件夹")
        self.import_folder_btn.clicked.connect(self.import_folder)
        import_layout.addWidget(self.import_btn)
        import_layout.addWidget(self.import_folder_btn)
        import_group.setLayout(import_layout)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.image_list.itemSelectionChanged.connect(self.on_image_selected)
        
        # 导出区域
        export_group = QGroupBox("导出设置")
        export_layout = QVBoxLayout()
        self.export_btn = QPushButton("导出图片")
        self.export_btn.clicked.connect(self.export_images)
        export_layout.addWidget(self.export_btn)
        export_group.setLayout(export_layout)
        
        left_panel.addWidget(import_group)
        left_panel.addWidget(self.image_list)
        left_panel.addWidget(export_group)
        
        # 中间面板 - 水印设置
        middle_panel = QVBoxLayout()
        
        # 水印类型选择
        type_group = QGroupBox("水印类型")
        type_layout = QHBoxLayout()
        self.text_radio = QRadioButton("文本水印")
        self.text_radio.setChecked(True)
        self.text_radio.toggled.connect(self.on_watermark_type_changed)
        self.image_radio = QRadioButton("图片水印")
        self.image_radio.toggled.connect(self.on_watermark_type_changed)
        type_layout.addWidget(self.text_radio)
        type_layout.addWidget(self.image_radio)
        type_layout.addStretch()
        type_group.setLayout(type_layout)
        
        # 水印设置标签页
        self.settings_tabs = QTabWidget()
        
        # 文本水印设置
        self.create_text_watermark_tab()
        
        # 图片水印设置
        self.create_image_watermark_tab()
        
        middle_panel.addWidget(type_group)
        middle_panel.addWidget(self.settings_tabs)
        
        # 右侧面板 - 预览
        right_panel = QVBoxLayout()
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("请选择图片进行预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 500)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        
        right_panel.addWidget(preview_group)
        
        # 添加到主布局
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(middle_panel, 1)
        main_layout.addLayout(right_panel, 2)
    
    def create_text_watermark_tab(self):
        """创建文本水印设置标签页"""
        text_watermark_widget = QWidget()
        text_layout = QFormLayout()
        
        # 文本内容
        self.text_input = QLineEdit("水印文本")
        self.text_input.textChanged.connect(lambda text: self.text_watermark.set_text(text))
        text_layout.addRow("文本内容:", self.text_input)
        
        # 字体大小
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(10, 100)
        self.font_size_input.setValue(36)
        self.font_size_input.valueChanged.connect(lambda size: self.text_watermark.set_font(self.text_watermark.font_family, size))
        text_layout.addRow("字体大小:", self.font_size_input)
        
        # 字体颜色
        color_layout = QHBoxLayout()
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.select_color)
        self.color_label = QLabel()
        self.color_label.setStyleSheet("background-color: rgb(255, 255, 255); border: 1px solid black;")
        self.color_label.setFixedWidth(50)
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        text_layout.addRow("字体颜色:", color_layout)
        
        # 透明度
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(128)
        self.opacity_slider.valueChanged.connect(lambda value: self.text_watermark.set_opacity(value))
        text_layout.addRow("透明度:", self.opacity_slider)
        
        # 高级文本设置
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QVBoxLayout()
        
        # 粗体和斜体
        style_layout = QHBoxLayout()
        self.bold_checkbox = QCheckBox("粗体")
        self.bold_checkbox.stateChanged.connect(lambda state: self.text_watermark.set_bold(state == Qt.Checked))
        self.italic_checkbox = QCheckBox("斜体")
        self.italic_checkbox.stateChanged.connect(lambda state: self.text_watermark.set_italic(state == Qt.Checked))
        style_layout.addWidget(self.bold_checkbox)
        style_layout.addWidget(self.italic_checkbox)
        advanced_layout.addLayout(style_layout)
        
        # 阴影效果
        shadow_layout = QHBoxLayout()
        self.shadow_checkbox = QCheckBox("阴影效果")
        self.shadow_checkbox.stateChanged.connect(self.on_shadow_changed)
        shadow_layout.addWidget(self.shadow_checkbox)
        advanced_layout.addLayout(shadow_layout)
        
        # 描边效果
        stroke_layout = QHBoxLayout()
        self.stroke_checkbox = QCheckBox("描边效果")
        self.stroke_checkbox.stateChanged.connect(self.on_stroke_changed)
        stroke_layout.addWidget(self.stroke_checkbox)
        advanced_layout.addLayout(stroke_layout)
        
        advanced_group.setLayout(advanced_layout)
        text_layout.addRow(advanced_group)
        
        text_watermark_widget.setLayout(text_layout)
        self.settings_tabs.addTab(text_watermark_widget, "文本水印")
    
    def create_image_watermark_tab(self):
        """创建图片水印设置标签页"""
        image_watermark_widget = QWidget()
        image_layout = QFormLayout()
        
        # 图片水印导入
        import_layout = QHBoxLayout()
        self.import_watermark_btn = QPushButton("导入水印图片")
        self.import_watermark_btn.clicked.connect(self.import_watermark_image)
        self.watermark_preview = QLabel("无水印图片")
        self.watermark_preview.setFixedHeight(100)
        self.watermark_preview.setAlignment(Qt.AlignCenter)
        self.watermark_preview.setStyleSheet("border: 1px solid gray;")
        import_layout.addWidget(self.import_watermark_btn)
        import_layout.addWidget(self.watermark_preview)
        image_layout.addRow("水印图片:", import_layout)
        
        # 缩放
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(1, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(lambda value: self.image_watermark.set_scale(value / 100.0))
        image_layout.addRow("缩放比例:", self.scale_slider)
        
        # 透明度
        self.image_opacity_slider = QSlider(Qt.Horizontal)
        self.image_opacity_slider.setRange(0, 255)
        self.image_opacity_slider.setValue(128)
        self.image_opacity_slider.valueChanged.connect(lambda value: self.image_watermark.set_opacity(value))
        image_layout.addRow("透明度:", self.image_opacity_slider)
        
        image_watermark_widget.setLayout(image_layout)
        self.settings_tabs.addTab(image_watermark_widget, "图片水印")
    
    def on_watermark_type_changed(self):
        """当水印类型改变时"""
        if self.text_radio.isChecked():
            self.watermark_type = "text"
        else:
            self.watermark_type = "image"
        self.update_preview()
    
    def on_shadow_changed(self, state):
        """当阴影效果改变时"""
        if state == Qt.Checked:
            self.text_watermark.set_shadow(True)
        else:
            self.text_watermark.set_shadow(False)
        self.update_preview()
    
    def on_stroke_changed(self, state):
        """当描边效果改变时"""
        if state == Qt.Checked:
            self.text_watermark.set_stroke(True)
        else:
            self.text_watermark.set_stroke(False)
        self.update_preview()
    
    def import_images(self):
        """导入图片文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择图片文件", 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_paths:
            # 筛选出支持的格式
            supported_files = self.file_handler.get_supported_files(file_paths)
            self.image_files.extend(supported_files)
            self.update_image_list()
    
    def import_folder(self):
        """导入整个文件夹的图片"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        
        if folder_path:
            try:
                image_files = self.file_handler.load_images_from_folder(folder_path)
                self.image_files.extend(image_files)
                self.update_image_list()
            except Exception as e:
                print(f"导入文件夹失败: {str(e)}")
    
    def import_watermark_image(self):
        """导入水印图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择水印图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_path:
            try:
                self.image_watermark.load_watermark(file_path)
                self.current_watermark_image_path = file_path
                
                # 显示水印图片预览
                pixmap = QPixmap(file_path)
                self.watermark_preview.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.watermark_preview.setText("")
                
                self.update_preview()
            except Exception as e:
                print(f"导入水印图片失败: {str(e)}")
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_list.clear()
        for file_path in self.image_files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.UserRole, file_path)  # 保存完整路径
            self.image_list.addItem(item)
    
    def on_image_selected(self):
        """当图片被选中时"""
        selected_items = self.image_list.selectedItems()
        if selected_items:
            file_path = selected_items[0].data(Qt.UserRole)
            try:
                self.current_image = self.file_handler.load_image(file_path)
                self.update_preview()
            except Exception as e:
                print(f"加载图片失败: {str(e)}")
    
    def update_preview(self):
        """更新预览"""
        if self.current_image:
            # 根据水印类型添加水印
            if self.watermark_type == "text":
                watermarked_image = self.text_watermark.add_watermark(self.current_image.copy())
            else:
                if self.image_watermark.watermark_image is None:
                    self.preview_label.setText("请先选择水印图片")
                    return
                watermarked_image = self.image_watermark.add_watermark(self.current_image.copy())
            
            # 显示预览图片
            self.display_image(watermarked_image)
    
    def display_image(self, image):
        """在预览区域显示图片"""
        # 转换PIL图像为QPixmap并显示
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        data = image.tobytes("raw", "RGB")
        qimage = QImage(data, image.width, image.height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # 缩放图片以适应预览区域
        scaled_pixmap = pixmap.scaled(
            self.preview_label.width() - 10, 
            self.preview_label.height() - 10, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setText("")
    
    def select_color(self):
        """选择字体颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())
            self.text_watermark.set_color(rgb)
            self.color_label.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border: 1px solid black;")
            self.update_preview()
    
    def export_images(self):
        """导出添加水印后的图片"""
        if not self.image_files:
            return
            
        # 选择导出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
            
        # 处理并导出每张图片
        for file_path in self.image_files:
            try:
                # 加载图片
                image = self.file_handler.load_image(file_path)
                
                # 添加水印
                if self.watermark_type == "text":
                    watermarked_image = self.text_watermark.add_watermark(image)
                else:
                    if self.image_watermark.watermark_image is not None:
                        watermarked_image = self.image_watermark.add_watermark(image)
                    else:
                        watermarked_image = image  # 没有水印图片时导出原图
                
                # 生成输出文件名
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_watermarked{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存图片
                self.file_handler.save_image(watermarked_image, output_path)
            except Exception as e:
                print(f"导出图片失败 {file_path}: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = WatermarkApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()