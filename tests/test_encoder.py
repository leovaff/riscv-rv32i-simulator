import unittest

from encoder import (
    add, addi, and_, andi, beq, bge, bgeu, blt, bltu, bne, lw, or_, ori, orn, sll, slli,
    slt, slti, sltiu, sltu, sra, srai, srl, srli, sub, sw, text_to_words, xor, xori,
)


class EncoderTest(unittest.TestCase):
    def test_r_type(self):
        cases = [
            (add(3, 1, 2), 0x002081B3),
            (sub(3, 1, 2), 0x402081B3),
            (sll(3, 1, 2), 0x002091B3),
            (slt(3, 1, 2), 0x0020A1B3),
            (sltu(3, 1, 2), 0x0020B1B3),
            (xor(3, 1, 2), 0x0020C1B3),
            (srl(3, 1, 2), 0x0020D1B3),
            (sra(3, 1, 2), 0x4020D1B3),
            (or_(3, 1, 2), 0x0020E1B3),
            (and_(3, 1, 2), 0x0020F1B3),
            (orn(3, 1, 2), 0x4020E1B3),
        ]
        for encoded, expected in cases:
            with self.subTest(expected=hex(expected)):
                self.assertEqual(encoded, expected)

    def test_i_type(self):
        cases = [
            (addi(3, 1, 5), 0x00508193),
            (addi(3, 1, -1), 0xFFF08193),
            (slti(3, 1, -1), 0xFFF0A193),
            (sltiu(3, 1, -1), 0xFFF0B193),
            (xori(3, 1, -1), 0xFFF0C193),
            (ori(3, 1, 0xF0), 0x0F00E193),
            (andi(3, 1, 0xF), 0x00F0F193),
            (slli(3, 1, 4), 0x00409193),
            (srli(3, 1, 4), 0x0040D193),
            (srai(3, 1, 4), 0x4040D193),
        ]
        for encoded, expected in cases:
            with self.subTest(expected=hex(expected)):
                self.assertEqual(encoded, expected)

    def test_memory_access(self):
        self.assertEqual(lw(3, 1, 8), 0x0080A183)
        self.assertEqual(lw(3, 1, -4), 0xFFC0A183)
        self.assertEqual(sw(2, 1, 8), 0x0020A423)
        self.assertEqual(sw(2, 1, -4), 0xFE20AE23)

    def test_branches(self):
        cases = [
            (beq(1, 2, 8), 0x00208463),
            (bne(1, 2, 8), 0x00209463),
            (blt(1, 2, 8), 0x0020C463),
            (bge(1, 2, 8), 0x0020D463),
            (bltu(1, 2, 8), 0x0020E463),
            (bgeu(1, 2, 8), 0x0020F463),
            (beq(0, 0, -4), 0xFE000EE3),
            (blt(2, 3, -8), 0xFE314CE3),
        ]
        for encoded, expected in cases:
            with self.subTest(expected=hex(expected)):
                self.assertEqual(encoded, expected)

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            addi(1, 0, 2048)
        with self.assertRaises(ValueError):
            sw(1, 0, -2049)
        with self.assertRaises(ValueError):
            slli(1, 1, 32)
        with self.assertRaises(ValueError):
            beq(0, 0, 3)

    def test_text_to_words(self):
        self.assertEqual(text_to_words("ABCD"), [0x44434241, 0])
        self.assertEqual(text_to_words("OK"), [0x00004B4F])


if __name__ == "__main__":
    unittest.main()
