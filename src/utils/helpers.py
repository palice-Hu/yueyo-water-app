import os
import sys
from PIL import Image
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt

class UIHelpers:
    """
    UI辅助类，提供界面美化和辅助功能
    """
    
    @staticmethod
    def create_pixmap_from_pil_image(pil_image: Image.Image, max_size: tuple = None) -> QPixmap:
        """
        将PIL图像转换为QPixmap
        
        Args:
            pil_image: PIL图像对象
            max_size: 最大尺寸 (width, height)，如果提供则会缩放图像
            
        Returns:
            QPixmap对象
        """
        # 确保图像是RGB模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 获取图像数据
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # 如果提供了最大尺寸，则缩放图像
        if max_size:
            pixmap = pixmap.scaled(
                max_size[0], 
                max_size[1], 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
        
        return pixmap
    
    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """
        获取资源文件的绝对路径（支持打包后的exe）
        
        Args:
            relative_path: 相对路径
            
        Returns:
            资源文件的绝对路径
        """
        try:
            # PyInstaller创建的临时文件夹
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def validate_image_file(file_path: str) -> bool:
        """
        验证文件是否为有效的图像文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为有效的图像文件
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False

class ImageUtils:
    """
    图像处理工具类
    """
    
    @staticmethod
    def resize_image_proportionally(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """
        按比例调整图像大小
        
        Args:
            image: 原始图像
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            调整大小后的图像
        """
        original_width, original_height = image.size
        ratio = min(max_width / original_width, max_height / original_height)
        
        if ratio < 1:  # 只有当图像大于最大尺寸时才缩小
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def calculate_watermark_position(image_size: tuple, watermark_size: tuple, position_type: str = "center") -> tuple:
        """
        计算水印位置
        
        Args:
            image_size: 图像尺寸 (width, height)
            watermark_size: 水印尺寸 (width, height)
            position_type: 位置类型 (top-left, top-center, top-right, center-left, center, center-right,
                          bottom-left, bottom-center, bottom-right)
            
        Returns:
            水印位置 (x, y)
        """
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        positions = {
            "top-left": (10, 10),
            "top-center": ((img_width - wm_width) // 2, 10),
            "top-right": (img_width - wm_width - 10, 10),
            "center-left": (10, (img_height - wm_height) // 2),
            "center": ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
            "center-right": (img_width - wm_width - 10, (img_height - wm_height) // 2),
            "bottom-left": (10, img_height - wm_height - 10),
            "bottom-center": ((img_width - wm_width) // 2, img_height - wm_height - 10),
            "bottom-right": (img_width - wm_width - 10, img_height - wm_height - 10)
        }
        
        return positions.get(position_type, positions["center"])