from .treenode import TreeNodeVisitor
from pector import vec3, mat4

def to_glsl(arg):
    """
    Converts values to correct glsl strings
    :param arg: int, float, vec3, mat4
    :return: string
    """
    if isinstance(arg, float):
        if abs(arg) < 1e-10:
            arg = 0.
        s = str(arg)
        if not '.' in s:
            s += '.'
        return s
    if isinstance(arg, vec3):
        return "vec3(%s, %s, %s)" % tuple([to_glsl(x) for x in arg])
    if isinstance(arg, mat4):
        return "mat4(%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s)" % tuple([
            to_glsl(x) for x in arg])
    if isinstance(arg, list):
        if len(arg) == 9:
            return "mat3(%s,%s,%s, %s,%s,%s, %s,%s,%s)" % tuple([to_glsl(x) for x in arg])
    raise NotImplementedError("Can't convert to glsl: '%s'" % type(arg))


def indent_code(code, indent="    "):
    import re
    return indent + re.sub(r"\n[ |\t]*", "\n"+indent, code.strip())


def render_glsl(csg, indent="    "):
    """
    Render the whole glsl code to represent the CSG object
    :param csg: CsgBase
    :param indent: The indentation string to use within function bodies
    :return:
    """
    # a visitor to render the functions for nodes that define them
    class FuncVisitor(TreeNodeVisitor):
        def __init__(self):
            self.code = ""
            self.id = 0
            self.static_funcs = set()

        def visit(self, node):
            body = node.get_glsl_function_body()
            if body:
                self.id += 1
                node._id = self.id
                self.code += "\nfloat %s(in vec3 pos) {\n" % node.get_glsl_function_name()
                self.code += indent_code(body, indent) + "\n"
                self.code += "}\n"
            funcs = node.get_glsl_static_functions()
            for i in funcs:
                self.static_funcs.add(i)

    code = "/*\n%s*/\n\n" % csg.render_node_tree(lambda node: repr(node))

    # render needed functions
    f = FuncVisitor()
    f.traverse_reverse(csg)
    for i in f.static_funcs:
        code += i.strip() + "\n\n"
    code += f.code

    # render main function
    code += "\nfloat DE(in vec3 pos) {\n%sreturn %s;\n}\n" % (indent, csg.get_glsl("pos"))

    return code