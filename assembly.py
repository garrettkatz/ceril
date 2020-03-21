import shape as sh

class Assembly(object):
    def __init__(self, category, sub_assemblies, name=""):
        self.category = category
        self.sub_assemblies = tuple(sub_assemblies)
        self.name = name
        self.position = (0., 0., 0.)
        self.rotation = (0., 0., 0.)
    
    def __str__(self):
        s = "Assembly<%s>" % self.category
        if self.name != "": s += " " + self.name
        return s


def block(name=""):
    return Assembly("block", [sh.block()], name)


if __name__ == "__main__":
    
    print(Assembly("custom", [], name="garrett"))
    print(block("garrett"))

