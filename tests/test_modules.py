import unittest

import alu
from alu import ALU
from control import ControlUnit
from encoder import addi, beq, blt, lw, sw
from immediate import ImmediateGenerator
from registers import RegisterFile


class RegisterFileTest(unittest.TestCase):
    def test_x0_is_always_zero(self):
        registers = RegisterFile()
        registers.write(0, 5)
        self.assertEqual(registers.read(0), 0)

    def test_write_and_read(self):
        registers = RegisterFile()
        registers.write(31, -1)
        self.assertEqual(registers.read(31), 0xFFFFFFFF)


class ALUTest(unittest.TestCase):
    def setUp(self):
        self.alu = ALU()

    def test_operations(self):
        cases = [
            (alu.ADD, 0xFFFFFFFF, 1, 0),
            (alu.SUB, 3, 10, 0xFFFFFFF9),
            (alu.SLL, 1, 33, 2),
            (alu.SLT, 0xFFFFFFFF, 1, 1),
            (alu.SLTU, 0xFFFFFFFF, 1, 0),
            (alu.XOR, 0b1100, 0b1010, 0b0110),
            (alu.SRL, 0x80000000, 4, 0x08000000),
            (alu.SRA, 0x80000000, 4, 0xF8000000),
            (alu.OR, 0b1100, 0b1010, 0b1110),
            (alu.AND, 0b1100, 0b1010, 0b1000),
            (alu.ORN, 0x0000000F, 0xFFFF0000, 0x0000FFFF),
        ]
        for operation, a, b, expected in cases:
            with self.subTest(operation=operation):
                self.assertEqual(self.alu.execute(operation, a, b), expected)

    def test_invalid_operation(self):
        with self.assertRaises(ValueError):
            self.alu.execute("MUL", 1, 2)


class ImmediateGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.generator = ImmediateGenerator()

    def test_formats(self):
        cases = [
            (addi(1, 0, -5), -5),
            (lw(1, 2, 2047), 2047),
            (sw(1, 2, -2048), -2048),
            (sw(1, 2, 40), 40),
            (beq(1, 2, -8), -8),
            (blt(1, 2, 4094), 4094),
            (0x002081B3, 0),
        ]
        for instruction, expected in cases:
            with self.subTest(instruction=hex(instruction)):
                self.assertEqual(self.generator.generate(instruction), expected)


class ControlUnitTest(unittest.TestCase):
    def setUp(self):
        self.control = ControlUnit()

    def test_signals(self):
        r_type = self.control.decode(0x33)
        self.assertTrue(r_type.reg_write)
        self.assertFalse(r_type.alu_src)

        load = self.control.decode(0x03)
        self.assertTrue(load.mem_read and load.mem_to_reg and load.reg_write and load.alu_src)

        store = self.control.decode(0x23)
        self.assertTrue(store.mem_write and store.alu_src)
        self.assertFalse(store.reg_write)

        branch = self.control.decode(0x63)
        self.assertTrue(branch.branch)
        self.assertFalse(branch.reg_write)

    def test_unknown_opcode(self):
        with self.assertRaises(ValueError):
            self.control.decode(0x6F)

    def test_alu_operation(self):
        cases = [
            (0x33, 0x0, 0x20, alu.SUB),
            (0x33, 0x6, 0x20, alu.ORN),
            (0x13, 0x6, 0x20, alu.OR),
            (0x13, 0x0, 0x20, alu.ADD),
            (0x13, 0x5, 0x20, alu.SRA),
            (0x03, 0x2, 0x00, alu.ADD),
            (0x23, 0x2, 0x00, alu.ADD),
            (0x63, 0x1, 0x00, alu.SUB),
            (0x63, 0x5, 0x00, alu.SLT),
            (0x63, 0x7, 0x00, alu.SLTU),
        ]
        for opcode, funct3, funct7, expected in cases:
            with self.subTest(opcode=hex(opcode), funct3=funct3, funct7=funct7):
                self.assertEqual(self.control.alu_operation(opcode, funct3, funct7), expected)


if __name__ == "__main__":
    unittest.main()
