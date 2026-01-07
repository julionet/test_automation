"""
Ação de clique que carrega nova tela de forma assíncrona.
"""
from typing import Optional, Any
import time
import threading

from src.actions.base_action import BaseAction
from src.models.test_script import Action


class ClickAsyncAction(BaseAction):
    """
    Ação de clique que carrega uma nova tela sem bloquear a execução.
    Ideal para casos onde o clique abre um novo formulário/janela.
    """
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique no controle e aguarda nova janela de forma não-bloqueante.
        
        Args:
            action: Definição da ação
            
        Returns:
            Título da nova janela carregada (se encontrada)
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
        
        # Capturar informações da janela atual antes do clique
        current_windows = self._get_current_windows()
        self.logger.debug(f"Janelas antes do clique: {len(current_windows)}")
        
        # Executar clique
        self.logger.info("Executando clique...")
        control.click()
        
        # Aguardar um pouco para a nova janela começar a carregar
        time.sleep(0.3)
        
        # Detectar e aguardar nova janela (se especificada)
        new_window_title = None
        if action.value:
            # value contém o título esperado da nova janela
            expected_title = action.value
            self.logger.info(f"Aguardando nova janela: '{expected_title}'")
            
            timeout = action.timeout or self.app_manager.timeout
            if self._wait_for_new_window(expected_title, timeout):
                new_window_title = expected_title
                self.logger.info(f"✓ Nova janela '{expected_title}' carregada")
                
                # Trazer nova janela para frente
                try:
                    new_window = self.app_manager.get_window(title=expected_title)
                    self.app_manager.bring_to_foreground(new_window)
                except Exception as e:
                    self.logger.warning(f"Não foi possível trazer nova janela para frente: {e}")
            else:
                self.logger.warning(f"Nova janela '{expected_title}' não foi detectada no timeout")
        else:
            # Detectar qualquer nova janela
            self.logger.info("Detectando novas janelas...")
            time.sleep(0.5)
            
            new_windows = self._detect_new_windows(current_windows)
            if new_windows:
                new_window_title = new_windows[0]
                self.logger.info(f"✓ Nova janela detectada: '{new_window_title}'")
                
                # Trazer nova janela para frente
                try:
                    new_window = self.app_manager.get_window(title=new_window_title)
                    self.app_manager.bring_to_foreground(new_window)
                except Exception as e:
                    self.logger.warning(f"Não foi possível trazer nova janela para frente: {e}")
            else:
                self.logger.debug("Nenhuma nova janela detectada")
        
        # Pequena pausa para estabilizar
        time.sleep(0.5)
        
        return new_window_title
    
    def _get_current_windows(self) -> list:
        """
        Obtém lista de títulos das janelas atuais da aplicação.
        
        Returns:
            Lista de títulos de janelas
        """
        windows = []
        try:
            if self.app_manager.app:
                for window in self.app_manager.app.windows():
                    try:
                        title = window.window_text()
                        if title:
                            windows.append(title)
                    except Exception:
                        pass
        except Exception:
            pass
        return windows
    
    def _detect_new_windows(self, previous_windows: list) -> list:
        """
        Detecta novas janelas comparando com a lista anterior.
        
        Args:
            previous_windows: Lista de janelas anteriores
            
        Returns:
            Lista de títulos de novas janelas
        """
        current_windows = self._get_current_windows()
        new_windows = [w for w in current_windows if w not in previous_windows]
        return new_windows
    
    def _wait_for_new_window(self, expected_title: str, timeout: int) -> bool:
        """
        Aguarda uma nova janela com título específico aparecer.
        
        Args:
            expected_title: Título esperado da janela
            timeout: Timeout em segundos
            
        Returns:
            True se a janela foi encontrada
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Tentar encontrar a janela
                window = self.app_manager.get_window(title=expected_title)
                if window.exists() and window.is_visible():
                    # Aguardar a janela estar pronta
                    time.sleep(0.3)
                    return True
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return False


class ClickAndWaitAction(BaseAction):
    """
    Ação de clique que aguarda explicitamente uma nova janela carregar.
    Mais robusto que ClickAsyncAction quando se sabe exatamente qual janela esperar.
    """
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique e aguarda janela específica estar pronta.
        
        Args:
            action: Definição da ação
            - control: Controle a ser clicado
            - value: Título da janela a aguardar (OBRIGATÓRIO)
            - duration: Tempo adicional de espera após janela aparecer (opcional)
            
        Returns:
            Título da janela carregada
        """
        if not action.value:
            raise ValueError(
                "Action 'click_and_wait' requer 'value' com o título da janela esperada"
            )
        
        expected_window_title = action.value
        additional_wait = action.duration or 0
        timeout = action.timeout or self.app_manager.timeout
        
        # Obter controle e executar clique
        control = self._get_control(action)
        
        control.wait('visible', timeout=timeout)
        control.wait('enabled', timeout=timeout)
        
        try:
            control.set_focus()
            time.sleep(0.2)
        except Exception:
            pass
        
        self.logger.info(f"Clicando e aguardando janela '{expected_window_title}'...")
        control.click()
        
        # Aguardar nova janela aparecer
        if not self.app_manager.wait_window(expected_window_title, timeout=timeout):
            raise Exception(
                f"Janela '{expected_window_title}' não foi carregada dentro de {timeout}s"
            )
        
        self.logger.info(f"✓ Janela '{expected_window_title}' carregada")
        
        # Aguardar tempo adicional se especificado (para a janela terminar de carregar)
        if additional_wait > 0:
            self.logger.info(f"Aguardando {additional_wait}s adicionais para janela estabilizar...")
            time.sleep(additional_wait)
        
        # Trazer janela para frente
        try:
            new_window = self.app_manager.get_window(title=expected_window_title)
            self.app_manager.bring_to_foreground(new_window)
            
            # Aguardar janela estar realmente pronta
            new_window.wait('ready', timeout=5)
        except Exception as e:
            self.logger.warning(f"Aviso ao preparar nova janela: {e}")
        
        return expected_window_title


