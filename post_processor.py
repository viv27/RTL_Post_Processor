import re
import json
import sys
import os

def read_verilog(filepath):
    with open(filepath) as f:
        return f.read()

def detect_ungated_registers(content):
    parts = re.split(r"always\s*@\s*\(\s*posedge\s+clk\s*\)", content)
    ungated = []
    gated = []
    for i, part in enumerate(parts[1:], 1):
        block_body = part.split("end")[0]
        if "if" in block_body:
            gated.append(i)
        else:
            ungated.append(i)
    return ungated, gated

def extract_module_name(content):
    match = re.search(r"module\s+(\w+)", content)
    if match:
        return match.group(1)
    return None

def extract_ports(content):
    return re.findall(r"((?:input|output)\s+(?:reg\s+)?(?:\[\d+:\d+\]\s+)?\w+)", content)

def extract_signals(content):
    return re.findall(r"(?:wire|reg)\s+(?:\[\d+:\d+\]\s+)?\w+", content)

def parse_verilog(content):
    return {
        "module_name": extract_module_name(content),
        "ports": extract_ports(content),
        "signals": extract_signals(content)
    }

def generate_clock_gate_cell():
    lines = []
    lines.append("module clock_gate(")
    lines.append("    input clk,")
    lines.append("    input enable,")
    lines.append("    output gated_clk")
    lines.append(");")
    lines.append("    reg enable_latched;")
    lines.append("    always @(clk or enable) begin")
    lines.append("        if (!clk) begin")
    lines.append("            enable_latched <= enable;")
    lines.append("        end")
    lines.append("    end")
    lines.append("    assign gated_clk = clk & enable_latched;")
    lines.append("endmodule")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_processor.py <verilog_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    base = os.path.splitext(filepath)[0]
    content = read_verilog(filepath)
    ungated, gated = detect_ungated_registers(content)

    modified_content = content
    cg_counter = 1

    parts = re.split(r"(always\s*@\s*\(\s*posedge\s+clk\s*\))", content)
    for i, part in enumerate(parts):
        if re.match(r"always\s*@\s*\(\s*posedge\s+clk\s*\)", part):
            block_body = parts[i+1]
            if "if" not in block_body.split("end")[0]:
                assignment = re.search(r"\s+\w+\s*<=\s*[\w\s]+;", block_body)
                if assignment:
                    old_always = "always @(posedge clk)" + block_body.split("end")[0] + "end"
                    new_always = f"clock_gate cg{cg_counter}(.clk(clk), .enable(enable), .gated_clk(gated_clk{cg_counter}));\n\nalways @(posedge gated_clk{cg_counter})" + block_body.split("end")[0] + "end"
                    modified_content = modified_content.replace(old_always, new_always)
                    cg_counter += 1

    with open(base + "_gated.v", "w") as f:
        f.write(modified_content)
    print("Written to " + base + "_gated.v")

    parsed = parse_verilog(content)
    parsed["ungated_registers"] = ungated
    parsed["gated_registers"] = gated

    with open(base + "_analysis.json", "w") as f:
        json.dump(parsed, f, indent=2)
    print("Generated: " + base + "_analysis.json")

    clock_gate_verilog = generate_clock_gate_cell()
    with open("clock_gate.v", "w") as f:
        f.write(clock_gate_verilog)
    print("Generated: clock_gate.v")