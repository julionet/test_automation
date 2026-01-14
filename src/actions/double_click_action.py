"""
Ação de clique duplo.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class DoubleClickAction(BaseAction):
    """Ação de clique duplo em controles."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique duplo no controle.
        
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
        
        # Executar clique duplo
        self.logger.debug("Executando clique duplo no controle")
        
        try:
            # Método 1: Tentar com double_click()
            try:
                control.double_click()
                self.logger.debug("Clique duplo executado com double_click()")
            except Exception as e1:
                self.logger.debug(f"double_click() não suportado: {e1}")
                
                # Método 2: Usar click com double_click parameter
                try:
                    control.click(double_click=True)
                    self.logger.debug("Clique duplo executado com click(double_click=True)")
                except Exception as e2:
                    self.logger.debug(f"click(double_click=True) não suportado: {e2}")
                    
                    # Método 3: Dois cliques rápidos em sequência
                    try:
                        rect = control.rectangle()
                        x = rect.left + (rect.right - rect.left) // 2
                        y = rect.top + (rect.bottom - rect.top) // 2
                        
                        # Duplo clique usando coordenadas
                        control.parent.double_click(coords=(x, y))
                        self.logger.debug("Clique duplo executado com coordenadas")
                    except Exception as e3:
                        self.logger.warning(f"Tentativa 3 falhou: {e3}")
                        
                        # Método 4: Dois cliques simples rápidos
                        try:
                            control.click()
                            time.sleep(0.1)
                            control.click()
                            self.logger.debug("Clique duplo executado com dois clicks rápidos")
                        except Exception as e4:
                            raise Exception(
                                f"Não foi possível executar clique duplo. "
                                f"Tentativas: double_click()={e1}, "
                                f"click(double_click=True)={e2}, "
                                f"coordenadas={e3}, "
                                f"dois_cliques={e4}"
                            )
        
        except Exception as e:
            self.logger.error(f"Erro ao executar clique duplo: {e}")
            raise
        
        time.sleep(0.5)  # Pequena pausa após clique duplo
        
        return None
