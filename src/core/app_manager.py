"""
Gerenciador de aplicações Windows.
"""
import time
import subprocess
from typing import Optional
from pathlib import Path
from pywinauto import Application as PyWinAutoApp
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.timings import TimeoutError


class AppManager:
    """Gerencia o ciclo de vida de aplicações Windows."""
    
    def __init__(self, app_path: str, arguments: str = "", backend: str = "uia", 
                 startup_delay: int = 3, timeout: int = 10):
        """
        Inicializa o gerenciador.
        
        Args:
            app_path: Caminho do executável
            arguments: Argumentos de linha de comando
            backend: Backend do pywinauto ('win32' ou 'uia')
            startup_delay: Tempo de espera após iniciar
            timeout: Timeout padrão para operações
        """
        self.app_path = Path(app_path)
        self.arguments = arguments
        self.backend = backend
        self.startup_delay = startup_delay
        self.timeout = timeout
        self.app: Optional[PyWinAutoApp] = None
        self.process: Optional[subprocess.Popen] = None
        
        if not self.app_path.exists():
            raise FileNotFoundError(f"Aplicação não encontrada: {app_path}")
    
    def start(self) -> bool:
        """
        Inicia a aplicação.
        
        Returns:
            True se iniciou com sucesso
            
        Raises:
            Exception: Se não conseguir iniciar
        """
        try:
            # Construir comando
            cmd = [str(self.app_path)]
            if self.arguments:
                cmd.extend(self.arguments.split())
            
            # Iniciar processo
            self.process = subprocess.Popen(cmd)
            
            # Aguardar startup
            time.sleep(self.startup_delay)
            
            # Conectar com pywinauto
            self.app = PyWinAutoApp(backend=self.backend).connect(
                process=self.process.pid,
                timeout=self.timeout
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Falha ao iniciar aplicação: {str(e)}")
    
    def connect(self, **kwargs) -> PyWinAutoApp:
        """
        Conecta a uma aplicação já em execução.
        
        Args:
            **kwargs: Parâmetros de conexão (title, path, process, etc.)
            
        Returns:
            Objeto Application do pywinauto
        """
        try:
            self.app = PyWinAutoApp(backend=self.backend).connect(
                timeout=self.timeout,
                **kwargs
            )
            return self.app
        except Exception as e:
            raise Exception(f"Falha ao conectar à aplicação: {str(e)}")
    
    def get_window(self, title: Optional[str] = None, **kwargs):
        """
        Obtém uma janela da aplicação.
        
        Args:
            title: Título da janela
            **kwargs: Outros critérios de busca
            
        Returns:
            Objeto window do pywinauto
        """
        if not self.app:
            raise RuntimeError("Aplicação não iniciada ou conectada")
        
        try:
            if title:
                return self.app.window(title=title, **kwargs)
            else:
                return self.app.top_window(**kwargs)
        except ElementNotFoundError as e:
            raise Exception(f"Janela não encontrada: {str(e)}")
    
    def wait_window(self, title: str, timeout: Optional[int] = None) -> bool:
        """
        Aguarda uma janela aparecer.
        
        Args:
            title: Título da janela
            timeout: Timeout em segundos
            
        Returns:
            True se a janela apareceu
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                window = self.get_window(title=title)
                if window.exists():
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        
        return False
    
    def close(self, force: bool = False):
        """
        Fecha a aplicação.
        
        Args:
            force: Se True, força o fechamento
        """
        try:
            if self.app:
                if force:
                    self.app.kill()
                else:
                    # Tentar fechar graciosamente
                    try:
                        top_window = self.app.top_window()
                        top_window.close()
                        time.sleep(1)
                    except Exception:
                        pass
                    
                    # Se ainda estiver rodando, força
                    if self.process and self.process.poll() is None:
                        self.app.kill()
            
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
                
        except Exception as e:
            # Se tudo falhar, tenta matar o processo diretamente
            if self.process:
                try:
                    self.process.kill()
                except Exception:
                    pass
        finally:
            self.app = None
            self.process = None
    
    def is_running(self) -> bool:
        """
        Verifica se a aplicação está rodando.
        
        Returns:
            True se está rodando
        """
        if self.process:
            return self.process.poll() is None
        return False
