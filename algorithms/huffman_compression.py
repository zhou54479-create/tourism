"""
哈夫曼压缩算法 - 用于日记文本压缩
"""

import heapq
from collections import Counter
from typing import Dict, Tuple

class HuffmanNode:
    """哈夫曼树节点"""
    def __init__(self, char: str = '', freq: int = 0):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text: str) -> HuffmanNode:
    """构建哈夫曼树"""
    if not text:
        return HuffmanNode()
    
    freq = Counter(text)
    heap = [HuffmanNode(char, f) for char, f in freq.items()]
    heapq.heapify(heap)
    
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(freq=left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)
    
    return heap[0] if heap else HuffmanNode()

def build_code_table(root: HuffmanNode) -> Dict[str, str]:
    """生成哈夫曼编码表"""
    codes = {}
    
    def traverse(node: HuffmanNode, code: str):
        if node.char:
            codes[node.char] = code or '0'
            return
        if node.left:
            traverse(node.left, code + '0')
        if node.right:
            traverse(node.right, code + '1')
    
    if root.char:
        codes[root.char] = '0'
    else:
        traverse(root, '')
    
    return codes

def compress(text: str) -> Tuple[bytes, Dict[str, str]]:
    """
    压缩文本
    返回: (压缩后的二进制数据, 编码表)
    """
    if not text:
        return b'', {}
    
    root = build_huffman_tree(text)
    code_table = build_code_table(root)
    
    # 将文本编码为二进制字符串
    encoded = ''.join(code_table[char] for char in text)
    
    # 补位并转为bytes
    padding = 8 - len(encoded) % 8
    encoded += '0' * padding
    
    result = bytearray()
    for i in range(0, len(encoded), 8):
        result.append(int(encoded[i:i+8], 2))
    
    # 在第一个字节储存补位数
    result.insert(0, padding)
    
    return bytes(result), code_table

def decompress(data: bytes, code_table: Dict[str, str]) -> str:
    """
    解压数据
    参数: data - 压缩后的二进制数据, code_table - 编码表
    """
    if not data:
        return ''
    
    # 读取补位数
    padding = data[0]
    data = data[1:]
    
    # 转为二进制字符串
    bits = ''.join(format(byte, '08b') for byte in data)
    
    # 去掉补位
    bits = bits[:-padding] if padding else bits
    
    # 反转编码表
    reverse_table = {code: char for char, code in code_table.items()}
    
    # 解码
    result = []
    current = ''
    for bit in bits:
        current += bit
        if current in reverse_table:
            result.append(reverse_table[current])
            current = ''
    
    return ''.join(result)