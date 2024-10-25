# 6-Bit ALU Documentation

## Introduction

This project implements a simple 6-bit **Arithmetic Logic Unit (ALU)** designed in Verilog HDL. The ALU performs basic arithmetic and logical operations, including addition, subtraction, shifting, and comparisons. It is configurable with a default width of 6 bits and is suitable for both educational purposes and small-scale digital designs.

---

## Features

- **6-bit Configurable ALU**: The width is set to 6 bits by default.
- **Supported Operations**:
  - AND, OR, XOR
  - Addition (ADD), Subtraction (SUB)
  - Logical Shifts (SLL, SRL), Arithmetic Shift Right (SRA)
  - Set Less Than (SLT)
- **Zero and Carry Flags** for status checking.
- **Tiny Tapeout Compatible**: Designed for use with the Tiny Tapeout flow.

---

## Supported Operations

| Control Code | Operation                     |
|--------------|-------------------------------|
| `0000`       | AND                           |
| `0001`       | OR                            |
| `0010`       | ADD                           |
| `0011`       | SLL (Shift Left Logical)      |
| `0100`       | XOR                           |
| `0101`       | SRL (Shift Right Logical)     |
| `0110`       | SUB                           |
| `0111`       | SRA (Shift Right Arithmetic)  |
| `1000`       | SLT (Set Less Than)           |

---

## How It Works

1. **Operands**: The ALU accepts two 6-bit inputs (`A` and `B`).
2. **Control Signal**: A 4-bit control signal determines the operation (AND, OR, ADD, etc.).
3. **Outputs**: The 6-bit result of the operation is outputted, along with the carry and zero flags.

---

## How to Test

Test using the **Tiny Tapeout flow**. Follow the standard process outlined in the [Tiny Tapeout Guide](https://tinytapeout.com/).

---

## External Hardware

No external hardware is required for this ALU design. It is self-contained and can be tested and prepared for tapeout using the Tiny Tapeout flow.

---

## Conclusion

This 6-bit ALU is a flexible and simple design that supports key arithmetic and logic operations. It is compatible with the Tiny Tapeout flow, making it an ideal candidate for tapeout in educational and hobbyist contexts. You can simulate, test, and submit the design for fabrication using the Tiny Tapeout process.

---

For more information on using Tiny Tapeout, visit [Tiny Tapeout's official website](https://tinytapeout.com/).