class ClickModalAction(BaseAction):
    """
    Ação de clique que abre uma janela modal/diálogo.
    Específico para janelas modais que bloqueiam a aplicação principal.
    """
    
    def _execute_action(self, action: Action) -> Optional[Any]:
        """
        Executa clique que abre janela modal.
        
        Args:
            action: Definição da ação
            - control: Controle a ser clicado
            - value: Título da janela modal (opcional)
            - duration: Tempo de espera para modal carregar (opcional)
            
        Returns:
            Título da janela modal
        """
        control = self._get_control(action)
        timeout = action.timeout or self.app_manager.timeout
        
        control.wait('visible', timeout=timeout)
        control.wait('enabled', timeout=timeout)
        
        try:
            control.set_focus()
            time.sleep(0.2)
        except Exception:
            pass
        
        self.logger.info("Clicando para abrir janela modal...")
        
        # Executar clique em thread separada para não bloquear
        def click_in_thread():
            try:
                control.click()
            except Exception as e:
                self.logger.warning(f"Erro ao executar clique: {e}")
        
        click_thread = threading.Thread(target=click_in_thread, daemon=True)
        click_thread.start()
        
        # Não aguardar a thread terminar - continuar execução
        # Aguardar apenas um tempo mínimo para modal começar a carregar
        wait_time = action.duration or 0.5
        time.sleep(wait_time)
        
        # Se título da modal foi especificado, aguardar ela de forma assíncrona
        modal_title = None
        if action.value:
            expected_modal = action.value
            self.logger.info(f"Aguardando modal '{expected_modal}'...")
            
            def wait_for_modal_in_thread():
                try:
                    if self.app_manager.wait_window(expected_modal, timeout=timeout):
                        nonlocal modal_title
                        modal_title = expected_modal
                        self.logger.info(f"✓ Modal '{expected_modal}' carregada")
                        
                        # Trazer modal para frente
                        try:
                            modal_window = self.app_manager.get_window(title=expected_modal)
                            self.app_manager.bring_to_foreground(modal_window)
                            
                            # Aguardar modal estar pronta
                            modal_window.wait('ready', timeout=3)
                        except Exception as e:
                            self.logger.warning(f"Aviso ao preparar modal: {e}")
                    else:
                        self.logger.warning(f"Modal '{expected_modal}' não foi detectada")
                except Exception as e:
                    self.logger.warning(f"Erro ao aguardar modal: {e}")
            
            # Executar espera em thread separada
            wait_thread = threading.Thread(target=wait_for_modal_in_thread, daemon=True)
            wait_thread.start()
        else:
            # Tentar detectar qualquer diálogo/modal em thread separada
            def detect_modal_in_thread():
                try:
                    # Modais geralmente são a top_window após o clique
                    time.sleep(0.5)
                    modal_window = self.app_manager.app.top_window()
                    nonlocal modal_title
                    modal_title = modal_window.window_text()
                    self.logger.info(f"✓ Modal detectada: '{modal_title}'")
                    
                    self.app_manager.bring_to_foreground(modal_window)
                except Exception as e:
                    self.logger.warning(f"Não foi possível detectar modal: {e}")
            
            detect_thread = threading.Thread(target=detect_modal_in_thread, daemon=True)
            detect_thread.start()
        
        return modal_title
