"""
Classe base para ações de teste.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime

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
            # NOVO: Trazer aplicação para primeiro plano antes de executar
            self._bring_app_to_foreground(action)
            
            # Executar a ação específica
            read_value = self._execute_action(action)
            if read_value == action.value:
                status = TestStatus.PASSED
                self.logger.info(f"✓ Valor lido corresponde ao esperado: '{read_value}'")

                 # Screenshot de sucesso se configurado
                if action.screenshot_on_success:
                    # NOVO: Garantir que está em primeiro plano antes do screenshot
                    self._bring_app_to_foreground(action)
                    screenshot_path = self.screenshot_manager.capture_full_screen(
                        prefix=f"success_{action.action_type}"
                    )
            else:
                status = TestStatus.FAILED
                error_message = f"Valor lido não corresponde ao esperado: {action.value}, lido: {read_value}"
                self.logger.error(f"✗ Ação falhou: {error_message}")
                
                # Screenshot de falha se configurado
                if action.screenshot_on_failure:
                    try:
                        # NOVO: Garantir que está em primeiro plano antes do screenshot
                        self._bring_app_to_foreground(action)
                        screenshot_path = self.screenshot_manager.capture_full_screen(
                            prefix=f"failure_{action.action_type}"
                        )
                    except Exception as screenshot_error:
                        self.logger.warning(f"Falha ao capturar screenshot: {screenshot_error}")           
                
        except Exception as e:
            status = TestStatus.FAILED
            error_message = str(e)
            self.logger.error(f"✗ Ação falhou: {error_message}")
            
            # Screenshot de falha se configurado
            if action.screenshot_on_failure:
                try:
                    # NOVO: Garantir que está em primeiro plano antes do screenshot
                    self._bring_app_to_foreground(action)
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
                control = window.child_window(auto_id=action.control)
                if control.exists():
                    return control
            except Exception as e:
                pass
            
            # Tentar por title
            try:
                control = window.child_window(title=action.control)
                if control.exists():
                    return control
            except Exception:
                pass
            
            # Tentar por class_name
            try:
                control = window.child_window(class_name=action.control)
                if control.exists():
                    return control
            except Exception:
                pass
            
            raise Exception(f"Controle não encontrado: {action.control}")
        
        return window

    def _bring_app_to_foreground(self, action: Action):
        """
        Traz a aplicação para primeiro plano antes da ação.
        
        Args:
            action: Definição da ação
        """
        try:
            # Se tiver window_title específico, trazer aquela janela
            if action.window_title:
                window = self.app_manager.get_window(title=action.window_title)
                self.app_manager.bring_to_foreground(window)
            else:
                # Caso contrário, trazer janela principal
                self.app_manager.bring_to_foreground()
            
            self.logger.debug("Aplicação trazida para primeiro plano")
        except Exception as e:
            self.logger.warning(f"Não foi possível trazer aplicação para primeiro plano: {e}")
