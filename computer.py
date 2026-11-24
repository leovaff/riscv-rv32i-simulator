from typing import Callable

from bus import RESERVED_START, VRAM_START, Bus
from cpu import CPU
from memory import Memory


class Computer:
    def __init__(self, vram_interval: int = 10):
        if vram_interval <= 0:
            raise ValueError("O intervalo da VRAM deve ser maior que zero.")

        self.memory = Memory()
        self.bus = Bus(self.memory)
        self.cpu = CPU(self.bus)
        self.vram_interval = vram_interval

    def load(self, words: list[int], start: int = 0) -> None:
        self.memory.load_program(words, start)

    def read_vram(self) -> str:
        text = []
        for address in range(VRAM_START, RESERVED_START, 4):
            for byte in self.bus.read(address).to_bytes(4, "little"):
                if byte == 0:
                    return "".join(text)
                text.append(chr(byte) if 32 <= byte < 127 or byte == 10 else "?")
        return "".join(text)

    def _show_vram(self, steps: int, output: Callable[[str], None]) -> None:
        output(f"[VRAM após {steps} instruções]")
        output(self.read_vram().rstrip("\n"))

    def run(self, max_steps: int = 10000, output: Callable[[str], None] = print) -> int:
        steps = 0
        while steps < max_steps and self.bus.read(self.cpu.pc) != 0:
            self.cpu.step()
            steps += 1
            if steps % self.vram_interval == 0:
                self._show_vram(steps, output)

        if steps % self.vram_interval != 0:
            self._show_vram(steps, output)
        return steps
