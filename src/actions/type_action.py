"""
Ação de digitação de texto.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class TypeAction(BaseAction):
    """Ação de digitação de texto."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa digitação de texto.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        if not action.value:
            raise ValueError("Ação 'type_text' requer o atributo 'value'")
        
        control = self._get_control(action)
        
        # Garantir que o controle está visível e habilitado
        control.wait('visible', timeout=action.timeout or self.app_manager.timeout)
        control.wait('enabled', timeout=action.timeout or self.app_manager.timeout)
        
        # Focar no controle
        control.set_focus()
        time.sleep(0.2)
        
        # Limpar conteúdo existente
        try:
            control.set_edit_text("")
        except Exception:
            # Se não for um controle de edição, tentar select_all + delete
            try:
                control.type_keys("^a{DELETE}")
                time.sleep(0.1)
            except Exception:
                pass
        
        # Digitar o texto
        control.type_keys(action.value, with_spaces=True)
        time.sleep(0.3)
        
        return None
