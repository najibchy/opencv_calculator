class stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)
    
    def pop(self):
        if self.items.isEmpty():
            return IndexError("The stack is empty")
        return self.items.pop()
    
    def peek(self):
        if self.items.isEmpty():
            return IndexError("The stack is empty")
        return self.items[-1]    
    
    def size(self):
        return len(self.items)
    
    def is_empty(self):
        return len(self.items) == 0
    
    def clear(self):
        return self.items.clear()
    
    def __str_(self) -> str:
        return "".join(self.items)

