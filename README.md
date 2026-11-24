# Simulador RISC-V RV32I

Projeto da disciplina de Organização de Computadores (Universidade Católica de Santos).
Simulador de um computador com CPU RV32I de ciclo único, memória RAM/VRAM, barramento e saída de vídeo no terminal.

Grupo 13: instrução especial **ORN**.

## Como executar

Precisa de Python 3.10 ou mais novo. Não usa nenhuma biblioteca externa.

```
python main.py
```

Para rodar os testes:

```
python -m unittest -v
```

## Estrutura

| Arquivo | Descrição |
|---|---|
| `cpu.py` | CPU: liga os módulos do datapath, ciclo de busca e tratamento de interrupções |
| `registers.py` | Banco de registradores |
| `alu.py` | ULA |
| `immediate.py` | Gerador de imediatos (Imm Gen) |
| `control.py` | Unidade de controle e controle da ULA |
| `memory.py` | Memória principal de `0xA0000` bytes, palavras de 32 bits em little-endian |
| `bus.py` | Barramento (linhas de endereço, dados, controle e interrupção) e mapa de memória |
| `devices.py` | Timer mapeado na região de E/S |
| `computer.py` | Junta CPU, barramento, memória e timer e mostra a VRAM no terminal a cada N instruções |
| `encoder.py` | Funções que geram o código de máquina de cada instrução (`addi(1, 0, 5)`, `orn(3, 1, 2)`, ...) |
| `program.py` | Programa de teste em RISC-V |
| `main.py` | Carrega o programa de teste e executa |
| `tests/` | Testes unitários |

## CPU

A CPU segue o processador de ciclo único: o PC aponta para um endereço, a instrução é buscada na memória pelo barramento, decodificada pelo `opcode`, `funct3` e `funct7`, executada na ULA e o PC é atualizado (`PC + 4` ou o destino do desvio).

São 32 registradores de 32 bits. O `x0` sempre vale zero, escritas nele são ignoradas.

### Módulos do datapath

A CPU é dividida nos mesmos blocos do processador de ciclo único (figura 5 do enunciado):

| Módulo | Classe | Função |
|---|---|---|
| Banco de registradores | `RegisterFile` | Lê `rs1`/`rs2` e escreve em `rd` |
| Unidade de controle | `ControlUnit.decode` | A partir do `opcode` gera os sinais `RegWrite`, `ALUSrc`, `MemRead`, `MemWrite`, `MemtoReg` e `Branch` |
| Controle da ULA | `ControlUnit.alu_operation` | A partir de `opcode`, `funct3` e `funct7` escolhe a operação da ULA |
| Imm Gen | `ImmediateGenerator` | Monta o imediato de cada formato (I, S, B) com extensão de sinal |
| ULA | `ALU` | Executa a operação |
| Memória de dados | `Bus` + `Memory` | Acessada quando `MemRead` ou `MemWrite` estão ativos |

Os multiplexadores da figura aparecem no `CPU.execute`: `ALUSrc` escolhe entre `rs2` e o imediato, `MemtoReg` escolhe entre o resultado da ULA e o valor lido da memória, e `Branch` junto com o resultado da ULA escolhe entre `PC + 4` e `PC + imediato`.

Nos desvios a ULA faz a comparação: `SUB` para BEQ/BNE (desvia se o resultado for ou não zero), `SLT` para BLT/BGE e `SLTU` para BLTU/BGEU.

### Instruções implementadas

| Tipo | Opcode | Instruções |
|---|---|---|
| R | `0110011` | ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND, **ORN** |
| I | `0010011` | ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI |
| I (load) | `0000011` | LW |
| S | `0100011` | SW |
| B | `1100011` | BEQ, BNE, BLT, BGE, BLTU, BGEU |
| Sistema | `1110011` | MRET (retorno de interrupção) |

Qualquer outra instrução gera erro e não altera registradores nem o PC.

No Tipo-I o segundo operando da ULA é o imediato com extensão de sinal. Como no Tipo-I os bits [31:25] fazem parte do imediato, o `funct7` só é considerado nos deslocamentos (SLLI, SRLI, SRAI). Assim um `ORI` com imediato grande não é confundido com a ORN.

### ORN (Grupo 13)

`ORN rd, rs1, rs2` faz `rd = rs1 OR (NOT rs2)`. É uma instrução da extensão Zbb e usa a mesma codificação oficial:

| funct7 | rs2 | rs1 | funct3 | rd | opcode |
|---|---|---|---|---|---|
| `0100000` | rs2 | rs1 | `110` | rd | `0110011` |

