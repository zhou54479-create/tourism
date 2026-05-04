"""
KMP查找算法 - 用于字符串匹配
时间复杂度：O(n + m)
"""

from typing import List

def build_lps(pattern: str) -> List[int]:
    """
    构建最长公共前后缀数组（LPS）
    """
    lps = [0] * len(pattern)
    length = 0
    i = 1
    
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    return lps

def kmp_search(text: str, pattern: str) -> List[int]:
    """
    KMP查找，返回所有匹配位置的起始索引
    """
    if not pattern or not text:
        return []
    
    lps = build_lps(pattern)
    matches = []
    i = j = 0
    
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            
            if j == len(pattern):
                matches.append(i - j)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return matches

def highlight(text: str, pattern: str) -> str:
    """
    高亮匹配文字（用 ** 包裹）
    """
    positions = kmp_search(text, pattern)
    if not positions:
        return text
    
    result = []
    last = 0
    
    for pos in positions:
        result.append(text[last:pos])
        result.append(f"**{text[pos:pos + len(pattern)]}**")
        last = pos + len(pattern)
    
    result.append(text[last:])
    return ''.join(result)