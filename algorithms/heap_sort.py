"""
堆排序算法 - 用于Top-K推荐
时间复杂度：O(n log k)
"""

from typing import List, Callable, Any
import heapq

def heap_sort(items: List[Any], k: int, key: Callable = None, reverse: bool = True) -> List[Any]:
    """
    堆排序 - 返回前k个元素
    
    参数:
        items: 待排序列表
        k: 返回前k个
        key: 排序依据函数
        reverse: True=降序（高分优先）, False=升序（低价优先）
    
    返回:
        排序后的前k个元素
    """
    if not items or k <= 0:
        return []
    
    k = min(k, len(items))
    
    if key is None:
        key = lambda x: x
    
    if reverse:
        # 取前k大：用小顶堆
        heap = []
        for item in items:
            val = key(item)
            if len(heap) < k:
                heapq.heappush(heap, (val, id(item), item))
            elif val > heap[0][0]:
                heapq.heapreplace(heap, (val, id(item), item))
        
        # 从堆中取出并降序排列
        result = [heapq.heappop(heap)[2] for _ in range(len(heap))]
        result.reverse()
        return result
    else:
        # 取前k小：用大顶堆
        heap = []
        for item in items:
            val = key(item)
            neg_val = -val if hasattr(val, '__neg__') else -val
            if len(heap) < k:
                heapq.heappush(heap, (neg_val if isinstance(val, (int, float)) else val, id(item), item))
            elif val < heap[0][0] if isinstance(val, (int, float)) else val < heap[0][0]:
                heapq.heapreplace(heap, (val, id(item), item))
        
        result = [heapq.heappop(heap)[2] for _ in range(len(heap))]
        return result