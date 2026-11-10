MASK_32 = 0xFFFFFFFF


class CPU:
    def __init__(self):
        self.registers = [0] * 32
        self.pc = 0x00000

    @staticmethod
    def _validate_register(reg_num: int) -> None:
        if not 0 <= reg_num < 32:
            raise ValueError("O registrador deve estar entre x0 e x31.")

    @staticmethod
    def _to_signed(value: int) -> int:
        if value & 0x80000000:
            return value - 0x100000000
        return value

    def read_register(self, reg_num: int) -> int:
        self._validate_register(reg_num)
        if reg_num == 0:
            return 0
        return self.registers[reg_num]

    def write_register(self, reg_num: int, value: int) -> None:
        self._validate_register(reg_num)
        if reg_num != 0:
            self.registers[reg_num] = value & MASK_32

    def _execute_r_type(self, funct3: int, funct7: int, val_rs1: int, val_rs2: int) -> int:
        shamt = val_rs2 & 0x1F

        if funct7 == 0x00:
            if funct3 == 0x0:
                return val_rs1 + val_rs2
            if funct3 == 0x1:
                return val_rs1 << shamt
            if funct3 == 0x2:
                return int(self._to_signed(val_rs1) < self._to_signed(val_rs2))
            if funct3 == 0x3:
                return int(val_rs1 < val_rs2)
            if funct3 == 0x4:
                return val_rs1 ^ val_rs2
            if funct3 == 0x5:
                return val_rs1 >> shamt
            if funct3 == 0x6:
                return val_rs1 | val_rs2
            if funct3 == 0x7:
                return val_rs1 & val_rs2

        if funct7 == 0x20:
            if funct3 == 0x0:
                return val_rs1 - val_rs2
            if funct3 == 0x5:
                return self._to_signed(val_rs1) >> shamt
            if funct3 == 0x6:
                return val_rs1 | (~val_rs2 & MASK_32)

        raise ValueError("Instrução não implementada.")

    def execute(self, instruction: int) -> None:
        if not 0 <= instruction <= MASK_32:
            raise ValueError("A instrução deve ser uma palavra de 32 bits.")

        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F

        if opcode == 0x33:
            val_rs1 = self.read_register(rs1)
            val_rs2 = self.read_register(rs2)
            result = self._execute_r_type(funct3, funct7, val_rs1, val_rs2)
        elif opcode == 0x13:
            imm = (instruction >> 20) & 0xFFF
            if imm & 0x800:
                imm -= 0x1000

            if funct3 not in (0x1, 0x5):
                funct7 = 0x00

            val_rs1 = self.read_register(rs1)
            result = self._execute_r_type(funct3, funct7, val_rs1, imm & MASK_32)
        else:
            raise ValueError("Instrução não implementada.")

        self.write_register(rd, result)
        self.pc = (self.pc + 4) & MASK_32
