"""
Ação de clique.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class ClickAction(BaseAction):
    """Ação de clique em controles."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique no controle.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        control = self._get_control(action)
        
        # Garantir que o controle está visível e habilitado
        control.wait('visible', timeout=action.timeout or self.app_manager.timeout)
        control.wait('enabled', timeout=action.timeout or self.app_manager.timeout)
        
        # Focar no controle
        try:
            control.set_focus()
            time.sleep(0.2)
        except Exception:
            pass
        
        # Executar clique
        control.click()
        time.sleep(0.5)  # Pequena pausa após clique
        
        return None
