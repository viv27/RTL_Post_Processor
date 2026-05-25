module complex_sample(
    input clk,
    input reset,
    input [7:0] data_in,
    input [7:0] data_in2,
    input enable,
    output reg [7:0] reg_a,
    output reg [7:0] reg_b,
    output reg [7:0] reg_c
);

// Ungated register 1
clock_gate cg1(.clk(clk), .enable(enable), .gated_clk(gated_clk1));

always @(posedge gated_clk1) begin
    reg_a <= data_in;
end

// Ungated register 2
clock_gate cg2(.clk(clk), .enable(enable), .gated_clk(gated_clk2));

always @(posedge gated_clk2) begin
    reg_b <= data_in2;
end

// Gated register — leave alone
always @(posedge clk) begin
    if (enable) begin
        reg_c <= data_in;
    end
end

endmodule