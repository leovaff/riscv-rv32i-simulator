from alu import ALU
from bus import Bus
from control import ControlUnit
from immediate import ImmediateGenerator
from registers import RegisterFile

MASK_32 = 0xFFFFFFFF
MRET = 0x30200073
INTERRUPT_HANDLER = 0x7F000


class CPU:
    def __init__(self, bus: Bus | None = None):
        self.pc = 0x00000
        self.bus = bus if bus is not None else Bus()
        self.memory = self.bus.memory
        self.register_file = RegisterFile()
        self.control_unit = ControlUnit()
        self.immediate_generator = ImmediateGenerator()
        self.alu = ALU()
        self.interrupts_enabled = True
        self.epc = 0

    @property
    def registers(self) -> list[int]:
        return self.register_file.values

    def read_register(self, reg_num: int) -> int:
        return self.register_file.read(reg_num)

    def write_register(self, reg_num: int, value: int) -> None:
        self.register_file.write(reg_num, value)

    @staticmethod
    def _branch_taken(funct3: int, alu_result: int) -> bool:
        zero = alu_result == 0
        if funct3 in (0x0, 0x5, 0x7):
            return zero
        return not zero

    def execute(self, instruction: int) -> None:
        if not 0 <= instruction <= MASK_32:
            raise ValueError("A instrução deve ser uma palavra de 32 bits.")

        if instruction == MRET:
            self.pc = self.epc
            self.interrupts_enabled = True
            return

        opcode = instruction & 0x7F
        rd = (instruction >> 7) & 0x1F
        funct3 = (instruction >> 12) & 0x7
        rs1 = (instruction >> 15) & 0x1F
        rs2 = (instruction >> 20) & 0x1F
        funct7 = (instruction >> 25) & 0x7F

        control = self.control_unit.decode(opcode)
        operation = self.control_unit.alu_operation(opcode, funct3, funct7)
        imm = self.immediate_generator.generate(instruction)

        val_rs1 = self.register_file.read(rs1)
        val_rs2 = self.register_file.read(rs2)
        alu_input = imm & MASK_32 if control.alu_src else val_rs2
        alu_result = self.alu.execute(operation, val_rs1, alu_input)

        next_pc = self.pc + 4
        if control.branch and self._branch_taken(funct3, alu_result):
            next_pc = self.pc + imm

        write_data = alu_result
        if control.mem_read:
            write_data = self.bus.read(alu_result)
        if control.mem_write:
            self.bus.write(alu_result, val_rs2)
        if control.reg_write:
            self.register_file.write(rd, write_data)

        self.pc = next_pc & MASK_32

    def check_interrupt(self) -> bool:
        if not self.interrupts_enabled or not self.bus.interrupt:
            return False

        self.bus.acknowledge_interrupt()
        self.epc = self.pc
        self.pc = INTERRUPT_HANDLER
        self.interrupts_enabled = False
        return True

    def step(self) -> None:
        instruction = self.bus.read(self.pc)
        self.execute(instruction)
        self.check_interrupt()

    def run(self, max_steps: int = 1000) -> int:
        steps = 0
        while steps < max_steps and self.bus.read(self.pc) != 0:
            self.step()
            steps += 1
        return steps
