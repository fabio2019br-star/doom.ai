import ctypes

lib = ctypes.CDLL('./minha_lib.so')

lib.soma.argtypes = [ctypes.c_int, ctypes.c_int]
lib.soma.restype = ctypes.c_int

lib.saudacao.argtypes = [ctypes.c_char_p]
lib.saudacao.restype = None

print(f"10 + 32 = {lib.soma(10, 32)}")
lib.saudacao(b"Neo")