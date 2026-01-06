"""
Ação de espera.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class WaitAction(BaseAction):
    """Ação de espera/pausa."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa espera.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        duration = action.duration or 1
        
        if duration < 0:
            raise ValueError("Duração da espera deve ser maior ou igual a zero")
        
        self.logger.info(f"Aguardando {duration} segundo(s)...")
        time.sleep(duration)
        
        return None
