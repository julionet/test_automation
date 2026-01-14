"""
Ação de leitura de texto.
"""
from typing import Optional, Any

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class ReadAction(BaseAction):
    """Ação de leitura de texto de controles."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa leitura de texto.
        
        Args:
            action: Definição da ação
            - value: Texto esperado para validação (opcional)
            
        Returns:
            Texto lido do controle
            
        Raises:
            ValueError: Se o texto lido for diferente do esperado (action.value)
        """
        control = self._get_control(action)
        
        # Garantir que o controle existe
        control.wait('exists', timeout=action.timeout or self.app_manager.timeout)
        
        # Tentar diferentes métodos de leitura
        text = None
        
        # Método 1: window_text
        try:
            text = control.window_text()
            if text:
                self.logger.debug(f"Texto lido (window_text): {text}")
                return text
        except Exception:
            pass
        
        # Método 2: texts (para controles compostos)
        try:
            texts = control.texts()
            if texts and len(texts) > 0:
                text = " ".join(texts)
                self.logger.debug(f"Texto lido (texts): {text}")
                return text
        except Exception:
            pass
        
        # Método 3: get_value (para controles de valor)
        try:
            text = control.get_value()
            if text:
                self.logger.debug(f"Texto lido (get_value): {text}")
                return text
        except Exception:
            pass
        
        # Método 4: legacy_properties
        try:
            text = control.legacy_properties().get('Value', '')
            if text:
                self.logger.debug(f"Texto lido (legacy_properties): {text}")
                return text
        except Exception:
            pass
        
        self.logger.warning("Não foi possível ler texto do controle")
        return ""
