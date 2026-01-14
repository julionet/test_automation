"""
Ação de limpeza de campo de texto.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class ClearAction(BaseAction):
    """Ação de limpeza de campo de texto."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa limpeza do campo.
        
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
        control.set_focus()
        time.sleep(0.2)
        
        # Tentar limpar via set_edit_text
        try:
            control.set_edit_text("")
        except Exception:
            # Se não funcionar, usar Select All + Delete
            try:
                control.type_keys("^a{DELETE}")
                time.sleep(0.1)
            except Exception:
                raise ValueError(f"Não foi possível limpar o campo: {control}")
        
        return None