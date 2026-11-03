from cpu import CPU


def main() -> None:
    cpu = CPU()
    cpu.write_register(1, 10)
    cpu.write_register(2, 3)

    print("Grupo 13: ADD e SUB")
    print(f"x1 = {cpu.read_register(1)}")
    print(f"x2 = {cpu.read_register(2)}")

    cpu.execute(0x002081B3)
    print(f"ADD x3, x1, x2 -> x3 = {cpu.read_register(3)}")
    print(f"PC = 0x{cpu.pc:08X}")

    cpu.execute(0x40208233)
    print(f"SUB x4, x1, x2 -> x4 = {cpu.read_register(4)}")
    print(f"PC = 0x{cpu.pc:08X}")


if __name__ == "__main__":
    main()
