module sample(
    input clk,
    input reset,
    input [7:0] data_in,
    input enable,
    output reg [7:0] reg_ungated,
    output reg [7:0] reg_gated
   
);
reg [7:0] internal_counter;
wire [3:0] status;
reg flag;
// Register WITHOUT clock gating — your tool should fix this
always @(posedge clk) begin
    if (enable) begin
        reg_ungated <= data_in;
    end

end

// Register WITH clock gating — your tool should leave this alone
always @(posedge clk) begin
    if (enable) begin
        reg_gated <= data_in;
    end
end



endmodule