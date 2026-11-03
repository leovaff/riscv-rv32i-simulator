import unittest

from cpu import CPU


class CPUTest(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()

    def test_initial_state(self):
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual([self.cpu.read_register(i) for i in range(32)], [0] * 32)

    def test_x0_ignores_writes_and_instruction_results(self):
        self.cpu.write_register(0, 123)
        self.assertEqual(self.cpu.read_register(0), 0)
        self.cpu.write_register(1, 10)
        self.cpu.write_register(2, 3)
        self.cpu.execute(0x00208033)
        self.cpu.execute(0x40208033)
        self.assertEqual(self.cpu.read_register(0), 0)
        self.assertEqual(self.cpu.pc, 8)

    def test_register_values_are_limited_to_32_bits(self):
        for value, expected in [(-1, 0xFFFFFFFF), (0x100000005, 5)]:
            with self.subTest(value=value):
                self.cpu.write_register(31, value)
                self.assertEqual(self.cpu.read_register(31), expected)

    def test_add_and_sub(self):
        self.cpu.write_register(1, 10)
        self.cpu.write_register(2, 3)
        self.cpu.execute(0x002081B3)
        self.assertEqual(self.cpu.read_register(3), 13)
        self.assertEqual(self.cpu.pc, 4)
        self.cpu.execute(0x40208233)
        self.assertEqual(self.cpu.read_register(4), 7)
        self.assertEqual(self.cpu.pc, 8)

    def test_add_overflow(self):
        self.cpu.write_register(1, 0xFFFFFFFF)
        self.cpu.write_register(2, 1)
        self.cpu.execute(0x002081B3)
        self.assertEqual(self.cpu.read_register(3), 0)

    def test_sub_negative_result(self):
        self.cpu.write_register(1, 3)
        self.cpu.write_register(2, 10)
        self.cpu.execute(0x40208233)
        self.assertEqual(self.cpu.read_register(4), 0xFFFFFFF9)

    def test_destination_can_be_a_source(self):
        self.cpu.write_register(1, 10)
        self.cpu.write_register(2, 3)
        self.cpu.execute(0x002080B3)
        self.assertEqual(self.cpu.read_register(1), 13)
        self.cpu.execute(0x40208133)
        self.assertEqual(self.cpu.read_register(2), 10)

    def test_unsupported_instructions_preserve_state(self):
        self.cpu.write_register(1, 10)
        self.cpu.write_register(2, 3)
        self.cpu.write_register(3, 99)
        self.cpu.execute(0x00208233)
        before = self.cpu.registers.copy()
        for instruction in [0x00100093, 0x022081B3, 0x0020F1B3, -1, 0x1002081B3]:
            with self.subTest(instruction=instruction):
                with self.assertRaises(ValueError):
                    self.cpu.execute(instruction)
                self.assertEqual(self.cpu.registers, before)
                self.assertEqual(self.cpu.pc, 4)

    def test_invalid_register_indices(self):
        for index in [-1, 32]:
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    self.cpu.read_register(index)
                with self.assertRaises(ValueError):
                    self.cpu.write_register(index, 1)


if __name__ == "__main__":
    unittest.main()