Ela tem o mesmo `funct3` do OR, mudando só o `funct7` (igual ao par ADD/SUB). Exemplo: `ORN x3, x1, x2` = `0x4020E1B3`.

## Memória e barramento

Mapa de memória:

| Faixa | Região |
|---|---|
| `0x00000` - `0x7FFFF` | RAM principal (programa, dados, pilha) |
| `0x80000` - `0x8FFFF` | VRAM |
| `0x90000` - `0x9FBFF` | Área reservada |
| `0x9FC00` - `0x9FFFF` | E/S mapeada |

Todo acesso da CPU à memória (busca de instrução, LW e SW) passa pelo barramento. Ele guarda o último valor de cada linha:

- **endereço**: posição acessada (32 bits)
- **dados**: valor lido ou escrito (32 bits)
- **controle**: `READ` ou `WRITE`
- **interrupção**: ligada por um dispositivo quando ele pede interrupção

Acessos à área reservada são bloqueados pelo barramento. Endereços precisam ser múltiplos de 4.

Dispositivos são conectados ao barramento em um endereço da região de E/S (`Bus.attach`). Quando a CPU lê ou escreve nesse endereço, o barramento repassa o acesso para o dispositivo em vez da memória.

## Interrupções

O ciclo segue a figura 7 do enunciado: buscar instrução, executar e, se as interrupções estiverem habilitadas, verificar se há interrupção pendente.

Quando a linha de interrupção do barramento está ativa:

1. A CPU confirma a interrupção (limpa a linha).
2. Guarda o PC atual em `epc`.
3. Desvia para o tratador em `0x7F000`, um trecho pré-definido da RAM.
4. Desabilita novas interrupções enquanto o tratador executa.

O tratador termina com `MRET` (`0x30200073`), que volta para o endereço guardado em `epc` e habilita as interrupções de novo. Uma interrupção que chegar durante o tratador fica pendente e é atendida logo depois do `MRET`.

### Timer (interrupção programada)

O timer fica no endereço `0x9FC00` (início da região de E/S). O programa escreve nesse endereço com `SW` quantas instruções devem passar entre uma interrupção e outra. A cada instrução o timer conta um ciclo e, ao chegar no intervalo, liga a linha de interrupção do barramento. Com o valor 0 ele fica desligado.

## Saída de vídeo (E/S programada)

O programa escreve caracteres ASCII na VRAM usando `SW`. A cada `N` instruções executadas (`VRAM_INTERVAL` no `main.py`, padrão 20), o `Computer` lê a VRAM pelo barramento e mostra o texto no terminal até encontrar um byte zero. Caracteres não imprimíveis aparecem como `?`.

## Programa de teste

O programa em `program.py` usa todos os tipos de instrução:

0. Monta o endereço `0x9FC00` com `ADDI` e `SLLI` e programa o timer para gerar uma interrupção a cada 25 instruções.
1. Soma de 1 a 10 com um laço (`ADDI`, `ADD`, `BLT`) e guarda o resultado (55) na RAM em `0x300` com `SW`.
2. Calcula `ORN 0x000000F0, 0xFFFFFF00`, que deve dar `0x000000FF`. Com um `BEQ` escolhe a mensagem de "ORN OK" ou "ORN ERRO".
3. Monta o endereço da VRAM com `ADDI` e `SLLI` e copia a mensagem da RAM para a VRAM palavra por palavra (`LW`, `SW`, `BNE`).

Enquanto isso o timer interrompe o programa. O tratador de interrupção salva o `x28` na memória, soma 1 no contador de interrupções em `0x304`, restaura o `x28` e volta com `MRET`.

Saída esperada (resumida):

```
[VRAM após 80 instruções]
Grupo 13 - Simul
[VRAM após 100 instruções]
Grupo 13 - Simulador RISC-V
[VRAM após 120 instruções]
Grupo 13 - Simulador RISC-V
ORN OK

Instruções executadas: 120
Soma de 1 a 10 (MEM[0x300]) = 55
ORN 0x000000F0, 0xFFFFFF00 = 0x000000FF
Interrupções tratadas (MEM[0x304]) = 4
```

São 96 instruções do programa principal mais 4 interrupções de 6 instruções cada.

A execução termina quando o PC aponta para uma palavra zerada (fim do programa) ou depois de 10000 instruções.

## Limitações

- Só acessos de palavra (LW/SW) alinhados em 4 bytes.
- Sem LUI, AUIPC, JAL, JALR, ECALL e EBREAK (não fazem parte do que foi pedido).
- Um único tratador de interrupção, sem identificar a causa.
- Sem cache.
