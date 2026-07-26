class MinHeap:
    def __init__(self, array=None):
        if array is None:
            self.heap = []
            self.heap_size = 0
        else:
            self.heap = array[:]
            self.heap_size = len(self.heap)
            self.min_full_heapify()

    def parent(self, i): return (i - 1) // 2
    def left_child(self, i): return 2 * i + 1
    def right_child(self, i): return 2 * i + 2

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def min_reheapify(self, i):
        left, right, smallest = self.left_child(i), self.right_child(i), i
        if left < self.heap_size and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < self.heap_size and self.heap[right] < self.heap[smallest]:
            smallest = right
        if smallest != i:
            self._swap(i, smallest)
            self.min_reheapify(smallest)

    def _heapify_up(self, i):
        parent = self.parent(i)
        while i > 0 and self.heap[i] < self.heap[parent]:
            self._swap(i, parent)
            i = parent
            parent = self.parent(i)

    def min_full_heapify(self):
        for i in range((self.heap_size // 2) - 1, -1, -1):
            self.min_reheapify(i)

    def push(self, value):
        self.heap.append(value)
        self.heap_size += 1
        self._heapify_up(self.heap_size - 1)

    def min_extract(self):
        if self.heap_size < 1:
            raise IndexError("Cannot extract from empty heap.")
        min_val = self.heap[0]
        self._swap(0, self.heap_size - 1)
        self.heap.pop()
        self.heap_size -= 1
        if self.heap_size > 0:
            self.min_reheapify(0)
        return min_val


class PriorityQueue(MinHeap):
    def __init__(self):
        super().__init__()
        self.item_to_index = {}

    def _swap(self, i, j):
        item_i, item_j = self.heap[i][1], self.heap[j][1]
        self.item_to_index[item_i] = j
        self.item_to_index[item_j] = i
        super()._swap(i, j)

    def insert(self, item, priority):
        if item in self.item_to_index:
            self.decrease_key(item, priority)
            return
        self.heap.append([priority, item])
        self.item_to_index[item] = self.heap_size
        self.heap_size += 1
        self._heapify_up(self.heap_size - 1)

    def extract_min(self):
        if self.heap_size < 1:
            raise IndexError("Cannot extract from empty Priority Queue.")
        min_priority, min_item = self.heap[0]
        self._swap(0, self.heap_size - 1)
        self.heap.pop()
        del self.item_to_index[min_item]
        self.heap_size -= 1
        if self.heap_size > 0:
            self.min_reheapify(0)
        return min_item, min_priority

    def decrease_key(self, item, new_priority):
        if item not in self.item_to_index:      # guard added
            return
        idx = self.item_to_index[item]
        if self.heap[idx][0] <= new_priority:
            return
        self.heap[idx][0] = new_priority
        self._heapify_up(idx)

    def is_empty(self):
        return self.heap_size == 0