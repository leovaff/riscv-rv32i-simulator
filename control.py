from dataclasses import dataclass

import alu
from immediate import BRANCH, LOAD, OP_IMM, STORE

OP = 0x33

R_TYPE_OPERATIONS = {
    (0x0, 0x00): alu.ADD,
    (0x0, 0x20): alu.SUB,
    (0x1, 0x00): alu.SLL,
    (0x2, 0x00): alu.SLT,
    (0x3, 0x00): alu.SLTU,
    (0x4, 0x00): alu.XOR,
    (0x5, 0x00): alu.SRL,
    (0x5, 0x20): alu.SRA,
    (0x6, 0x00): alu.OR,
    (0x7, 0x00): alu.AND,
    (0x6, 0x20): alu.ORN,
}

BRANCH_OPERATIONS = {
    0x0: alu.SUB,
    0x1: alu.SUB,
    0x4: alu.SLT,
    0x5: alu.SLT,
    0x6: alu.SLTU,
    0x7: alu.SLTU,
}


@dataclass(frozen=True)
class ControlSignals:
    reg_write: bool = False
    alu_src: bool = False
    mem_read: bool = False
    mem_write: bool = False
    mem_to_reg: bool = False
    branch: bool = False


class ControlUnit:
    def decode(self, opcode: int) -> ControlSignals:
        if opcode == OP:
            return ControlSignals(reg_write=True)
        if opcode == OP_IMM:
            return ControlSignals(reg_write=True, alu_src=True)
        if opcode == LOAD:
            return ControlSignals(reg_write=True, alu_src=True, mem_read=True, mem_to_reg=True)
        if opcode == STORE:
            return ControlSignals(alu_src=True, mem_write=True)
        if opcode == BRANCH:
            return ControlSignals(branch=True)

        raise ValueError("Instrução não implementada.")

    def alu_operation(self, opcode: int, funct3: int, funct7: int) -> str:
        if opcode in (LOAD, STORE):
            if funct3 != 0x2:
                raise ValueError("Instrução não implementada.")
            return alu.ADD

        if opcode == BRANCH:
            if funct3 not in BRANCH_OPERATIONS:
                raise ValueError("Instrução não implementada.")
            return BRANCH_OPERATIONS[funct3]

        if opcode == OP_IMM and funct3 not in (0x1, 0x5):
            funct7 = 0x00

        if (funct3, funct7) not in R_TYPE_OPERATIONS:
            raise ValueError("Instrução não implementada.")
        return R_TYPE_OPERATIONS[(funct3, funct7)]
