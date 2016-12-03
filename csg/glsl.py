from .treenode import TreeNodeVisitor

def to_glsl(arg):
    """
    Converts values to correct glsl strings
    :param arg: int, float, vec3
    :return: string
    """
    if isinstance(arg, float):
        s = str(arg)
        if not '.' in s:
            s += '.'
        return s
    if isinstance(arg, vec3):
        return "vec3(%s, %s, %s)" % (to_glsl(arg[0]), to_glsl(arg[1]), to_glsl(arg[2]))
    return str(arg)


def indent_code(code, indent="    "):
    import re
    return indent + re.sub(r"\n[ |\t]*", "\n"+indent, code.strip())


def render_glsl(csg, indent="    "):
    """
    Render the whole glsl code to represent the CSG object
    :param csg: CsgBase
    :return:
    """
    class FuncVisitor(TreeNodeVisitor):
        def __init__(self):
            self.code = ""
            self.id = 0

        def visit(self, node):
            self.id += 1
            node._id = self.id
            body = node.get_glsl_function()
            if not body:
                return
            self.code += "float %s(in vec3 p)\n{\n" % node.get_glsl_function_name()
            self.code += indent_code(body, indent) + "\n"
            self.code += "}\n"

    code = "/*\n%s\n%s*/\n" % (str(csg), csg.render_node_tree())

    f = FuncVisitor()
    f.traverse_reverse(csg)
    code += f.code

    return code