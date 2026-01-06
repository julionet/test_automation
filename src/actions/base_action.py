"""
Classe base para ações de teste.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime
import time

from src.models.test_script import Action
from src.models.test_result import ActionResult, TestStatus
from src.core.app_manager import AppManager
from src.core.screenshot_manager import ScreenshotManager
from src.utils.logger import TestLogger


class BaseAction(ABC):
    """Classe base para todas as ações de teste."""
    
    def __init__(self, app_manager: AppManager, screenshot_manager: ScreenshotManager, 
                 logger: TestLogger):
        """
        Inicializa a ação.
        
        Args:
            app_manager: Gerenciador da aplicação
            screenshot_manager: Gerenciador de screenshots
            logger: Logger
        """
        self.app_manager = app_manager
        self.screenshot_manager = screenshot_manager
        self.logger = logger
    
    def execute(self, action: Action) -> ActionResult:
        """
        Executa a ação.
        
        Args:
            action: Definição da ação
            
        Returns:
            Resultado da execução
        """
        start_time = datetime.now()
        status = TestStatus.RUNNING
        error_message = None
        screenshot_path = None
        read_value = None
        
        self.logger.info(f"Executando ação: {action.description}")
        
        try:
            # Executar a ação específica
            read_value = self._execute_action(action)
            status = TestStatus.PASSED
            self.logger.info(f"✓ Ação concluída com sucesso")
            
            # Screenshot de sucesso se configurado
            if action.screenshot_on_success:
                screenshot_path = self.screenshot_manager.capture_full_screen(
                    prefix=f"success_{action.action_type}"
                )
                
        except Exception as e:
            status = TestStatus.FAILED
            error_message = str(e)
            self.logger.error(f"✗ Ação falhou: {error_message}")
            
            # Screenshot de falha se configurado
            if action.screenshot_on_failure:
                try:
                    screenshot_path = self.screenshot_manager.capture_full_screen(
                        prefix=f"failure_{action.action_type}"
                    )
                except Exception as screenshot_error:
                    self.logger.warning(f"Falha ao capturar screenshot: {screenshot_error}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ActionResult(
            action_type=action.action_type,
            description=action.description,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            error_message=error_message,
            screenshot_path=screenshot_path,
            read_value=read_value
        )
    
    @abstractmethod
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Implementação específica da ação.
        Deve ser sobrescrito nas classes filhas.
        
        Args:
            action: Definição da ação
            
        Returns:
            Valor lido (se aplicável)
        """
        pass
    
    def _get_control(self, action: Action):
        """
        Obtém o controle especificado na ação.
        
        Args:
            action: Definição da ação
            
        Returns:
            Controle do pywinauto
        """
        timeout = action.timeout or self.app_manager.timeout
        
        # Obter janela
        if action.window_title:
            window = self.app_manager.get_window(title=action.window_title)
        else:
            window = self.app_manager.get_window()
        
        # Obter controle
        if action.control:
            # Tentar por auto_id primeiro
            try:
                control = window.child_window(auto_id=action.control, timeout=timeout)
                if control.exists():
                    return control
            except Exception:
                pass
            
            # Tentar por title
            try:
                control = window.child_window(title=action.control, timeout=timeout)
                if control.exists():
                    return control
            except Exception:
                pass
            
            # Tentar por class_name
            try:
                control = window.child_window(class_name=action.control, timeout=timeout)
                if control.exists():
                    return control
            except Exception:
                pass
            
            raise Exception(f"Controle não encontrado: {action.control}")
        
        return window
