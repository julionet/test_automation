"""
Factory para ações de teste.
"""
from typing import Dict, Type

from src.actions.base_action import BaseAction
from src.actions.click_action import ClickAction
from src.actions.click_label_action import ClickLabelAction
from src.actions.double_click_action import DoubleClickAction
from src.actions.type_action import TypeAction
from src.actions.read_action import ReadAction
from src.actions.wait_action import WaitAction
from src.actions.clear_action import ClearAction
from src.actions.dialog_action import (
    CloseDialogAction, 
    VerifyTextAction, 
    CloseWindowAction,
    ScreenshotAction
)
from src.actions.click_wait_action import (
    ClickAndWaitAction,
)
from src.core.app_manager import AppManager
from src.core.screenshot_manager import ScreenshotManager
from src.utils.logger import TestLogger


class ActionFactory:
    """Factory para criar ações de teste."""
    
    _action_map: Dict[str, Type[BaseAction]] = {
        "click": ClickAction,
        "click_label": ClickLabelAction,
        "double_click": DoubleClickAction,
        "type_text": TypeAction,
        "read_text": ReadAction,
        "wait": WaitAction,
        "clear": ClearAction,
        "close_dialog": CloseDialogAction,
        "verify_text": VerifyTextAction,
        "close_window": CloseWindowAction,
        "screenshot": ScreenshotAction,
        "click_and_wait": ClickAndWaitAction
    }
    
    @classmethod
    def create_action(cls, action_type: str, app_manager: AppManager,
                     screenshot_manager: ScreenshotManager, 
                     logger: TestLogger) -> BaseAction:
        """
        Cria uma ação baseada no tipo.
        
        Args:
            action_type: Tipo da ação
            app_manager: Gerenciador da aplicação
            screenshot_manager: Gerenciador de screenshots
            logger: Logger
            
        Returns:
            Instância da ação
            
        Raises:
            ValueError: Se o tipo de ação não for suportado
        """
        action_class = cls._action_map.get(action_type)
        
        if not action_class:
            raise ValueError(
                f"Tipo de ação não suportado: '{action_type}'. "
                f"Tipos válidos: {list(cls._action_map.keys())}"
            )
        
        return action_class(app_manager, screenshot_manager, logger)
    
    @classmethod
    def get_supported_actions(cls) -> list:
        """
        Retorna lista de ações suportadas.
        
        Returns:
            Lista de tipos de ação suportados
        """
        return list(cls._action_map.keys())
