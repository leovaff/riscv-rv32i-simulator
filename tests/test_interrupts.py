import unittest

from bus import IO_START, Bus
from cpu import INTERRUPT_HANDLER, MRET, CPU
from devices import TIMER_ADDRESS, Timer
from encoder import addi


class TimerTest(unittest.TestCase):
    def setUp(self):
        self.bus = Bus()
        self.timer = Timer(self.bus)
        self.bus.attach(TIMER_ADDRESS, self.timer)

    def test_disabled_by_default(self):
        for _ in range(100):
            self.timer.tick()
        self.assertFalse(self.bus.interrupt)

    def test_programmed_through_the_bus(self):
        self.bus.write(TIMER_ADDRESS, 3)
        self.assertEqual(self.timer.interval, 3)
        self.assertEqual(self.bus.read(TIMER_ADDRESS), 3)
        self.assertEqual(self.bus.memory.read_word(TIMER_ADDRESS), 0)

    def test_requests_interrupt_after_interval(self):
        self.bus.write(TIMER_ADDRESS, 3)
        self.timer.tick()
        self.timer.tick()
        self.assertFalse(self.bus.interrupt)
        self.timer.tick()
        self.assertTrue(self.bus.interrupt)

    def test_device_outside_io_region(self):
        with self.assertRaises(ValueError):
            self.bus.attach(IO_START - 4, self.timer)


class InterruptTest(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()
        self.cpu.memory.load_program([addi(1, 0, 1), addi(2, 0, 2), addi(3, 0, 3)])
        self.cpu.memory.load_program([addi(10, 0, 7), MRET], INTERRUPT_HANDLER)

    def test_no_interrupt(self):
        self.assertFalse(self.cpu.check_interrupt())
        self.assertEqual(self.cpu.pc, 0)

    def test_interrupt_jumps_to_handler(self):
        self.cpu.step()
        self.cpu.bus.request_interrupt()
        self.cpu.step()
        self.assertEqual(self.cpu.pc, INTERRUPT_HANDLER)
        self.assertEqual(self.cpu.epc, 8)
        self.assertFalse(self.cpu.interrupts_enabled)
        self.assertFalse(self.cpu.bus.interrupt)

    def test_mret_returns_to_program(self):
        self.cpu.step()
        self.cpu.bus.request_interrupt()
        self.cpu.step()
        self.cpu.step()
        self.cpu.step()
        self.assertEqual(self.cpu.read_register(10), 7)
        self.assertEqual(self.cpu.pc, 8)
        self.assertTrue(self.cpu.interrupts_enabled)
        self.cpu.step()
        self.assertEqual(self.cpu.read_register(3), 3)

    def test_interrupt_waits_while_disabled(self):
        self.cpu.interrupts_enabled = False
        self.cpu.bus.request_interrupt()
        self.cpu.step()
        self.assertEqual(self.cpu.pc, 4)
        self.assertTrue(self.cpu.bus.interrupt)
        self.cpu.interrupts_enabled = True
        self.cpu.step()
        self.assertEqual(self.cpu.pc, INTERRUPT_HANDLER)
        self.assertEqual(self.cpu.epc, 8)

    def test_interrupt_during_handler_is_handled_after_mret(self):
        self.cpu.bus.request_interrupt()
        self.cpu.step()
        self.cpu.bus.request_interrupt()
        self.cpu.step()
        self.assertEqual(self.cpu.pc, INTERRUPT_HANDLER + 4)
        self.cpu.step()
        self.assertEqual(self.cpu.pc, INTERRUPT_HANDLER)
        self.assertEqual(self.cpu.epc, 4)

    def test_other_system_instructions_are_not_implemented(self):
        for instruction in [0x00000073, 0x00100073]:
            with self.subTest(instruction=hex(instruction)):
                with self.assertRaises(ValueError):
                    self.cpu.execute(instruction)


if __name__ == "__main__":
    unittest.main()
