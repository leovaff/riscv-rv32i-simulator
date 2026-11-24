from computer import Computer
from encoder import add, addi, beq, blt, bne, lw, orn, slli, sw, text_to_words

SUM_ADDRESS = 0x300
MESSAGE_OK_ADDRESS = 0x400
MESSAGE_ERROR_ADDRESS = 0x480

MESSAGE_OK = "Grupo 13 - Simulador RISC-V\nORN OK\n"
MESSAGE_ERROR = "Grupo 13 - Simulador RISC-V\nORN ERRO\n"


def build_program() -> list[int]:
    return [
        addi(1, 0, 0),
        addi(2, 0, 1),
        addi(3, 0, 11),
        add(1, 1, 2),
        addi(2, 2, 1),
        blt(2, 3, -8),
        sw(1, 0, SUM_ADDRESS),

        addi(10, 0, 0x0F0),
        addi(11, 0, -256),
        orn(12, 10, 11),
        addi(13, 0, 0x0FF),
        addi(5, 0, MESSAGE_OK_ADDRESS),
        beq(12, 13, 8),
        addi(5, 0, MESSAGE_ERROR_ADDRESS),

        addi(6, 0, 1),
        slli(6, 6, 19),
        lw(7, 5, 0),
        sw(7, 6, 0),
        addi(5, 5, 4),
        addi(6, 6, 4),
        bne(7, 0, -16),
    ]


def load_test_program(computer: Computer) -> None:
    computer.load(build_program())
    computer.load(text_to_words(MESSAGE_OK), MESSAGE_OK_ADDRESS)
    computer.load(text_to_words(MESSAGE_ERROR), MESSAGE_ERROR_ADDRESS)
