import cocotb
from cocotb.triggers import Timer
import random

# ALU Control Signal Type
# AND = 4'b0000
# OR  = 4'b0001
# ADD = 4'b0010
# SUB = 4'b0110
# XOR = 4'b0100
# SLL = 4'b0011  # Shift Left Logical
# SRL = 4'b0101  # Shift Right Logical
# SRA = 4'b0111  # Shift Right Arithmetic
# SLT = 4'b1000  # Set Less Than Signed

# Helper function to compute expected result
def compute_expected_result(control, a, b):
    # Ensure operands are 6 bits
    a = a & 0x3F
    b = b & 0x3F

    # Initialize result, carry, zero
    result = 0
    carry = 0
    zero = 0

    if control == 0b0000:  # AND
        result = a & b
    elif control == 0b0001:  # OR
        result = a | b
    elif control == 0b0010:  # ADD
        sum_ = a + b
        result = sum_ & 0x3F
        carry = (sum_ >> 6) & 0x1  # 7th bit is carry
    elif control == 0b0110:  # SUB
        dif = (a - b) & 0x7F  # 7 bits to capture sign
        result = dif & 0x3F
        carry = (dif >> 6) & 0x1  # Carry out
    elif control == 0b0100:  # XOR
        result = a ^ b
    elif control == 0b0011:  # SLL
        shift_amount = b & 0x07  # 3 bits for shift amount
        result = (a << shift_amount) & 0x3F  # Mask to 6 bits
    elif control == 0b0101:  # SRL
        shift_amount = b & 0x07  # 3 bits for shift amount
        result = (a >> shift_amount) & 0x3F
    # elif control == 0b0111:  # SRA
    #     shift_amount = b & 0x07  # 3 bits for shift amount
    #     # Sign-extend a to an integer
    #     a_signed = a if a < 32 else a - 64  # Since 6 bits
    #     result_signed = a_signed >> shift_amount
    #     result = result_signed & 0x3F  # Mask to 6 bits
    elif control == 0b0111:  # SRA
        shift_amount = b & 0x3F  # 取低6位作为移位量
        # 对a进行符号扩展
        if (a & 0x20) == 0:
            a_signed = a  # 正数
        else:
            a_signed = a - 64  # 负数，进行符号扩展

        # 执行算术右移
        result_signed = a_signed >> shift_amount

        # 将结果转换回6位二进制表示
        if result_signed < 0:
            result = (result_signed + 64) & 0x3F  # 处理负数情况
        else:
            result = result_signed & 0x3F  # 处理正数情况
    elif control == 0b1000:  # SLT
        # Signed comparison
        a_signed = a if a < 32 else a - 64
        b_signed = b if b < 32 else b - 64
        result = 1 if a_signed < b_signed else 0
    else:
        result = 0

    zero = 1 if result == 0 else 0

    return result, carry, zero

# Helper function to display results for debugging
def signed_6bit(val):
    val = val & 0x3F  # 确保只取低6位
    if val & 0x20:
        return val - 64  # 处理负数
    else:
        return val  # 正数

def display_result(operation, dut, expected_result, expected_carry, expected_zero):
    a_unsigned = dut.ui_in.value.integer & 0x3F  # 提取操作数a的低6位
    b_unsigned = dut.uio_in.value.integer & 0x3F  # 提取操作数b的低6位
    control = ((dut.ui_in.value.integer >> 6) & 0x3) << 2 | ((dut.uio_in.value.integer >> 6) & 0x3)  # 组合控制信号
    result_unsigned = dut.uo_out.value.integer & 0x3F  # 提取结果的低6位
    carry = (dut.uo_out.value.integer >> 6) & 0x1  # 第7位为进位标志
    zero = (dut.uo_out.value.integer >> 7) & 0x1  # 第8位为零标志

    # 将无符号数转换为有符号数
    a_signed = signed_6bit(a_unsigned)
    b_signed = signed_6bit(b_unsigned)
    result_signed = signed_6bit(result_unsigned)
    expected_result_signed = signed_6bit(expected_result)

    print(f"Operation: {operation}")
    print(f"a = {a_unsigned} ({a_unsigned:06b}), signed: {a_signed}")
    print(f"b = {b_unsigned} ({b_unsigned:06b}), signed: {b_signed}")
    print(f"control = {control:04b}")
    print(f"Expected result = {expected_result} ({expected_result:06b}), signed: {expected_result_signed}, carry = {expected_carry}, zero = {expected_zero}")
    print(f"DUT result = {result_unsigned} ({result_unsigned:06b}), signed: {result_signed}, carry = {carry}, zero = {zero}\n")


