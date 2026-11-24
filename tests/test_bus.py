import unittest

from bus import IO_START, READ, RESERVED_START, VRAM_START, WRITE, Bus, get_region
from cpu import CPU


class BusTest(unittest.TestCase):
    def setUp(self):
        self.bus = Bus()

    def test_initial_state(self):
        self.assertEqual(self.bus.address, 0)
        self.assertEqual(self.bus.data, 0)
        self.assertIsNone(self.bus.control)

    def test_write_updates_lines(self):
        self.bus.write(0x100, 0xCAFE)
        self.assertEqual(self.bus.address, 0x100)
        self.assertEqual(self.bus.data, 0xCAFE)
        self.assertEqual(self.bus.control, WRITE)
        self.assertEqual(self.bus.memory.read_word(0x100), 0xCAFE)

    def test_read_updates_lines(self):
        self.bus.memory.write_word(0x200, 77)
        self.assertEqual(self.bus.read(0x200), 77)
        self.assertEqual(self.bus.address, 0x200)
        self.assertEqual(self.bus.data, 77)
        self.assertEqual(self.bus.control, READ)

    def test_regions(self):
        cases = [
            (0x00000, "RAM"),
            (0x7FFFC, "RAM"),
            (VRAM_START, "VRAM"),
            (0x8FFFC, "VRAM"),
            (RESERVED_START, "RESERVADO"),
            (0x9FBFC, "RESERVADO"),
            (IO_START, "E/S"),
            (0x9FFFC, "E/S"),
        ]
        for address, region in cases:
            with self.subTest(address=hex(address)):
                self.assertEqual(get_region(address), region)

    def test_vram_and_io_are_accessible(self):
        for address in [VRAM_START, IO_START]:
            with self.subTest(address=hex(address)):
                self.bus.write(address, 0x41)
                self.assertEqual(self.bus.read(address), 0x41)

    def test_reserved_area_is_blocked(self):
        for address in [RESERVED_START, 0x9FBFC]:
            with self.subTest(address=hex(address)):
                with self.assertRaises(ValueError):
                    self.bus.read(address)
                with self.assertRaises(ValueError):
                    self.bus.write(address, 1)
        self.assertIsNone(self.bus.control)

    def test_cpu_uses_the_bus(self):
        cpu = CPU(self.bus)
        cpu.write_register(1, 0x100)
        cpu.write_register(2, 5)
        cpu.execute(0x0020A023)
        self.assertEqual(self.bus.control, WRITE)
        self.assertEqual(self.bus.address, 0x100)
        self.assertEqual(self.bus.data, 5)

    def test_cpu_store_in_reserved_area(self):
        cpu = CPU(self.bus)
        cpu.write_register(1, RESERVED_START)
        with self.assertRaises(ValueError):
            cpu.execute(0x0020A023)
        self.assertEqual(cpu.pc, 0)


if __name__ == "__main__":
    unittest.main()
