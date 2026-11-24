from bus import IO_START, Bus

TIMER_ADDRESS = IO_START


class Timer:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.interval = 0
        self.counter = 0

    def read(self) -> int:
        return self.interval

    def write(self, value: int) -> None:
        self.interval = value
        self.counter = 0

    def tick(self) -> None:
        if self.interval == 0:
            return

        self.counter += 1
        if self.counter >= self.interval:
            self.counter = 0
            self.bus.request_interrupt()
