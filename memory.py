MEMORY_SIZE = 0xA0000


class Memory:
    def __init__(self, size: int = MEMORY_SIZE):
        self.data = bytearray(size)

    def _validate_address(self, address: int) -> None:
        if address % 4 != 0:
            raise ValueError("O endereço deve ser múltiplo de 4.")
        if not 0 <= address <= len(self.data) - 4:
            raise ValueError("Endereço fora da memória.")

    def read_word(self, address: int) -> int:
        self._validate_address(address)
        return int.from_bytes(self.data[address:address + 4], "little")

    def write_word(self, address: int, value: int) -> None:
        self._validate_address(address)
        self.data[address:address + 4] = (value & 0xFFFFFFFF).to_bytes(4, "little")

    def load_program(self, program: list[int], start: int = 0) -> None:
        for i, instruction in enumerate(program):
            self.write_word(start + i * 4, instruction)
