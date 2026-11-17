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

    def test_logic_operations(self):
        self.cpu.write_register(1, 0b1100)
        self.cpu.write_register(2, 0b1010)
        cases = [
            (0x0020C1B3, 0b0110),
            (0x0020E1B3, 0b1110),
            (0x0020F1B3, 0b1000),
        ]
        for instruction, expected in cases:
            with self.subTest(instruction=hex(instruction)):
                self.cpu.execute(instruction)
                self.assertEqual(self.cpu.read_register(3), expected)

    def test_shifts(self):
        self.cpu.write_register(1, 0x80000010)
        self.cpu.write_register(2, 4)
        cases = [
            (0x002091B3, 0x00000100),
            (0x0020D1B3, 0x08000001),
            (0x4020D1B3, 0xF8000001),
        ]
        for instruction, expected in cases:
            with self.subTest(instruction=hex(instruction)):
                self.cpu.execute(instruction)
                self.assertEqual(self.cpu.read_register(3), expected)

    def test_shift_uses_only_low_five_bits(self):
        self.cpu.write_register(1, 1)
        self.cpu.write_register(2, 33)
        self.cpu.execute(0x002091B3)
        self.assertEqual(self.cpu.read_register(3), 2)

    def test_slt_and_sltu(self):
        self.cpu.write_register(1, 0xFFFFFFFF)
        self.cpu.write_register(2, 1)
        self.cpu.execute(0x0020A1B3)
        self.assertEqual(self.cpu.read_register(3), 1)
        self.cpu.execute(0x0020B1B3)
        self.assertEqual(self.cpu.read_register(3), 0)

    def test_orn(self):
        self.cpu.write_register(1, 0x0000000F)
        self.cpu.write_register(2, 0xFFFF0000)
        self.cpu.execute(0x4020E1B3)
        self.assertEqual(self.cpu.read_register(3), 0x0000FFFF)
        self.assertEqual(self.cpu.pc, 4)

    def test_orn_with_zero_register(self):
        self.cpu.write_register(1, 0x12345678)
        self.cpu.execute(0x4000E1B3)
        self.assertEqual(self.cpu.read_register(3), 0xFFFFFFFF)

    def test_addi(self):
        self.cpu.write_register(1, 10)
        self.cpu.execute(0x00508193)
        self.assertEqual(self.cpu.read_register(3), 15)
        self.cpu.execute(0xFFF08193)
        self.assertEqual(self.cpu.read_register(3), 9)
        self.assertEqual(self.cpu.pc, 8)

    def test_addi_loads_constant_from_x0(self):
        self.cpu.execute(0x00100093)
        self.assertEqual(self.cpu.read_register(1), 1)

    def test_slti_and_sltiu(self):
        self.cpu.write_register(1, 5)
        self.cpu.execute(0xFFF0A193)
        self.assertEqual(self.cpu.read_register(3), 0)
        self.cpu.execute(0xFFF0B193)
        self.assertEqual(self.cpu.read_register(3), 1)

    def test_logic_immediates(self):
        self.cpu.write_register(1, 0x0000003C)
        cases = [
            (0xFFF0C193, 0xFFFFFFC3),
            (0x0F00E193, 0x000000FC),
            (0x00F0F193, 0x0000000C),
        ]
        for instruction, expected in cases:
            with self.subTest(instruction=hex(instruction)):
                self.cpu.execute(instruction)
                self.assertEqual(self.cpu.read_register(3), expected)

    def test_ori_is_not_orn(self):
        self.cpu.write_register(1, 0x1)
        self.cpu.execute(0x4000E193)
        self.assertEqual(self.cpu.read_register(3), 0x401)

    def test_shift_immediates(self):
        self.cpu.write_register(1, 0x80000010)
        cases = [
            (0x00409193, 0x00000100),
            (0x0040D193, 0x08000001),
            (0x4040D193, 0xF8000001),
        ]
        for instruction, expected in cases:
            with self.subTest(instruction=hex(instruction)):
                self.cpu.execute(instruction)
                self.assertEqual(self.cpu.read_register(3), expected)

    def test_sw_and_lw(self):
        self.cpu.write_register(1, 0x100)
        self.cpu.write_register(2, 0xDEADBEEF)
        self.cpu.execute(0x0020A423)
        self.assertEqual(self.cpu.memory.read_word(0x108), 0xDEADBEEF)
        self.cpu.execute(0x0080A183)
        self.assertEqual(self.cpu.read_register(3), 0xDEADBEEF)
        self.assertEqual(self.cpu.pc, 8)

    def test_sw_and_lw_with_negative_offset(self):
        self.cpu.write_register(1, 0x100)
        self.cpu.write_register(2, 42)
        self.cpu.execute(0xFE20AE23)
        self.assertEqual(self.cpu.memory.read_word(0xFC), 42)
        self.cpu.execute(0xFFC0A183)
        self.assertEqual(self.cpu.read_register(3), 42)

    def test_lw_misaligned_address(self):
        self.cpu.write_register(1, 0x100)
        with self.assertRaises(ValueError):
            self.cpu.execute(0x0020A183)
        self.assertEqual(self.cpu.read_register(3), 0)
        self.assertEqual(self.cpu.pc, 0)

    def test_branches(self):
        cases = [
            (0x00208463, 5, 5, True),
            (0x00208463, 5, 6, False),
            (0x00209463, 5, 6, True),
            (0x00209463, 5, 5, False),
            (0x0020C463, 0xFFFFFFFF, 1, True),
            (0x0020D463, 0xFFFFFFFF, 1, False),
            (0x0020E463, 0xFFFFFFFF, 1, False),
            (0x0020F463, 0xFFFFFFFF, 1, True),
        ]
        for instruction, val_rs1, val_rs2, taken in cases:
            with self.subTest(instruction=hex(instruction), rs1=val_rs1, rs2=val_rs2):
                cpu = CPU()
                cpu.write_register(1, val_rs1)
                cpu.write_register(2, val_rs2)
                cpu.execute(instruction)
                self.assertEqual(cpu.pc, 8 if taken else 4)

    def test_branch_backwards(self):
        self.cpu.pc = 0x20
        self.cpu.execute(0xFE000CE3)
        self.assertEqual(self.cpu.pc, 0x18)

    def test_step_fetches_from_memory(self):
        self.cpu.memory.load_program([0x00500093, 0x00108133])
        self.cpu.step()
        self.assertEqual(self.cpu.read_register(1), 5)
        self.cpu.step()
        self.assertEqual(self.cpu.read_register(2), 10)
        self.assertEqual(self.cpu.pc, 8)

    def test_run_loop_program(self):
        program = [
            0x00000093,
            0x00100113,
            0x00600193,
            0x002080B3,
            0x00110113,
            0xFE314CE3,
            0x10102023,
            0x10002203,
        ]
        self.cpu.memory.load_program(program)
        steps = self.cpu.run()
        self.assertEqual(self.cpu.read_register(1), 15)
        self.assertEqual(self.cpu.memory.read_word(0x100), 15)
        self.assertEqual(self.cpu.read_register(4), 15)
        self.assertEqual(self.cpu.pc, 32)
        self.assertEqual(steps, 20)

    def test_run_respects_max_steps(self):
        self.cpu.memory.load_program([0x00000063])
        self.assertEqual(self.cpu.run(max_steps=50), 50)
        self.assertEqual(self.cpu.pc, 0)

    def test_unsupported_instructions_preserve_state(self):
        self.cpu.write_register(1, 10)
        self.cpu.write_register(2, 3)
        self.cpu.write_register(3, 99)
        self.cpu.execute(0x00208233)
        before = self.cpu.registers.copy()
        for instruction in [0x00008183, 0x022081B3, 0x402091B3, 0x40409193, 0x0020A463, -1, 0x1002081B3]:
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
