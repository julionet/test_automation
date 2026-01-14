"""
Ações relacionadas a diálogos.
"""
from typing import Optional, Any
import time

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class CloseDialogAction(BaseAction):
    """Ação para fechar diálogos."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Fecha um diálogo.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        # Se window_title especificado, usar aquela janela
        if action.window_title:
            self.app_manager.wait_window(
                action.window_title, 
                timeout=action.timeout or self.app_manager.timeout
            )
            window = self.app_manager.get_window(title=action.window_title)
        else:
            # Caso contrário, usar janela atual
            window = self.app_manager.get_window()
        
        # Tentar fechar de várias formas
        try:
            # Método 1: Botão close
            window.close()
        except Exception:
            try:
                # Método 2: Alt+F4
                window.type_keys("%{F4}")
            except Exception:
                try:
                    # Método 3: Esc
                    window.type_keys("{ESC}")
                except Exception:
                    raise Exception("Não foi possível fechar o diálogo")
        
        time.sleep(0.5)
        return None


class VerifyTextAction(BaseAction):
    """Ação para verificar texto."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Verifica se um texto existe no controle.
        
        Args:
            action: Definição da ação
            
        Returns:
            True se o texto foi encontrado
        """
        if not action.value:
            raise ValueError("Ação 'verify_text' requer o atributo 'value'")
        
        control = self._get_control(action)
        
        # Ler o texto do controle
        actual_text = ""
        try:
            actual_text = control.window_text()
        except Exception:
            try:
                texts = control.texts()
                actual_text = " ".join(texts) if texts else ""
            except Exception:
                pass
        
        expected_text = action.value
        
        if expected_text in actual_text:
            self.logger.info(f"✓ Texto verificado: '{expected_text}' encontrado em '{actual_text}'")
            return True
        else:
            raise AssertionError(
                f"Texto esperado '{expected_text}' não encontrado. "
                f"Texto atual: '{actual_text}'"
            )


class CloseWindowAction(BaseAction):
    """Ação para fechar uma janela específica."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Fecha uma janela.
        
        Args:
            action: Definição da ação
            
        Returns:
            None
        """
        # Se window_title especificado, usar aquela janela
        if action.window_title:
            self.app_manager.wait_window(
                action.window_title, 
                timeout=action.timeout or self.app_manager.timeout
            )
            window = self.app_manager.get_window(title=action.window_title)
        else:
            # Caso contrário, usar janela atual (top_window)
            window = self.app_manager.app.top_window()
        
        # Tentar fechar de várias formas
        try:
            # Método 1: Botão close (mais confiável)
            window.close()
            self.logger.info(f"Janela '{window.window_text()}' fechada com sucesso")
        except Exception as e1:
            self.logger.warning(f"Método 1 (close) falhou: {e1}")
            try:
                # Método 2: Alt+F4 (atalho de teclado)
                window.type_keys("%{F4}")
                self.logger.info(f"Janela fechada com Alt+F4")
            except Exception as e2:
                self.logger.warning(f"Método 2 (Alt+F4) falhou: {e2}")
                try:
                    # Método 3: Esc
                    window.type_keys("{ESC}")
                    self.logger.info(f"Janela fechada com ESC")
                except Exception as e3:
                    self.logger.warning(f"Método 3 (ESC) falhou: {e3}")
                    raise Exception(
                        f"Não foi possível fechar a janela. "
                        f"close(): {e1}, Alt+F4: {e2}, ESC: {e3}"
                    )
        
        time.sleep(0.5)
        return None


class ScreenshotAction(BaseAction):
    """Ação para capturar screenshot."""
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Captura screenshot.
        
        Args:
            action: Definição da ação
            
        Returns:
            Caminho do screenshot
        """
        # NOVO: Garantir que está em primeiro plano antes do screenshot
        try:
            if action.window_title:
                window = self.app_manager.get_window(title=action.window_title)
                self.app_manager.bring_to_foreground(window)
            else:
                self.app_manager.bring_to_foreground()
        except Exception as e:
            self.logger.warning(f"Aviso ao trazer janela para frente: {e}")
        
        screenshot_path = self.screenshot_manager.capture_full_screen(
            prefix="manual_screenshot"
        )
        
        self.logger.info(f"Screenshot capturado: {screenshot_path}")
        return screenshot_path
