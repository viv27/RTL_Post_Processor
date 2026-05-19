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

if __name__ == "__main__":
    content = read_verilog("sample.v")
    ungated, gated = detect_ungated_registers(content)
    print(f"Ungated registers: {ungated}")
    print(f"Gated registers: {gated}")

    print(parse_verilog(content))



    



