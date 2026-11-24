from memory import Memory

RAM_START = 0x00000
VRAM_START = 0x80000
RESERVED_START = 0x90000
IO_START = 0x9FC00

READ = "READ"
WRITE = "WRITE"


def get_region(address: int) -> str:
    if RAM_START <= address < VRAM_START:
        return "RAM"
    if VRAM_START <= address < RESERVED_START:
        return "VRAM"
    if RESERVED_START <= address < IO_START:
        return "RESERVADO"
    return "E/S"


class Bus:
    def __init__(self, memory: Memory | None = None):
        self.memory = memory if memory is not None else Memory()
        self.address = 0
        self.data = 0
        self.control = None
        self.interrupt = False
        self.devices = {}

    @staticmethod
    def _validate_address(address: int) -> None:
        if RESERVED_START <= address < IO_START:
            raise ValueError("Endereço na área reservada.")

    def attach(self, address: int, device) -> None:
        if address < IO_START:
            raise ValueError("Dispositivos devem ficar na região de E/S.")
        self.devices[address] = device

    def request_interrupt(self) -> None:
        self.interrupt = True

    def acknowledge_interrupt(self) -> None:
        self.interrupt = False

    def read(self, address: int) -> int:
        self._validate_address(address)
        if address in self.devices:
            value = self.devices[address].read() & 0xFFFFFFFF
        else:
            value = self.memory.read_word(address)
        self.address = address
        self.control = READ
        self.data = value
        return value

    def write(self, address: int, value: int) -> None:
        self._validate_address(address)
        if address in self.devices:
            self.devices[address].write(value & 0xFFFFFFFF)
        else:
            self.memory.write_word(address, value)
        self.address = address
        self.control = WRITE
        self.data = value & 0xFFFFFFFF
