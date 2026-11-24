OP_IMM = 0x13
LOAD = 0x03
STORE = 0x23
BRANCH = 0x63


def sign_extend(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


class ImmediateGenerator:
    def generate(self, instruction: int) -> int:
        opcode = instruction & 0x7F

        if opcode in (OP_IMM, LOAD):
            return sign_extend(instruction >> 20, 12)

        if opcode == STORE:
            imm = ((instruction >> 25) & 0x7F) << 5 | ((instruction >> 7) & 0x1F)
            return sign_extend(imm, 12)

        if opcode == BRANCH:
            imm = (
                ((instruction >> 31) & 0x1) << 12
                | ((instruction >> 7) & 0x1) << 11
                | ((instruction >> 25) & 0x3F) << 5
                | ((instruction >> 8) & 0xF) << 1
            )
            return sign_extend(imm, 13)

        return 0
