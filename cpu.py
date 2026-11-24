from bus import Bus

MASK_32 = 0xFFFFFFFF


class CPU:
    def __init__(self, bus: Bus | None = None):
        self.registers = [0] * 32
        self.pc = 0x00000
        self.bus = bus if bus is not None else Bus()
        self.memory = self.bus.memory

    @staticmethod
    def _validate_register(reg_num: int) -> None:
        if not 0 <= reg_num < 32:
            raise ValueError("O registrador deve estar entre x0 e x31.")

    @staticmethod
    def _to_signed(value: int) -> int:
        if value & 0x80000000:
            return value - 0x100000000
        return value

    @staticmethod
    def _sign_extend(value: int, bits: int) -> int:
        value &= (1 << bits) - 1
        if value & (1 << (bits - 1)):
            value -= 1 << bits
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

    def _branch_taken(self, funct3: int, val_rs1: int, val_rs2: int) -> bool:
        if funct3 == 0x0:
            return val_rs1 == val_rs2
        if funct3 == 0x1:
            return val_rs1 != val_rs2
        if funct3 == 0x4:
            return self._to_signed(val_rs1) < self._to_signed(val_rs2)
        if funct3 == 0x5:
            return self._to_signed(val_rs1) >= self._to_signed(val_rs2)
        if funct3 == 0x6:
            return val_rs1 < val_rs2
        if funct3 == 0x7:
            return val_rs1 >= val_rs2

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

        next_pc = self.pc + 4

        if opcode == 0x33:
            val_rs1 = self.read_register(rs1)
            val_rs2 = self.read_register(rs2)
            self.write_register(rd, self._execute_r_type(funct3, funct7, val_rs1, val_rs2))
        elif opcode == 0x13:
            imm = self._sign_extend(instruction >> 20, 12)

            if funct3 not in (0x1, 0x5):
                funct7 = 0x00

            val_rs1 = self.read_register(rs1)
            self.write_register(rd, self._execute_r_type(funct3, funct7, val_rs1, imm & MASK_32))
        elif opcode == 0x03:
            if funct3 != 0x2:
                raise ValueError("Instrução não implementada.")

            imm = self._sign_extend(instruction >> 20, 12)
            address = (self.read_register(rs1) + imm) & MASK_32
            self.write_register(rd, self.bus.read(address))
        elif opcode == 0x23:
            if funct3 != 0x2:
                raise ValueError("Instrução não implementada.")

            imm = self._sign_extend((funct7 << 5) | rd, 12)
            address = (self.read_register(rs1) + imm) & MASK_32
            self.bus.write(address, self.read_register(rs2))
        elif opcode == 0x63:
            imm = (
                ((instruction >> 31) & 0x1) << 12
                | ((instruction >> 7) & 0x1) << 11
                | ((instruction >> 25) & 0x3F) << 5
                | ((instruction >> 8) & 0xF) << 1
            )
            imm = self._sign_extend(imm, 13)

            if self._branch_taken(funct3, self.read_register(rs1), self.read_register(rs2)):
                next_pc = self.pc + imm
        else:
            raise ValueError("Instrução não implementada.")

        self.pc = next_pc & MASK_32

    def step(self) -> None:
        instruction = self.bus.read(self.pc)
        self.execute(instruction)

    def run(self, max_steps: int = 1000) -> int:
        steps = 0
        while steps < max_steps and self.bus.read(self.pc) != 0:
            self.step()
            steps += 1
        return steps
