import json

"""
EXE_PATH = r"D:\SteamLibrary\steamapps\common\Geometry Dash GDL\GeometryDash.exe"
STRINGS_PATH = r".\str_dump6.txt"
OUTPUT_PATH = r"D:\SteamLibrary\steamapps\common\Geometry Dash GDL\gdl_patches.json"
"""

"""
EXE_PATH = r"D:\SteamLibrary\steamapps\common\Geometry Dash GDL MH7\GeometryDash.exe"
STRINGS_PATH = r".\str_dump6.txt"
OUTPUT_PATH = r"D:\SteamLibrary\steamapps\common\Geometry Dash GDL MH7\gdl_patches.json"
"""

#"""
EXE_PATH = r"./GeometryDash.exe"
STRINGS_PATH = r"./str_dump6.txt"
OUTPUT_PATH = r"./gdl_patches.json"
#"""

excludes = {
    "ship": ["0x12bac4", "0xc4c51", "0xc516d", "0x12a4d3", "0x12c1ba", "0x249a70"],
    "icon": [
        "0x71c3",
        "0x7878",
        "0x7e42",
        "0x5854a",
        "0x5859b",
        "0xc4a8b",
        "0xc4afc",
        "0xc4bf9",
        "0xc5012",
        "0xc5081",
        "0xc512f",
        "0x2498a6",
        "0x24993c"
    ],
    "ball": [
        "0x3a9e2",
        "0x58769",
        "0xc4ca9",
        "0xc51ab",
        "0x249c07"
    ],
    "spider": [
        "0x3aaef",
        "0x5887a",
        "0xc4e0d",
        "0x1253b6",
        "0x127d69",
        "0x12a5dc",
        "0x12bb3f",
        "0x12c208",
        "0x208463",
        "0x24a00c"
    ],
    "robot": [
        "0x3aaaf",
        "0x58839",
        "0xc4dca",
        "0xc5265",
        "0x1252f6",
        "0x127ba9",
        "0x12a5a7",
        "0x12bb27",
        "0x12c1f9",
        "0x2083a7",
        "0x249fac"
    ],
    "color": [
        "0x3abac",
        "0x5893a",
        "0xc4ed3",
        "0xc52e1",
        "0x24a12c"
    ],
    "Robot": [
        "0x144c67"
    ],
    "Spider": [
        "0x1461d7"
    ]
}

output = {}

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

with open(STRINGS_PATH, 'r') as f:
    lines = f.readlines()
    strings = [a[:-1] if not a == lines[-1] else a for a in lines] # removes the \n at the end of each line

with open(EXE_PATH, 'rb') as exe:
    exe_string = exe.read()
    ok_codes = [0x68, 0xba, 0xb9, 0xb8, 0xbf, 0xbe, 0xbb, 0x3c, 0xa4]
    
    all = 0
    wrong = 0
    all_codes = {}
    
    for string in strings:
        replaced_str = string.replace("\\n", "\n").replace("\\\\", "\\").replace("\\\"", '"').encode().replace(b'\xd0\xa0\xd0\x86\xd0\xa0\xe2\x80\x9a\xd0\xa1\xd1\x9b', b"\xE2\x80\xA2")
        
        #print([hex(x) for x in instruction])
        
        # 1. find the string address
        str_addr = exe_string.find(bytes([0x0]) + replaced_str + bytes([0x0])) + 0x1
        
        # 2. find all usages of it
        # how to do it is explained in "finding the instructions for addr gen be like.txt"
        ptr_addr = str(hex(str_addr + 0x400E00))[2:]
            
        instruction = bytearray([int(ptr_addr[4:6], 16), int(ptr_addr[2:4], 16), int(ptr_addr[0:2], 16), 0x0]) # ... offset string
        found_addrs = list(find_all(exe_string, instruction))
        
        OK_ADDRS = found_addrs.copy()
        for i in range(len(found_addrs)):
            addr = found_addrs[i]
            
            all += 1
            
            # now need to check that its actually the thing i need
            # 1. get the full instruction 
            
            first_op = hex(exe_string[addr-1])
            #if int(first_op, 16) in [0x3c,0xa4]:
            #    print(first_op, addr, found_addrs, replaced_str) # debug check
            
            all_codes[first_op] = all_codes[first_op] + 1 if first_op in all_codes else 1
            if not int(first_op, 16) in ok_codes:
                wrong += 1
                OK_ADDRS.remove(addr)
                continue
                
            if replaced_str.decode() in excludes:
                if str(hex(addr)) in excludes[replaced_str.decode()]:
                    #print("FOUNDEXCLUSION!!!!")
                    OK_ADDRS.remove(addr)
                    wrong += 1
           
        addrs = [str(hex(x)) for x in OK_ADDRS]
        output[replaced_str.decode()] = addrs
        print(f'{round(strings.index(string)/len(strings)*100.0,1)}%', end="\r")
        
    print(f'Wrong: {wrong} of {all} ({round(100.0 * (wrong/all), 3)}%)')
    #print(all_codes)
        
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(json.dumps(output, ensure_ascii=False, indent=4))
    #f.write(json.dumps(output, ensure_ascii=False))