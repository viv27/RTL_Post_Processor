# Verilog RTL Post-Processor

A Python-based static analysis tool that parses Verilog source files, detects registers without clock enables, and automatically inserts latch-based clock gating cells — generating modified Verilog with gated clocks to reduce dynamic power consumption.

## What This Is

In digital design, every register consumes power on every clock edge — even when its value isn't changing. Clock gating solves this by physically blocking the clock signal to registers that don't need to update, reducing switching activity and saving power.

This tool automates that process:
1. Parse a Verilog file — extract module name, ports, and signal definitions
2. Detect all `always @(posedge clk)` blocks without clock enables
3. Insert a latch-based clock gating cell before each ungated register
4. Output modified Verilog with gated clocks and a JSON analysis report

## Project Structure

```
verilog-rtl-post-processor/
├── post_processor.py      # Main tool — parse, detect, insert, output
├── clock_gate.v           # Auto-generated latch-based clock gating cell
├── sample.v               # Simple test case — 1 ungated, 1 gated register
├── complex_sample.v       # Complex test case — 2 ungated, 1 gated register
├── sample_gated.v         # Modified output for sample.v
├── complex_sample_gated.v # Modified output for complex_sample.v
├── sample_analysis.json   # JSON analysis report for sample.v
└── complex_sample_analysis.json
```

## How To Run

### Requirements
- Python 3.x
- [Icarus Verilog](https://bleyer.org/icarus/) (iverilog)

### Run the tool
```bash
python post_processor.py <verilog_file>
```

### Example
```bash
python post_processor.py sample.v
```

Output:
```
Written to sample_gated.v
Generated: sample_analysis.json
Generated: clock_gate.v
```

### Verify output compiles
```bash
iverilog -o sim.vvp clock_gate.v sample_gated.v
```

## What The Tool Does

### 1. Parse Verilog Structure
Extracts module name, port declarations, and signal definitions using regex:

```python
extract_module_name(content)  # → "sample"
extract_ports(content)        # → ["input clk", "input [7:0] data_in", ...]
extract_signals(content)      # → ["reg [7:0] reg_ungated", ...]
```

### 2. Detect Ungated Registers
Splits file by `always @(posedge clk)` blocks and checks each body for an `if` condition:

```
Block WITHOUT if → ungated → needs clock gating
Block WITH if    → gated   → leave alone
```

### 3. Insert Latch-Based Clock Gating Cell
For each ungated register, the tool:
- Instantiates a `clock_gate` module before the always block
- Changes `posedge clk` to `posedge gated_clk`

**Before:**
```verilog
always @(posedge clk) begin
    reg_ungated <= data_in;
end
```

**After:**
```verilog
clock_gate cg1(.clk(clk), .enable(enable), .gated_clk(gated_clk1));

always @(posedge gated_clk1) begin
    reg_ungated <= data_in;
end
```

### 4. Latch-Based Clock Gating Cell
The generated `clock_gate` module uses a latch to prevent glitches:

```verilog
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
```

The latch captures `enable` during the LOW phase of the clock. When clock goes HIGH, `enable_latched` is already stable — preventing glitches from corrupting registers.

### 5. JSON Analysis Report
Outputs a structured JSON report:

```json
{
  "module_name": "complex_sample",
  "ports": ["input clk", "input [7:0] data_in", "output reg [7:0] reg_a"],
  "signals": ["reg [7:0] reg_a", "reg [7:0] reg_b"],
  "ungated_registers": [1, 2],
  "gated_registers": [3]
}
```

## Why Latch-Based vs Simple if (enable)?

| Approach | How it works | Power saving |
|---|---|---|
| `if (enable)` | Register ignores clock when disabled | Partial — clock still reaches register |
| Latch-based gate | Clock physically blocked before register | Full — no switching activity |

Simple `if (enable)` works in simulation but doesn't save power in real silicon — the clock wire still switches every cycle. A latch-based gate physically stops the clock pulse before it reaches the register.

## Verified With Icarus Verilog

Both test cases compile and simulate correctly:

```bash
iverilog -o s1.vvp clock_gate.v sample_gated.v        # clean
iverilog -o s2.vvp clock_gate.v complex_sample_gated.v # clean
```

## Built With

- Python 3.x — regex parsing, file I/O, JSON output
- Verilog — clock gating cell implementation
- Icarus Verilog — compilation and simulation verification

## Author

Vivek — MS Computer Engineering, University of Kentucky
