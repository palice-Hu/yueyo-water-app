from PIL import Image, ImageEnhance
import os

class ImageWatermark:
    """
    图片水印类，负责在图片上添加图片水印
    """
    
    def __init__(self):
        self.watermark_image = None
        self.position = (0, 0)  # 默认位置 (x, y)
        self.opacity = 128  # 透明度 0-255
        self.scale = 1.0  # 缩放比例
        self.rotation = 0  # 旋转角度
    
    def load_watermark(self, file_path: str):
        """
        加载水印图片
        
        Args:
            file_path: 水印图片路径
        """
        try:
            self.watermark_image = Image.open(file_path)
            if self.watermark_image.mode != 'RGBA':
                self.watermark_image = self.watermark_image.convert('RGBA')
        except Exception as e:
            raise Exception(f"无法加载水印图片 {file_path}: {str(e)}")
    
    def set_position(self, position: tuple):
        """设置水印位置 (x, y)"""
        self.position = position
    
    def set_opacity(self, opacity: int):
        """设置透明度 (0-255)"""
        self.opacity = max(0, min(255, opacity))
    
    def set_scale(self, scale: float):
        """设置缩放比例"""
        self.scale = max(0.01, scale)  # 限制最小缩放为1%
    
    def set_rotation(self, rotation: int):
        """设置旋转角度"""
        self.rotation = rotation % 360
    
    def add_watermark(self, image: Image.Image) -> Image.Image:
        """
        在图片上添加图片水印
        
        Args:
            image: 原始图片
            
        Returns:
            添加水印后的图片
        """
        if self.watermark_image is None:
            return image
            
        # 复制原始图片避免修改原图
        img = image.copy()
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 调整水印大小
        watermark = self.watermark_image.copy()
        if self.scale != 1.0:
            new_width = int(watermark.width * self.scale)
            new_height = int(watermark.height * self.scale)
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 调整水印透明度
        if self.opacity < 255:
            alpha = watermark.split()[-1]  # 获取alpha通道
            alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity / 255.0)
            watermark.putalpha(alpha)
        
        # 旋转水印
        if self.rotation != 0:
            watermark = watermark.rotate(self.rotation, expand=True)
        
        # 确保水印位置在图片范围内
        x = max(0, min(self.position[0], img.width - watermark.width))
        y = max(0, min(self.position[1], img.height - watermark.height))
        
        # 将水印粘贴到图片上
        img.paste(watermark, (x, y), watermark)
        
        return img