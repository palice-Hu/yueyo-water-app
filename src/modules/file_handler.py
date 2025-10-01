import os
from PIL import Image
from typing import List

class FileHandler:
    """
    文件处理类，负责图片的导入和导出
    """
    
    # 支持的图片格式
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    def __init__(self):
        pass
    
    def load_image(self, file_path: str) -> Image.Image:
        """
        加载单个图片文件
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            PIL Image对象
        """
        try:
            image = Image.open(file_path)
            # 保持原格式信息
            image.format = image.format if image.format else 'JPEG'
            return image
        except Exception as e:
            raise Exception(f"无法加载图片 {file_path}: {str(e)}")
    
    def load_images_from_folder(self, folder_path: str) -> List[str]:
        """
        从文件夹加载所有支持的图片文件路径
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            图片文件路径列表
        """
        image_files = []
        try:
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(self.SUPPORTED_FORMATS):
                    image_files.append(os.path.join(folder_path, filename))
            return image_files
        except Exception as e:
            raise Exception(f"无法读取文件夹 {folder_path}: {str(e)}")
    
    def save_image(self, image: Image.Image, output_path: str, quality: int = 95):
        """
        保存图片到指定路径
        
        Args:
            image: PIL Image对象
            output_path: 输出路径
            quality: JPEG质量 (1-100)
        """
        try:
            if image.mode in ('RGBA', 'LA') and output_path.lower().endswith(('.jpg', '.jpeg')):
                # 如果是带透明通道的图片但要保存为JPEG，需要转换
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
            else:
                image.save(output_path, image.format if image.format else 'PNG')
        except Exception as e:
            raise Exception(f"无法保存图片到 {output_path}: {str(e)}")
    
    def get_supported_files(self, file_paths: List[str]) -> List[str]:
        """
        从文件列表中筛选出支持的图片格式
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            支持的图片文件路径列表
        """
        return [path for path in file_paths if os.path.splitext(path)[1].lower() in self.SUPPORTED_FORMATS]