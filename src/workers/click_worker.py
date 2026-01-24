"""
Classe que carrega uma nova tela de forma assíncrona.
"""
import sys
import time
from pywinauto import Application

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

titulo_janela = sys.argv[1]
nome_botao = sys.argv[2]

app = Application(backend="uia").connect(title_re=titulo_janela)
window = app.window(title_re=titulo_janela)

# Tentar trazer para foco usando pywinauto
window.set_focus()
time.sleep(0.2)

# Tentar usar win32 para garantir que fica no topo
if HAS_WIN32:
    try:
        hwnd = window.handle
        # Mostrar e ativar a janela
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        time.sleep(0.2)
    except Exception:
        pass

control = window.child_window(auto_id=nome_botao, control_type="Button")
if not control.exists():
    control = window.child_window(title=nome_botao, control_type="Button")
    if not control.exists():
        control = window.child_window(class_name=nome_botao, control_type="Button")

if control.exists():
    try:
        control.set_focus()
        time.sleep(0.2)
    except Exception:
        pass

    control.click()
    time.sleep(0.5) 
