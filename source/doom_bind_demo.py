from doom_key_bind import DoomInputBridge


bridge = DoomInputBridge()

print("Status da bridge:", bridge.connected)
if bridge.last_error:
    print(bridge.last_error)

# Exemplo de uso em Python para mover o personagem.
# Quando a library C estiver disponível, cada chamada vira um evento do DOOM.
# Sem a lib, a chamada cai no modo fallback e apenas registra a ação.

bridge.move("left", pressed=True)
bridge.move("left", pressed=False)

bridge.move("up", pressed=True)
bridge.move("up", pressed=False)

bridge.move("right", pressed=True)
bridge.move("right", pressed=False)

bridge.move("down", pressed=True)
bridge.move("down", pressed=False)

print("Movimentos enviados.")
