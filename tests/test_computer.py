import unittest

from bus import VRAM_START
from computer import Computer
from encoder import addi, slli, sw
from devices import TIMER_ADDRESS
from program import INTERRUPT_COUNT_ADDRESS, MESSAGE_OK, SUM_ADDRESS, TIMER_INTERVAL, load_test_program


class ComputerTest(unittest.TestCase):
    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            Computer(vram_interval=0)

    def test_empty_vram(self):
        self.assertEqual(Computer().read_vram(), "")

    def test_read_vram(self):
        computer = Computer()
        computer.memory.write_word(VRAM_START, 0x41424344)
        computer.memory.write_word(VRAM_START + 4, 0x00000A45)
        self.assertEqual(computer.read_vram(), "DCBAE\n")

    def test_non_printable_characters(self):
        computer = Computer()
        computer.memory.write_word(VRAM_START, 0x00410141)
        self.assertEqual(computer.read_vram(), "A?A")

    def test_vram_is_shown_every_interval(self):
        computer = Computer(vram_interval=2)
        computer.load([
            addi(1, 0, 0x48),
            addi(2, 0, 1),
            slli(2, 2, 19),
            sw(1, 2, 0),
            addi(3, 0, 0),
        ])
        lines = []
        steps = computer.run(output=lines.append)
        self.assertEqual(steps, 5)
        self.assertEqual(lines, [
            "[VRAM após 2 instruções]", "",
            "[VRAM após 4 instruções]", "H",
            "[VRAM após 5 instruções]", "H",
        ])

    def test_test_program(self):
        computer = Computer(vram_interval=1000)
        load_test_program(computer)
        lines = []
        steps = computer.run(output=lines.append)
        self.assertEqual(computer.memory.read_word(SUM_ADDRESS), 55)
        self.assertEqual(computer.cpu.read_register(12), 0xFF)
        self.assertEqual(computer.read_vram(), MESSAGE_OK)
        self.assertEqual(lines[-1], MESSAGE_OK.rstrip("\n"))
        self.assertEqual(computer.memory.read_word(INTERRUPT_COUNT_ADDRESS), 4)
        self.assertEqual(steps, 96 + 4 * 6)

    def test_interrupt_handler_preserves_register(self):
        computer = Computer(vram_interval=1000)
        load_test_program(computer)
        computer.cpu.write_register(28, 1234)
        computer.run(output=lambda line: None)
        self.assertEqual(computer.cpu.read_register(28), 1234)

    def test_timer_is_programmed_by_the_program(self):
        computer = Computer(vram_interval=1000)
        load_test_program(computer)
        computer.run(output=lambda line: None)
        self.assertEqual(computer.timer.interval, TIMER_INTERVAL)
        self.assertEqual(computer.bus.read(TIMER_ADDRESS), TIMER_INTERVAL)


if __name__ == "__main__":
    unittest.main()