# Function to test a specific operation
async def test_operation(dut, operation_name, control_code, test_cases, delay_ns=50):
    for a_val, b_val in test_cases:
        # Set the control code
        control_upper = (control_code >> 2) & 0b11  # upper 2 bits
        control_lower = control_code & 0b11         # lower 2 bits

        # Set ui_in and uio_in
        ui_in_value = ((control_upper << 6) | (a_val & 0x3F))
        uio_in_value = ((control_lower << 6) | (b_val & 0x3F))

        dut.ui_in.value = ui_in_value
        dut.uio_in.value = uio_in_value

        await Timer(delay_ns, units='ns')

        # Compute expected result
        expected_result, expected_carry, expected_zero = compute_expected_result(control_code, a_val, b_val)

        # Get outputs from dut
        uo_out_value = dut.uo_out.value.integer
        result = uo_out_value & 0x3F
        carry = (uo_out_value >> 6) & 0x1
        zero = (uo_out_value >> 7) & 0x1

        # Display results
        display_result(operation_name, dut, expected_result, expected_carry, expected_zero)

        # Check results
        assert result == expected_result, f"{operation_name} failed for a={a_val}, b={b_val}. Expected result {expected_result}, got {result}"
        assert carry == expected_carry, f"{operation_name} carry mismatch for a={a_val}, b={b_val}. Expected carry {expected_carry}, got {carry}"
        assert zero == expected_zero, f"{operation_name} zero flag mismatch for a={a_val}, b={b_val}. Expected zero {expected_zero}, got {zero}"

@cocotb.test()
async def test_tt_um_alu(dut):
    """Test ALU operations with corner cases and random values"""

    delay_ns = 50

    # Control codes
    AND = 0b0000
    OR  = 0b0001
    ADD = 0b0010
    SUB = 0b0110
    XOR = 0b0100
    SLL = 0b0011
    SRL = 0b0101
    SRA = 0b0111
    SLT = 0b1000

    # Test cases for each operation

    # AND operation
    and_test_cases = [
        (0, 0),
        (0x3F, 0x3F),  # max values
        (0x15, 0x2A),
        (0x0F, 0x3C),
    ]
    # Random test cases
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        and_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "AND", AND, and_test_cases, delay_ns)

    # OR operation
    or_test_cases = [
        (0, 0),
        (0x3F, 0x3F),
        (0x15, 0x2A),
        (0x0F, 0x30),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        or_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "OR", OR, or_test_cases, delay_ns)

    # ADD operation
    add_test_cases = [
        (0, 0),
        (0x3F, 0x01),  # Overflow case
        (0x1E, 0x01),
        (0x0F, 0x0F),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        add_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "ADD", ADD, add_test_cases, delay_ns)

    # SUB operation
    sub_test_cases = [
        (0, 0),
        (0x00, 0x01),  # Underflow case
        (0x3F, 0x3F),
        (0x10, 0x0F),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        sub_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "SUB", SUB, sub_test_cases, delay_ns)

    # XOR operation
    xor_test_cases = [
        (0, 0),
        (0x3F, 0x3F),
        (0x15, 0x2A),
        (0x0F, 0x30),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        xor_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "XOR", XOR, xor_test_cases, delay_ns)

    # SLL operation
    sll_test_cases = [
        (0x01, 0x00),  # Shift by 0
        (0x01, 0x03),  # Shift left by 3
        (0x3F, 0x01),  # Overflow case
        (0x15, 0x02),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x07)  # Shift amount up to 6
        sll_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "SLL", SLL, sll_test_cases, delay_ns)

    # SRL operation
    srl_test_cases = [
        (0x20, 0x00),  # Shift by 0
        (0x20, 0x03),  # Shift right by 3
        (0x01, 0x01),
        (0x3F, 0x02),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x06)
        srl_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "SRL", SRL, srl_test_cases, delay_ns)

    # SRA operation
    sra_test_cases = [
        (0x20, 0x00),  # Shift by 0
        (0x20, 0x03),  # Shift right arithmetic by 3
        (0x3F, 0x01),  # Negative number
        (0x10, 0x02),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x06)
        sra_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "SRA", SRA, sra_test_cases, delay_ns)

    # SLT operation
    slt_test_cases = [
        (0x00, 0x00),
        (0x1F, 0x1F),
        (0x1F, 0x20),
        (0x20, 0x1F),
        (0x3F, 0x00),
        (0x00, 0x3F),
    ]
    for _ in range(10):
        a_rand = random.randint(0, 0x3F)
        b_rand = random.randint(0, 0x3F)
        slt_test_cases.append((a_rand, b_rand))

    await test_operation(dut, "SLT", SLT, slt_test_cases, delay_ns)

    print("All tests passed!")
