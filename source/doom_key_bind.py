from __future__ import annotations

import ctypes
import os
from enum import IntEnum
from typing import Optional

# DOOM key codes from source/doomdef.h.
# They are the canonical arrow keys used by the engine.
KEY_LEFTARROW = 0xAC
KEY_RIGHTARROW = 0xAE
KEY_UPARROW = 0xAD
KEY_DOWNARROW = 0xAF


class DoomEventType(IntEnum):
    EV_KEYDOWN = 0
    EV_KEYUP = 1
    EV_MOUSE = 2
    EV_JOYSTICK = 3
    EV_BUTTONDOWN = 4
    EV_BUTTONUP = 5


class DoomEvent(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("data1", ctypes.c_int),
        ("data2", ctypes.c_int),
        ("data3", ctypes.c_int),
        ("data4", ctypes.c_int),
    ]


class DoomInputBridge:
    """
    Python binding layer for DOOM input using the engine's native event queue.

    This file intentionally does not modify the project source code. Instead,
    it expects the game to expose a C symbol like D_PostEvent(). If the project
    is compiled as a shared library (.so), this bridge can call it directly via
    ctypes. If not, the class falls back to a safe "print-only" mode so the
    script remains importable and easy to test.
    """

    _DEFAULT_CANDIDATES = (
        "./build/libclowndoom.so",
        "./build/clowndoom.so",
        "./libclowndoom.so",
        "./clowndoom.so",
        "/usr/local/lib/libclowndoom.so",
    )

    def __init__(self, library_path: Optional[str] = None) -> None:
        self.lib = None
        self.connected = False
        self.last_error: Optional[str] = None
        self._connect(library_path)

    def _connect(self, library_path: Optional[str]) -> None:
        candidates = []

        if library_path:
            candidates.append(library_path)

        candidates.extend(self._DEFAULT_CANDIDATES)

        for path in candidates:
            if not path:
                continue
            if not os.path.exists(path):
                continue
            try:
                lib = ctypes.CDLL(path)
                if hasattr(lib, "D_PostEvent"):
                    lib.D_PostEvent.argtypes = [ctypes.POINTER(DoomEvent)]
                    lib.D_PostEvent.restype = None
                    self.lib = lib
                    self.connected = True
                    return
            except OSError as exc:
                self.last_error = f"Falha ao abrir {path}: {exc}"
                continue

        self.last_error = (
            "Nenhuma biblioteca C exportando D_PostEvent foi encontrada. "
            "O projeto atual compila como executável e não como .so, então o "
            "binding em ctypes deve ser usado contra uma C library ou um shim "
            "compilado separadamente."
        )

    def _send_event(self, keycode: int, pressed: bool) -> dict:
        event_type = DoomEventType.EV_KEYDOWN if pressed else DoomEventType.EV_KEYUP

        if self.connected and self.lib is not None:
            ev = DoomEvent()
            ev.type = int(event_type)
            ev.data1 = int(keycode)
            ev.data2 = 0
            ev.data3 = 0
            ev.data4 = 0
            self.lib.D_PostEvent(ctypes.byref(ev))
            return {
                "mode": "ctypes",
                "key": keycode,
                "pressed": pressed,
            }

        return {
            "mode": "fallback",
            "key": keycode,
            "pressed": pressed,
            "note": "Fallback: ação apenas registrada em Python; conecte uma lib C exportando D_PostEvent() para aplicar no jogo.",
        }

    def left(self, pressed: bool = True) -> dict:
        return self._send_event(KEY_LEFTARROW, pressed)

    def right(self, pressed: bool = True) -> dict:
        return self._send_event(KEY_RIGHTARROW, pressed)

    def up(self, pressed: bool = True) -> dict:
        return self._send_event(KEY_UPARROW, pressed)

    def down(self, pressed: bool = True) -> dict:
        return self._send_event(KEY_DOWNARROW, pressed)

    def move(self, direction: str, pressed: bool = True) -> dict:
        direction = direction.lower()
        if direction == "left":
            return self.left(pressed)
        if direction == "right":
            return self.right(pressed)
        if direction == "up":
            return self.up(pressed)
        if direction == "down":
            return self.down(pressed)
        raise ValueError(f"Direção inválida: {direction!r}. Use left, right, up ou down.")

    def press_left(self) -> dict:
        return self.left(True)

    def release_left(self) -> dict:
        return self.left(False)

    def press_right(self) -> dict:
        return self.right(True)

    def release_right(self) -> dict:
        return self.right(False)

    def press_up(self) -> dict:
        return self.up(True)

    def release_up(self) -> dict:
        return self.up(False)

    def press_down(self) -> dict:
        return self.down(True)

    def release_down(self) -> dict:
        return self.down(False)


if __name__ == "__main__":
    bridge = DoomInputBridge()
    print("Conectado:", bridge.connected)
    if bridge.last_error:
        print(bridge.last_error)

    print(bridge.press_up())
    print(bridge.release_up())
    print(bridge.press_right())
    print(bridge.release_right())
