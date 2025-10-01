import json
import os
from typing import Dict, Any

class ConfigManager:
    """
    配置管理类，负责保存和加载水印配置
    """
    
    def __init__(self, config_file: str = "watermark_config.json"):
        self.config_file = config_file
        self.default_config = {
            "text_watermark": {
                "text": "水印文本",
                "font_family": "arial.ttf",
                "font_size": 36,
                "color": [255, 255, 255],
                "opacity": 128,
                "position": [50, 50],
                "rotation": 0,
                "bold": False,
                "italic": False,
                "shadow": False,
                "shadow_color": [0, 0, 0],
                "shadow_offset": [2, 2],
                "stroke": False,
                "stroke_color": [0, 0, 0],
                "stroke_width": 1
            },
            "image_watermark": {
                "position": [0, 0],
                "opacity": 128,
                "scale": 1.0,
                "rotation": 0
            },
            "last_used": {
                "watermark_type": "text"
            }
        }
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Returns:
            配置字典，如果文件不存在则返回默认配置
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return self.default_config.copy()
    
    def save_text_watermark_template(self, name: str, settings: Dict[str, Any]) -> bool:
        """
        保存文本水印模板
        
        Args:
            name: 模板名称
            settings: 水印设置
            
        Returns:
            是否保存成功
        """
        try:
            config = self.load_config()
            if "templates" not in config:
                config["templates"] = {}
            if "text" not in config["templates"]:
                config["templates"]["text"] = {}
            
            config["templates"]["text"][name] = settings
            return self.save_config(config)
        except Exception as e:
            print(f"保存文本水印模板失败: {str(e)}")
            return False
    
    def save_image_watermark_template(self, name: str, settings: Dict[str, Any]) -> bool:
        """
        保存图片水印模板
        
        Args:
            name: 模板名称
            settings: 水印设置
            
        Returns:
            是否保存成功
        """
        try:
            config = self.load_config()
            if "templates" not in config:
                config["templates"] = {}
            if "image" not in config["templates"]:
                config["templates"]["image"] = {}
            
            config["templates"]["image"][name] = settings
            return self.save_config(config)
        except Exception as e:
            print(f"保存图片水印模板失败: {str(e)}")
            return False
    
    def load_text_watermark_template(self, name: str) -> Dict[str, Any]:
        """
        加载文本水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            模板设置，如果不存在则返回空字典
        """
        try:
            config = self.load_config()
            if "templates" in config and "text" in config["templates"] and name in config["templates"]["text"]:
                return config["templates"]["text"][name]
            return {}
        except Exception as e:
            print(f"加载文本水印模板失败: {str(e)}")
            return {}
    
    def load_image_watermark_template(self, name: str) -> Dict[str, Any]:
        """
        加载图片水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            模板设置，如果不存在则返回空字典
        """
        try:
            config = self.load_config()
            if "templates" in config and "image" in config["templates"] and name in config["templates"]["image"]:
                return config["templates"]["image"][name]
            return {}
        except Exception as e:
            print(f"加载图片水印模板失败: {str(e)}")
            return {}
    
    def get_text_templates(self) -> Dict[str, Any]:
        """
        获取所有文本水印模板
        
        Returns:
            文本水印模板字典
        """
        try:
            config = self.load_config()
            if "templates" in config and "text" in config["templates"]:
                return config["templates"]["text"]
            return {}
        except Exception as e:
            print(f"获取文本水印模板列表失败: {str(e)}")
            return {}
    
    def get_image_templates(self) -> Dict[str, Any]:
        """
        获取所有图片水印模板
        
        Returns:
            图片水印模板字典
        """
        try:
            config = self.load_config()
            if "templates" in config and "image" in config["templates"]:
                return config["templates"]["image"]
            return {}
        except Exception as e:
            print(f"获取图片水印模板列表失败: {str(e)}")
            return {}
    
    def delete_text_template(self, name: str) -> bool:
        """
        删除文本水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            config = self.load_config()
            if "templates" in config and "text" in config["templates"] and name in config["templates"]["text"]:
                del config["templates"]["text"][name]
                return self.save_config(config)
            return False
        except Exception as e:
            print(f"删除文本水印模板失败: {str(e)}")
            return False
    
    def delete_image_template(self, name: str) -> bool:
        """
        删除图片水印模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            config = self.load_config()
            if "templates" in config and "image" in config["templates"] and name in config["templates"]["image"]:
                del config["templates"]["image"][name]
                return self.save_config(config)
            return False
        except Exception as e:
            print(f"删除图片水印模板失败: {str(e)}")
            return False