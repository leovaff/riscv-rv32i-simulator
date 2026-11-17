import unittest

from memory import MEMORY_SIZE, Memory


class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()

    def test_initial_state(self):
        self.assertEqual(len(self.memory.data), MEMORY_SIZE)
        self.assertEqual(self.memory.read_word(0), 0)

    def test_write_and_read_word(self):
        self.memory.write_word(0x40, 0x12345678)
        self.assertEqual(self.memory.read_word(0x40), 0x12345678)

    def test_little_endian(self):
        self.memory.write_word(0, 0x12345678)
        self.assertEqual(list(self.memory.data[0:4]), [0x78, 0x56, 0x34, 0x12])

    def test_values_are_limited_to_32_bits(self):
        self.memory.write_word(0, -1)
        self.assertEqual(self.memory.read_word(0), 0xFFFFFFFF)

    def test_last_word(self):
        self.memory.write_word(MEMORY_SIZE - 4, 7)
        self.assertEqual(self.memory.read_word(MEMORY_SIZE - 4), 7)

    def test_invalid_addresses(self):
        for address in [-4, 2, MEMORY_SIZE, 0xFFFFFFFC]:
            with self.subTest(address=hex(address)):
                with self.assertRaises(ValueError):
                    self.memory.read_word(address)
                with self.assertRaises(ValueError):
                    self.memory.write_word(address, 1)

    def test_load_program(self):
        self.memory.load_program([0x11, 0x22, 0x33], start=0x100)
        self.assertEqual(self.memory.read_word(0x100), 0x11)
        self.assertEqual(self.memory.read_word(0x104), 0x22)
        self.assertEqual(self.memory.read_word(0x108), 0x33)


if __name__ == "__main__":
    unittest.main()
