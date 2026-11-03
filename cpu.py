MASK_32 = 0xFFFFFFFF


class CPU:
    def __init__(self):
        self.registers = [0] * 32
        self.pc = 0x00000

    @staticmethod
    def _validate_register(reg_num: int) -> None:
        if not 0 <= reg_num < 32:
            raise ValueError("O registrador deve estar entre x0 e x31.")

    def read_register(self, reg_num: int) -> int:
        self._validate_register(reg_num)
        if reg_num == 0:
            return 0
        return self.registers[reg_num]

    def write_register(self, reg_num: int, value: int) -> None:
        self._validate_register(reg_num)
        if reg_num != 0:
            self.registers[reg_num] = value & MASK_32

    def execute(self, instruction: int) -> None:
        if not 0 <= instruction <= MASK_32:
            raise ValueError("A instrução deve ser uma palavra de 32 bits.")

        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F

        if opcode != 0x33 or funct3 != 0 or funct7 not in (0x00, 0x20):
            raise ValueError("Instrução não implementada.")

        val_rs1 = self.read_register(rs1)
        val_rs2 = self.read_register(rs2)

        if funct7 == 0x00:
            result = val_rs1 + val_rs2
        else:
            result = val_rs1 - val_rs2

        self.write_register(rd, result)
        self.pc = (self.pc + 4) & MASK_32
