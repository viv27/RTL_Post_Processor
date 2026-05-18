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

if __name__ == "__main__":
    content = read_verilog("sample.v")
    ungated, gated = detect_ungated_registers(content)
    print(f"Ungated registers: {ungated}")
    print(f"Gated registers: {gated}")