class RegisterFile:
    def __init__(self):
        self.values = [0] * 32

    @staticmethod
    def _validate(reg_num: int) -> None:
        if not 0 <= reg_num < 32:
            raise ValueError("O registrador deve estar entre x0 e x31.")

    def read(self, reg_num: int) -> int:
        self._validate(reg_num)
        if reg_num == 0:
            return 0
        return self.values[reg_num]

    def write(self, reg_num: int, value: int) -> None:
        self._validate(reg_num)
        if reg_num != 0:
            self.values[reg_num] = value & 0xFFFFFFFF
