class Shape(object):
    def __init__(self, category):
        self.category = category
    def __str__(self):
        return "Shape<%s>" % self.category

def block():
    return Shape("block")

if __name__ == "__main__":

    print(Shape("block"))
    print(block())

