module clock_gate(
    input clk,
    input enable,
    output gated_clk
);
    reg enable_latched;
    always @(clk or enable) begin
        if (!clk) begin
            enable_latched <= enable;
        end
    end
    assign gated_clk = clk & enable_latched;
endmodule