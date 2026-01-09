"""
Classe que carrega uma nova tela de forma assíncrona.
"""
import sys
import time
from pywinauto import Application

print ("Iniciando clique assíncrono...")

titulo_janela = sys.argv[1]
nome_botao = sys.argv[2]

app = Application(backend="uia").connect(title_re=titulo_janela)
window = app.window(title_re=titulo_janela)

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
