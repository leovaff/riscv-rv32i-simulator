def _r_type(funct7: int, funct3: int, rd: int, rs1: int, rs2: int) -> int:
    return funct7 << 25 | rs2 << 20 | rs1 << 15 | funct3 << 12 | rd << 7 | 0x33


def _i_type(opcode: int, funct3: int, rd: int, rs1: int, imm: int) -> int:
    if not -2048 <= imm <= 2047:
        raise ValueError("O imediato deve caber em 12 bits.")
    return (imm & 0xFFF) << 20 | rs1 << 15 | funct3 << 12 | rd << 7 | opcode


def _shift_type(funct7: int, funct3: int, rd: int, rs1: int, shamt: int) -> int:
    if not 0 <= shamt < 32:
        raise ValueError("O deslocamento deve estar entre 0 e 31.")
    return funct7 << 25 | shamt << 20 | rs1 << 15 | funct3 << 12 | rd << 7 | 0x13


def _s_type(rs1: int, rs2: int, imm: int) -> int:
    if not -2048 <= imm <= 2047:
        raise ValueError("O imediato deve caber em 12 bits.")
    imm &= 0xFFF
    return (imm >> 5) << 25 | rs2 << 20 | rs1 << 15 | 0x2 << 12 | (imm & 0x1F) << 7 | 0x23


def _b_type(funct3: int, rs1: int, rs2: int, offset: int) -> int:
    if offset % 2 != 0 or not -4096 <= offset <= 4094:
        raise ValueError("Deslocamento de desvio inválido.")
    imm = offset & 0x1FFF
    return (
        ((imm >> 12) & 0x1) << 31
        | ((imm >> 5) & 0x3F) << 25
        | rs2 << 20
        | rs1 << 15
        | funct3 << 12
        | ((imm >> 1) & 0xF) << 8
        | ((imm >> 11) & 0x1) << 7
        | 0x63
    )


def add(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x0, rd, rs1, rs2)


def sub(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x20, 0x0, rd, rs1, rs2)


def sll(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x1, rd, rs1, rs2)


def slt(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x2, rd, rs1, rs2)


def sltu(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x3, rd, rs1, rs2)


def xor(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x4, rd, rs1, rs2)


def srl(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x5, rd, rs1, rs2)


def sra(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x20, 0x5, rd, rs1, rs2)


def or_(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x6, rd, rs1, rs2)


def and_(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x00, 0x7, rd, rs1, rs2)


def orn(rd: int, rs1: int, rs2: int) -> int:
    return _r_type(0x20, 0x6, rd, rs1, rs2)


def addi(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x0, rd, rs1, imm)


def slti(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x2, rd, rs1, imm)


def sltiu(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x3, rd, rs1, imm)


def xori(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x4, rd, rs1, imm)


def ori(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x6, rd, rs1, imm)


def andi(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x13, 0x7, rd, rs1, imm)


def slli(rd: int, rs1: int, shamt: int) -> int:
    return _shift_type(0x00, 0x1, rd, rs1, shamt)


def srli(rd: int, rs1: int, shamt: int) -> int:
    return _shift_type(0x00, 0x5, rd, rs1, shamt)


def srai(rd: int, rs1: int, shamt: int) -> int:
    return _shift_type(0x20, 0x5, rd, rs1, shamt)


def lw(rd: int, rs1: int, imm: int) -> int:
    return _i_type(0x03, 0x2, rd, rs1, imm)


def sw(rs2: int, rs1: int, imm: int) -> int:
    return _s_type(rs1, rs2, imm)


def beq(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x0, rs1, rs2, offset)


def bne(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x1, rs1, rs2, offset)


def blt(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x4, rs1, rs2, offset)


def bge(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x5, rs1, rs2, offset)


def bltu(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x6, rs1, rs2, offset)


def bgeu(rs1: int, rs2: int, offset: int) -> int:
    return _b_type(0x7, rs1, rs2, offset)


def mret() -> int:
    return 0x30200073


def text_to_words(text: str) -> list[int]:
    data = text.encode("ascii")
    data += bytes(4 - len(data) % 4)
    return [int.from_bytes(data[i:i + 4], "little") for i in range(0, len(data), 4)]
