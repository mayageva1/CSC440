import os
import sys
import marshal
import array

try:
    import cPickle as pickle
except:
    import pickle
class Node:
    def __init__(self, char=None, freq=0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

def calculate_frequencies(msg):
    freq = {}
    for char in msg:
        if char in freq:
            freq[char] += 1
        else:
            freq[char] = 1
    return freq

def generate_codes(node, current_code, codes):
    if node is None:
        return
    if node.char is not None:
        codes[node.char] = current_code
    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)

def build_tree(nodes):
    while len(nodes) > 1:
        nodes = sorted(nodes, key=lambda x: x.freq)
        left = nodes.pop(0)
        right = nodes.pop(0)
        merged = Node(freq=left.freq + right.freq)
        merged.left = left
        merged.right = right
        nodes.append(merged)
    return nodes[0]

def generate_codes(node, current_code, codes):
    if node is None:
        return
    if node.left is None and node.right is None:
        # leaf
        codes[node.char] = current_code if current_code != "" else "0"
        return
    if node.left:
        generate_codes(node.left, current_code + "0", codes)
    if node.right:
        generate_codes(node.right, current_code + "1", codes)
    
def code(msg):
    # str is the ASCII representation of the 
    # Huffman-encoded message
    nodes = []
    #calculate frequency of each character in msg
    freq = calculate_frequencies(msg)
    #build huffman tree based on frequencies
    root = build_tree([Node(char, frequency) for char, frequency in freq.items()])
    #generate huffman codes
    codes = {}
    generate_codes(root, "", codes)
    # Tree is your representation of the 
    # Huffman tree needed to decompress that message
    str = "".join(codes[char] for char in msg)
    return (str, root)

def decode(msg, decoderRing):
    codes = {}
    generate_codes(decoderRing, "", codes)
    current_code = ""
    decoded_chars = []
    code_to_char = {v: k for k, v in codes.items()}
    for bit in msg:
        current_code += bit
        if current_code in code_to_char:
            decoded_chars.append(code_to_char[current_code])
            current_code = ""
    return "".join(decoded_chars)
    # msg is the ASCII representation of the Huffman-encoded message
    # decoderRing is your representation of the Huffman tree needed to decompress that message
def compress(msg):
    # Initializes an array to hold the compressed message.
    compressed = array.array('B')
    # Empty input
    if not msg:
        compressed.extend([0, 0, 0, 0])  # 4-byte big-endian length
        return (compressed, None)
    # Build frequency table and Huffman tree
    freq = calculate_frequencies(msg)
    root = build_tree([Node(char, frequency) for char, frequency in freq.items()])

    # Generate codes
    codes = {}
    generate_codes(root, "", codes)

    # 4-byte header
    n = len(msg)
    compressed.extend([(n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF])

    # Bit-pack the code stream, MSB-first within each byte
    bit_buffer = 0
    bit_count = 0
    for byte in msg:
        code = codes[byte]
        for bit in code:
            bit_buffer = (bit_buffer << 1) | (1 if bit == '1' else 0)
            bit_count += 1
            if bit_count == 8:
                compressed.append(bit_buffer)
                bit_buffer = 0
                bit_count = 0

    #pad zeros on the right)
    if bit_count > 0:
        bit_buffer <<= (8 - bit_count)
        compressed.append(bit_buffer)

    return (compressed, root)

def decompress(msg, decoderRing):
    # Represent the message as an array
    byteArray = array.array('B',msg)
     # Not enough for header → empty
    if len(byteArray) < 4:
        return b""
    # Read 4-byte big-endian symbol count
    n_symbols = (byteArray[0] << 24) | (byteArray[1] << 16) | (byteArray[2] << 8) | byteArray[3]
    if n_symbols == 0:
        return b""
    # Single-leaf tree fast-path: emit that symbol n_symbols times
    if decoderRing.left is None and decoderRing.right is None:
        sym = decoderRing.char
        return bytes([sym]) * n_symbols
    out = bytearray()
    idx = 4  # start of bit payload
    node = decoderRing
    emitted = 0
    while idx < len(byteArray) and emitted < n_symbols:
        b = byteArray[idx]
        idx += 1
        # Consume bits MSB→LSB to mirror packing
        for shift in range(7, -1, -1):
            bit = (b >> shift) & 1
            node = node.right if bit == 1 else node.left

            # Reached a leaf → emit symbol and reset to root
            if node.left is None and node.right is None:
                out.append(node.char)
                emitted += 1
                if emitted == n_symbols:
                    break
                node = decoderRing
    return bytes(out)

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) != 4:
        usage()
    opt = sys.argv[1]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    if opt == "-c":
        compressing = True
    elif opt == "-d":
        decompressing = True
    elif opt == "-v":
        encoding = True
    elif opt == "-w":
        decoding = True
    else:
        usage()

    infile = sys.argv[2]
    outfile = sys.argv[3]
    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        msg = fp.read()
        fp.close()
        if compressing:
            compr, tree = compress(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), compr), fcompressed)
            fcompressed.close()
        else:
            enc, tree = code(msg)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), enc), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pickleRick, compr = marshal.load(fp)
        tree = pickle.loads(pickleRick)
        fp.close()
        if decompressing:
            msg = decompress(compr, tree)
        else:
            msg = decode(compr, tree)
            print(msg)
        fp = open(outfile, 'wb')
        fp.write(msg)
        fp.close()