"""
Ação de clique em label ou texto.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class ClickLabelAction(BaseAction):
    """Ação de clique em elementos de texto/label."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique em um texto ou label.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        if not action.value:
            raise ValueError("Ação 'click_label' requer o campo 'value' com o texto a clicar")
        
        # Obter janela
        if action.window_title:
            window = self.app_manager.get_window(title=action.window_title)
        else:
            window = self.app_manager.get_window()
        
        # Tentar clicar no texto/label
        success = self._click_on_text_or_label(window, action.value)
        
        if not success:
            raise Exception(f"Não foi possível clicar no texto/label: {action.value}")
        
        return None
    
    def _click_on_text_or_label(self, window, text_or_label: str) -> bool:
        """
        Clica em um elemento de texto ou label buscando por seu conteúdo.
        Útil para elementos que não são normalmente clicáveis.
        
        Args:
            window: Objeto da janela pywinauto
            text_or_label: Texto a buscar
            
        Returns:
            True se conseguiu clicar, False caso contrário
        """
        try:
            # Buscar por titulo exato
            control = window.child_window(title=text_or_label)
            if control.exists():
                rect = control.rectangle()
                x = (rect.left + rect.right) // 2
                y = (rect.top + rect.bottom) // 2
                control.click(coords=(x - rect.left, y - rect.top))
                self.logger.info(f"Clicou no texto/label: {text_or_label}")
                time.sleep(0.5)
                return True
        except Exception:
            pass
        
        try:
            # Buscar por titulo parcial (contém)
            for control in window.descendants():
                if text_or_label.lower() in (control.title or "").lower():
                    rect = control.rectangle()
                    x = (rect.left + rect.right) // 2
                    y = (rect.top + rect.bottom) // 2
                    control.click(coords=(x - rect.left, y - rect.top))
                    self.logger.info(f"Clicou no texto/label contendo: {text_or_label}")
                    time.sleep(0.5)
                    return True
        except Exception:
            pass
        
        self.logger.warning(f"Não foi possível clicar no texto/label: {text_or_label}")
        return False
