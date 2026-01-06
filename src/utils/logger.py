"""
Módulo responsável pela configuração e gerenciamento de logs.
"""
import logging
import colorlog
from datetime import datetime
from pathlib import Path


class TestLogger:
    """Gerenciador de logs com suporte a cores e arquivo."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura o logger com handlers de console e arquivo."""
        logger = logging.getLogger("TestAutomation")
        logger.setLevel(logging.DEBUG)
        
        # Evitar duplicação de handlers
        if logger.handlers:
            return logger
        
        # Handler de console com cores
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_format)
        
        # Handler de arquivo
        log_file = self.log_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(levelname)-8s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str):
        """Log de informação."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log de debug."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log de aviso."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log de erro."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log crítico."""
        self.logger.critical(message)
