import sys
sys.stdout.reconfigure(encoding='utf-8')

p = r'C:\Users\GLY\.config\opencode\skills\math-paper-reproduction\SKILL.md'
with open(p, 'rb') as f:
    raw = f.read()

# Check encoding
print(f"File size: {len(raw)} bytes")
print(f"First 3 bytes (BOM): {raw[0]:02X} {raw[1]:02X} {raw[2]:02X}")

# Check if UTF-8 decode succeeds completely
try:
    decoded = raw.decode('utf-8')
    print("UTF-8 decode: OK")
    # Check for known characters
    if '宿主检测' in decoded:
        print("✓ '宿主检测' found correctly")
    else:
        print("✗ '宿主检测' NOT found")
        # Show what's actually at position ~line 5
        lines = decoded.split('\n')
        for i, line in enumerate(lines[:8], 1):
            print(f"  Line {i}: {repr(line[:100])}")
except Exception as e:
    print(f"UTF-8 decode failed: {e}")
    
# Check CP936/GBK decode
try:
    decoded_gbk = raw.decode('gbk')
    print(f"\nGBK decode: OK")
    if '宿主检测' in decoded_gbk:
        print("✓ '宿主检测' found in GBK decode")
        lines_gbk = decoded_gbk.split('\n')
        for i, line in enumerate(lines_gbk[:8], 1):
            print(f"  Line {i}: {repr(line[:100])}")
except:
    print(f"\nGBK decode: FAILED")
