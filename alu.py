MASK_32 = 0xFFFFFFFF

ADD = "ADD"
SUB = "SUB"
SLL = "SLL"
SLT = "SLT"
SLTU = "SLTU"
XOR = "XOR"
SRL = "SRL"
SRA = "SRA"
OR = "OR"
AND = "AND"
ORN = "ORN"


def to_signed(value: int) -> int:
    if value & 0x80000000:
        return value - 0x100000000
    return value


class ALU:
    def execute(self, operation: str, a: int, b: int) -> int:
        shamt = b & 0x1F

        if operation == ADD:
            result = a + b
        elif operation == SUB:
            result = a - b
        elif operation == SLL:
            result = a << shamt
        elif operation == SLT:
            result = int(to_signed(a) < to_signed(b))
        elif operation == SLTU:
            result = int(a < b)
        elif operation == XOR:
            result = a ^ b
        elif operation == SRL:
            result = a >> shamt
        elif operation == SRA:
            result = to_signed(a) >> shamt
        elif operation == OR:
            result = a | b
        elif operation == AND:
            result = a & b
        elif operation == ORN:
            result = a | (~b & MASK_32)
        else:
            raise ValueError("Operação da ULA inválida.")

        return result & MASK_32
