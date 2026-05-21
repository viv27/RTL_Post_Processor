import re

def read_verilog(filepath):
    with open(filepath) as f:
        return f.read()

def detect_ungated_registers(content):

  
    parts = re.split(r"always\s*@\s*\(\s*posedge\s+clk\s*\)",content)
    
    ungated = []
    gated = []

    for i, part in enumerate(parts[1:],1):
        block_body = part.split("end")[0]
        if "if" in block_body:
            gated.append(i)
        else:
            ungated.append(i)
    return ungated,gated

def extract_module_name(content):
    match = re.search(r"module\s+(\w+)",content)
    if match:
        return match.group(1)
    else:
        return None

def extract_ports(content):

    ports = re.findall(r"((?:input|output)\s+(?:reg\s+)?(?:\[\d+:\d+\]\s+)?\w+)",content)
    return ports

def extract_signals(content):
    signals = re.findall(r"(?:wire|reg)\s+(?:\[\d+:\d+\]\s+)?\w+", content)
    return signals

def parse_verilog(content):
    return {
        "module_name": extract_module_name(content),
        "ports": extract_ports(content),
        "signals": extract_signals(content)
    }

def insert_clock_gating(content):
    assignments = re.findall(r"\s+\w+\s*<=\s*\w+;", content)
    print(assignments)


if __name__ == "__main__":
    content = read_verilog("sample.v")
    ungated, gated = detect_ungated_registers(content)
    #print(f"Ungated registers: {ungated}")
    #print(f"Gated registers: {gated}")

    parts = re.split(r"(always\s*@\s*\(\s*posedge\s+clk\s*\))", content)
    for i, part in enumerate(parts):
        print(f"--- Part {i} ---")
        
        if re.match(r"always\s*@\s*\(\s*posedge\s+clk\s*\)", part):
            block_body = parts[i+1]
            if "if" not in block_body.split("end")[0]:
                print(f"Block body (Part {i+1}): UNGATED — needs fixing")
                assignment = re.search(r"\s+\w+\s*<=\s*[\w\s]+;", block_body)
                if assignment:
                    original = assignment.group(0)
                    gated = "\n    if (enable) begin\n        " + original.strip() + "\n    end\n"
                    print("Original:", repr(original))
                    print("Gated:", repr(gated))
                    modified_content = content.replace(original, gated)
            else:
                print(f"Block body (Part {i+1}): GATED — leave alone")

    with open("sample_gated.v", "w") as f:
        f.write(modified_content)
        print("Written to sample_gated.v")



    



