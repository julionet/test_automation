"""
Gerenciador de screenshots.
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from PIL import ImageGrab
import pywinauto


class ScreenshotManager:
    """Gerencia captura e salvamento de screenshots."""
    
    def __init__(self, screenshot_dir: str = "screenshots"):
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(exist_ok=True)
        self.current_test_dir: Optional[Path] = None
    
    def prepare_test_directory(self, suite_name: str, test_id: str):
        """
        Prepara diretório para screenshots de um teste específico.
        
        Args:
            suite_name: Nome da suíte
            test_id: ID do teste
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dir_name = f"{suite_name}_{test_id}_{timestamp}"
        self.current_test_dir = self.screenshot_dir / dir_name
        self.current_test_dir.mkdir(exist_ok=True)
    
    def capture_full_screen(self, prefix: str = "screenshot") -> str:
        """
        Captura screenshot da tela inteira.
        
        Args:
            prefix: Prefixo do nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        if not self.current_test_dir:
            raise RuntimeError("Diretório de teste não preparado")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{prefix}_{timestamp}.png"
        filepath = self.current_test_dir / filename
        
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        
        return str(filepath)
    
    def capture_window(self, window, prefix: str = "window") -> str:
        """
        Captura screenshot de uma janela específica.
        
        Args:
            window: Janela do pywinauto
            prefix: Prefixo do nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        if not self.current_test_dir:
            raise RuntimeError("Diretório de teste não preparado")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{prefix}_{timestamp}.png"
        filepath = self.current_test_dir / filename
        
        try:
            window.capture_as_image().save(filepath)
        except Exception:
            # Fallback para captura de tela inteira
            return self.capture_full_screen(prefix)
        
        return str(filepath)
    
    def capture_control(self, control, prefix: str = "control") -> str:
        """
        Captura screenshot de um controle específico.
        
        Args:
            control: Controle do pywinauto
            prefix: Prefixo do nome do arquivo
            
        Returns:
            Caminho do arquivo salvo
        """
        if not self.current_test_dir:
            raise RuntimeError("Diretório de teste não preparado")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"{prefix}_{timestamp}.png"
        filepath = self.current_test_dir / filename
        
        try:
            control.capture_as_image().save(filepath)
        except Exception:
            # Fallback para captura de tela inteira
            return self.capture_full_screen(prefix)
        
        return str(filepath)
