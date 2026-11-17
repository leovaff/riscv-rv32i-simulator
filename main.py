from cpu import CPU


def main() -> None:
    cpu = CPU()
    cpu.write_register(1, 10)
    cpu.write_register(2, 3)

    print("Grupo 13: instruções Tipo-R, Tipo-I + ORN")
    print(f"x1 = {cpu.read_register(1)}")
    print(f"x2 = {cpu.read_register(2)}")

    instructions = [
        ("ADD ", 0x002081B3),
        ("SUB ", 0x402081B3),
        ("SLL ", 0x002091B3),
        ("SLT ", 0x0020A1B3),
        ("SLTU", 0x0020B1B3),
        ("XOR ", 0x0020C1B3),
        ("SRL ", 0x0020D1B3),
        ("SRA ", 0x4020D1B3),
        ("OR  ", 0x0020E1B3),
        ("AND ", 0x0020F1B3),
        ("ORN ", 0x4020E1B3),
    ]

    for name, instruction in instructions:
        cpu.execute(instruction)
        print(f"{name} x3, x1, x2 -> x3 = 0x{cpu.read_register(3):08X}  PC = 0x{cpu.pc:08X}")

    immediate_instructions = [
        ("ADDI ", "-1", 0xFFF08193),
        ("SLTI ", "5", 0x0050A193),
        ("SLTIU", "5", 0x0050B193),
        ("XORI ", "15", 0x00F0C193),
        ("ORI  ", "15", 0x00F0E193),
        ("ANDI ", "15", 0x00F0F193),
        ("SLLI ", "2", 0x00209193),
        ("SRLI ", "2", 0x0020D193),
        ("SRAI ", "2", 0x4020D193),
    ]

    for name, imm, instruction in immediate_instructions:
        cpu.execute(instruction)
        print(f"{name} x3, x1, {imm:>2} -> x3 = 0x{cpu.read_register(3):08X}  PC = 0x{cpu.pc:08X}")

    print()
    print("Programa na memória: soma de 1 a 5")

    program = [
        0x00000093,
        0x00100113,
        0x00600193,
        0x002080B3,
        0x00110113,
        0xFE314CE3,
        0x10102023,
        0x10002203,
        0x404062B3,
    ]

    cpu = CPU()
    cpu.memory.load_program(program)
    steps = cpu.run()

    print(f"Instruções executadas: {steps}")
    print(f"x1 (soma) = {cpu.read_register(1)}")
    print(f"MEM[0x100] = {cpu.memory.read_word(0x100)}")
    print(f"x4 (LW) = {cpu.read_register(4)}")
    print(f"x5 (ORN x0, x4) = 0x{cpu.read_register(5):08X}")
    print(f"PC = 0x{cpu.pc:08X}")


if __name__ == "__main__":
    main()
