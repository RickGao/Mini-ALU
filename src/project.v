/*
 * Copyright (c) 2024 RickGao
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none


// Define Width with Marco
`ifndef WIDTH
`define WIDTH 6
`endif


module tt_um_alu (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    // Bidirectional Pins All Input
    assign uio_oe[7:0]  = 8'b00000000;

    // All output pins must be assigned. If not used, assign to 0.
    assign uio_out = 0;  // Not Used

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, clk, rst_n, 1'b0};


    wire [3:0]        control;    // Control Signal
    wire [`WIDTH-1:0] a;          // Operand A
    wire [`WIDTH-1:0] b;          // Operand B
    wire [`WIDTH-1:0] out;        // Output
    wire              carry;       // Carry Out
    wire              zero;        // Zero Flag


    assign a[5:0] = ui_in[5:0];        // Lower 6 bits of IN is Operand A
    assign b[5:0] = uio_in[5:0];       // Lower 6 bits of IO is Operand B
    assign control[3:2] = ui_in[7:6];  // Upper 2 bits of IN is Control[3:2]
    assign control[1:0] = uio_in[7:6]; // Upper 2 bits of IO is Control[1:0]


    // ALU Control Signal Type
    localparam [3:0] 
        AND  = 4'b0000,
        OR   = 4'b0001,
        ADD  = 4'b0010,
        SUB  = 4'b0110,
        XOR  = 4'b0100,
        SLL  = 4'b0011,  // Shift Left Logical
        SRL  = 4'b0110,  // Shift Right Logical
        SRA  = 4'b0111,  // Shift Right Arithmatic
        SLT  = 4'b1000;  // Set Less Than Signed

    wire [`WIDTH:0] sum;
    wire [`WIDTH:0] dif;

    assign sum = {1'b0, a} + {1'b0, b};
    assign dif = {1'b0, a} - {1'b0, b};
    
    // Assign outputs based on the control signal
    assign out =    (control == AND) ? (a & b) :
                    (control == OR)  ? (a | b) :
                    (control == ADD) ? sum[`WIDTH-1:0] :
                    (control == SUB) ? dif[`WIDTH-1:0] :
                    (control == XOR) ? (a ^ b) :
                    (control == SLL) ? (a << b[$clog2(`WIDTH)-1:0]) :
                    (control == SRL) ? (a >> b[$clog2(`WIDTH)-1:0]) :
                    (control == SRA) ? (a >>> b[$clog2(`WIDTH)-1:0]) :
                    (control == SLT) ? (($signed(a) < $signed(b)) ? {{(`WIDTH-1){1'b0}}, 1'b1} : {`WIDTH{1'b0}}) :
                    {`WIDTH{1'b0}};  // Default output is 0

    // Assign carry out for ADD and SUB operations
    assign carry =  (control == ADD) ? sum[`WIDTH] :
                    (control == SUB) ? dif[`WIDTH] :
                    1'b0;  // No carry for other operations

    // Zero Flag
    assign zero = (out == {`WIDTH{1'b0}});

    assign uo_out[5:0] = out[5:0];
    assign uo_out[6]   = carry;
    assign uo_out[7]   = zero;

endmodule
