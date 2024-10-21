import cocotb
from cocotb.triggers import Timer

# Helper function to display results for debugging
def display_result(operation, dut):
    a = dut.ui_in.value & 0x3F  # Extract lower 6 bits for a
    b = dut.uio_in.value & 0x3F  # Extract lower 6 bits for b
    control = ((dut.ui_in.value >> 6) & 0x3) << 2 | ((dut.uio_in.value >> 6) & 0x3)  # Combine upper 2 bits of ui_in and uio_in to form control
    result = dut.uo_out.value & 0x3F  # Extract lower 6 bits for the result
    carry = (dut.uo_out.value >> 6) & 0x1  # Carry bit is the 7th bit
    zero = (dut.uo_out.value >> 7) & 0x1  # Zero flag is the 8th bit
    print(f"Operation: {operation}")
    print(f"a = {a}, b = {b}, control = {control}, result = {result}, carry = {carry}, zero = {zero}\n")

@cocotb.test()
async def test_alu(dut):
    """Test ALU operations: AND, OR, ADD, SUB, XOR"""
    # AND = 4'b0000,
    # OR  = 4'b0001,
    # ADD = 4'b0010,
    # SUB = 4'b0110,
    # XOR = 4'b0100,
    # SLL = 4'b0011,  // Shift Left Logical
    # SRL = 4'b0110,  // Shift Right Logical
    # SRA = 4'b0111,  // Shift Right Arithmatic
    # SLT = 4'b1000;  // Set Less Than Signed

    # Set a small delay
    delay_ns = 50

    # Test AND operation 0000
    dut.ui_in.value  = 0b00000010  # a = 2, control upper = 00
    dut.uio_in.value = 0b00000010  # b = 2, control lower = 00
    await Timer(delay_ns, units='ns')
    display_result("AND", dut)
    assert dut.uo_out.value == 0b00000010, f"AND failed, expected 0b00000010, got {dut.uo_out.value}"

    # Test OR operation 0001
    dut.ui_in.value  = 0b00001100  # a = 12, control upper = 00
    dut.uio_in.value = 0b01000010  # b = 2,  control lower = 01
    await Timer(delay_ns, units='ns')
    display_result("OR", dut)
    assert dut.uo_out.value == 0b00001110, f"OR failed, expected 0b00001110, got {dut.uo_out.value}"

    # Test ADD operation 0010
    dut.ui_in.value  = 0b00000011  # a = 3, control upper = 00
    dut.uio_in.value = 0b10000101  # b = 5, control lower = 10
    await Timer(delay_ns, units='ns')
    display_result("ADD", dut)
    assert dut.uo_out.value == 0b00001000, f"ADD failed, expected 0b00001000, got {dut.uo_out.value}"

    # Test SUB operation 0110
    dut.ui_in.value  = 0b01000010  # a = 2, control upper = 01
    dut.uio_in.value = 0b10010001  # b = 1, control lower = 10
    await Timer(delay_ns, units='ns')
    display_result("SUB", dut)
    assert dut.uo_out.value == 0b00000001, f"SUB failed, expected 0b00000001, got {dut.uo_out.value}"

    # Test XOR operation 0100
    dut.ui_in.value  = 0b01001100  # a = 12, control upper = 01
    dut.uio_in.value = 0b00000010  # b = 2,  control lower = 00
    await Timer(delay_ns, units='ns')
    display_result("XOR", dut)
    assert dut.uo_out.value == 0b00001110, f"XOR failed, expected 0b00000110, got {dut.uo_out.value}"

    # Check the result for any failure
    print("All tests passed!")
