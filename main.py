from computer import Computer
from program import SUM_ADDRESS, load_test_program

VRAM_INTERVAL = 20


def main() -> None:
    computer = Computer(vram_interval=VRAM_INTERVAL)
    load_test_program(computer)

    print("Grupo 13: Simulador RISC-V RV32I + ORN")
    print(f"VRAM exibida a cada {VRAM_INTERVAL} instruções")
    print()

    steps = computer.run()

    print()
    print(f"Instruções executadas: {steps}")
    print(f"Soma de 1 a 10 (MEM[0x{SUM_ADDRESS:X}]) = {computer.memory.read_word(SUM_ADDRESS)}")
    print(f"ORN 0x{computer.cpu.read_register(10):08X}, 0x{computer.cpu.read_register(11):08X} = 0x{computer.cpu.read_register(12):08X}")
    print(f"PC = 0x{computer.cpu.pc:08X}")


if __name__ == "__main__":
    main()
