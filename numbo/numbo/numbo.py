"""
Python implementation of Numbo
Based on reading in _Fluid Concepts and Creative Analogies_
"""

import functools
import random
import sys

from coderack import Rack
from coderack import RackUrgency
from network import Network, LinkDirection, NetworkLink, NetworkNode


# Initialize PNet
class NumboNodeType:
    TARGET = "target"
    SECONDARY = "secondary target"
    BRICK = "brick"
    BLOCK = "block"
    OPERATION = "operation"


class NumboCytoNode:
    def __init__(self, label, ntype, networkNode=None):
        self.label = label
        self.ntype = ntype
        self.pnetNode = networkNode
        self.status = "free"
        self.links = []

        # TODO: Should this just be the weight/activation level?
        self.attractiveness = 1

    def add_link(self, link):
        self.links.append(link)
        if link.direction == LinkDirection.BIDIRECTIONAL:
            # TODO: This seems fragile, as we may add new fields
            link.node2.links.append(NetworkLink(link.node2, self, relationship=link.relationship, weight=link.weight))

    def linked_node_strings(self):
        return list(map(lambda x: str(x.node2), self.links))

    def __str__(self):
        selfstr = ""
        if self.ntype == NumboNodeType.OPERATION:
            selfstr += "(" + self.label.join(self.linked_node_strings()) + ")"
        else:
            selfstr = self.ntype + "." + self.status + ":" + self.label + "<" + str(
                self.pnetNode.activation if self.pnetNode else None) + ">"
            if self.ntype == NumboNodeType.BLOCK:
                selfstr = "[" + selfstr
                for l in self.links:
                    selfstr += "=" + str(l.node2)
                selfstr += "]"
        return selfstr


# TODO: Load these in as "facts" via JSON/YAML/whatever
def initPnet():
    pnet = Network()
    # Add our small numbers
    one = pnet.addNode(label="1", top=True)
    two = pnet.addNode(label="2", top=True)
    three = pnet.addNode(label="3", top=True)
    four = pnet.addNode(label="4", top=True)
    five = pnet.addNode(label="5", top=True)
    six = pnet.addNode(label="6", top=True)
    seven = pnet.addNode(label="7", top=True)
    eight = pnet.addNode(label="8", top=True)
    nine = pnet.addNode(label="9", top=True)
    ten = pnet.addNode(label="10", top=True)
    eleven = pnet.addNode(label="11", top=True)
    twelve = pnet.addNode(label="12", top=True)
    pnet.addNode(label="20", top=True)
    pnet.addNode(label="30", top=True)
    pnet.addNode(label="40", top=True)
    pnet.addNode(label="50", top=True)
    pnet.addNode(label="60", top=True)
    pnet.addNode(label="70", top=True)
    pnet.addNode(label="80", top=True)
    pnet.addNode(label="90", top=True)
    pnet.addNode(label="100", top=True)

    # -------
    # These are relationships
    requires = pnet.addNode("requires")
    produces = pnet.addNode("produces")  # does this make sense to do vs just saying we require these nodes
    inheritnode = pnet.addNode("inherits")
    similar = pnet.addNode("similar")
    # end relationships

    # Addition is a "concept" here
    addopt = pnet.addNode("additive operand")
    thesum = pnet.addNode("sum")
    addition = pnet.addNode("addition", top=True)
    addition.add_codelet(functools.partial(codelet_propose_operation, codelet_operation_add), children_only=True)
    # TODO: Should we have a special way of defining quantity?
    addition.add_link(NetworkLink(addition, addopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    addition.add_link(NetworkLink(addition, addopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    addition.add_link(NetworkLink(addition, thesum, direction=LinkDirection.UNIDIRECTIONAL, relationship=produces))

    multopt = pnet.addNode("multiplicative operand")
    multresult = pnet.addNode("multiplicative result")
    multiplication = pnet.addNode("multiplication", top=True)
    multiplication.add_codelet(functools.partial(codelet_propose_operation, codelet_operation_multiply),
                               children_only=True)
    # TODO: Should we have a special way of defining quantity?
    multiplication.add_link(
        NetworkLink(addition, multopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    multiplication.add_link(
        NetworkLink(addition, multopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    multiplication.add_link(
        NetworkLink(addition, multresult, direction=LinkDirection.UNIDIRECTIONAL, relationship=produces))

    # Subtraction
    minuend = pnet.addNode("minuend")
    subtrahend = pnet.addNode("subtrahend")
    difference = pnet.addNode("difference")
    subtraction = pnet.addNode("subtraction", top=True)
    subtraction.add_codelet(functools.partial(codelet_propose_operation, codelet_operation_subtract),
                            children_only=True)
    # TODO: Should we have a special way of defining quantity?
    subtraction.add_link(NetworkLink(addition, minuend, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    subtraction.add_link(
        NetworkLink(addition, subtrahend, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    subtraction.add_link(
        NetworkLink(addition, difference, direction=LinkDirection.UNIDIRECTIONAL, relationship=produces))

    for a in range(1, 11):
        node = pnet.getNode(str(a))
        if not node:
            node = pnet.addNode(label=str(a))
        for b in range(a, 11):
            bnode = pnet.getNode(label=str(b))
            if not bnode:
                bnode = pnet.addNode(label=str(b))
            if b == (a + 1) and not node.has_link_to(bnode.label, similar):
                node.add_link(NetworkLink(node, bnode, direction=LinkDirection.BIDIRECTIONAL, relationship=similar))

            # ADDITION
            sum = pnet.getNode((str)(a + b))
            if not sum:
                sum = pnet.addNode((str)(a + b))

            # create the instance of addition for these numbers
            plus = NetworkNode("+", parent_type=addition, long_desc=(node.label + "+" + bnode.label))
            pnet.addNode(plus, False)
            # TODO: There is a lot of redundancy in how links get added
            sum.add_link(NetworkLink(sum, plus, direction=LinkDirection.BIDIRECTIONAL, relationship=thesum))

            # TODO: Should these be bi-directional here?
            # Note that we are actually creating *instances* of the actual "ideal" type of the number
            plus.add_link(
                NetworkLink(plus, NetworkNode(node.label, parent_type=node), direction=LinkDirection.BIDIRECTIONAL,
                            relationship=addopt))
            plus.add_link(
                NetworkLink(plus, NetworkNode(bnode.label, parent_type=bnode), direction=LinkDirection.BIDIRECTIONAL,
                            relationship=addopt))

            # SUBTRACTION
            if b - a > 0:
                diff = pnet.getNode((str)(b - a))
                if not diff:
                    diff = pnet.addNode((str)(b - a))

                # create the instance of addition for these numbers
                minus = NetworkNode("-", parent_type=subtraction, long_desc=(bnode.label + "-" + node.label))
                pnet.addNode(minus, False)
                # TODO: There is a lot of redundancy in how links get added
                diff.add_link(NetworkLink(diff, minus, direction=LinkDirection.BIDIRECTIONAL, relationship=difference))

                # TODO: Should these be bi-directional here?
                # Note that we are actually creating *instances* of the actual "ideal" type of the number
                minus.add_link(
                    NetworkLink(minus, NetworkNode(bnode.label, parent_type=bnode),
                                direction=LinkDirection.BIDIRECTIONAL,
                                relationship=minuend))
                minus.add_link(
                    NetworkLink(minus, NetworkNode(node.label, parent_type=node), direction=LinkDirection.BIDIRECTIONAL,
                                relationship=subtrahend))

            # MULTIPLICATION
            if a > 1 and b > 1:
                result = pnet.getNode((str)(a * b))
                if not result:
                    result = pnet.addNode((str)(a * b))

                times = NetworkNode("*", parent_type=multiplication, long_desc=(node.label + "*" + bnode.label))
                pnet.addNode(times, False)
                result.add_link(
                    NetworkLink(result, times, direction=LinkDirection.BIDIRECTIONAL, relationship=multresult))

                times.add_link(
                    NetworkLink(times, NetworkNode(node.label, parent_type=node), direction=LinkDirection.BIDIRECTIONAL,
                                relationship=multopt))
                times.add_link(
                    NetworkLink(times, NetworkNode(bnode.label, parent_type=bnode),
                                direction=LinkDirection.BIDIRECTIONAL,
                                relationship=multopt))

    return pnet


def cytoplasm_find_exact(label, cytoplasm, allowed_types=['block', 'brick']):
    for elem in cytoplasm:
        if elem.label == label and elem.ntype in allowed_types:
            print "\tFound exact of " + label + " in cytoplasm"
            if elem.status == "free":
                return elem
            else:
                print "\tBut it is not free..."
    return None


def cytoplasm_find_less(label, cytoplasm):
    for elem in cytoplasm:
        if int(elem.label) == int(label) - 1:
            print "\tFound one less of " + label + " in cytoplasm"
            if elem.status == "free":
                return elem
            else:
                print "\tBut it is not free..."
    return None


def cytoplasm_find_greater(label, cytoplasm):
    for elem in cytoplasm:
        if int(elem.label) == int(label) + 1:
            print "\tFound one greater of " + label + " in cytoplasm"
            if elem.status == "free":
                return elem
            else:
                print "\tBut it is not free..."
    return None


def cytoplasm_find_less(label, cytoplasm):
    for elem in cytoplasm:
        if int(elem.label) == int(label) - 1:
            print "\tFound one less of " + label + " in cytoplasm"
            if elem.status == "free":
                return elem
            else:
                print "\tBut it is not free..."
    return None


def cytoplasm_find_near(label, cytoplasm, allowed_types=['block', 'brick']):
    for elem in cytoplasm:
        try:
            if elem.ntype in allowed_types and elem.pnetNode.has_link_to(label, "similar"):
                print "\tFound one near of " + label + " in cytoplasm: " + elem.label
                if elem.status == "free":
                    return elem
                else:
                    print "\tBut it is not free..."
                    # if elem.ntype in allowed_types and (int(elem.label) == int(label) + 1 or int(elem.label) == int(label) - 1):
        except AttributeError:
            print "\tHad issues with pNetNode for: " + str(elem)
    return None


def codelet_read_target(vision, pnet=None, cytoplasm=None):
    """
    Take in the 'target' item, adding it to the cytoplasm.
    Will likely lead to activation of nodes related to the number based on its size
    For example, a larger number would lead to activation of "multiplication", which
    itself would likely activate codelets which can perform multiplication
    :param vision:
    :param pnet:
    :param ext_cytoplasm:
    :return:
    """
    print "CODELET: read_target"
    t = vision['target']
    pNode = pnet.getNode(t)
    cNode = NumboCytoNode(t, NumboNodeType.TARGET, networkNode=pNode)
    codelets = []
    if pNode:
        codelets.extend(pNode.activate(level=10))
    else:
        codelets.append(functools.partial(codelet_find_syntactically_similar, cNode))

    cytoplasm.append(cNode)

    return codelets


def codelet_read_brick(vision, pnet=None, cytoplasm=None):
    print "CODELET: read_brick"
    bricks = vision['bricks']
    codelets = []
    if len(bricks):
        b = bricks.pop(random.randint(0, len(bricks)-1))
        pNode = pnet.getNode(b)
        cNode = NumboCytoNode(b, NumboNodeType.BRICK, networkNode=pNode)
        if pNode:
            codelets.extend(pNode.activate())
        else:
            codelets.append(functools.partial(codelet_find_syntactically_similar, cNode))

        cytoplasm.append(cNode)

    return codelets


def codelet_seek_reasonable_fascimile(desired, proposed, new_partials, pnet=None, cytoplasm=None, attempt=1):
    """
    Try to locate free Cyto nodes which are reasonably close
    to the given targets, and if available, push the next
    set of codelets
    desired - array of labels of nodes we would like to find (as numbers)
    proposed - the label for the item we plan on creating
    new_partials - the codelets that will get run if we succeed
    :return:
    """
    print "CODELET: seek_reasonable_fascimile: " + str(desired) + " ATTEMPT: " + str(attempt)
    assert len(desired) > 1

    found = []
    for des in desired:
        node = cytoplasm_find_exact(des, cytoplasm)
        if node is None or node in found:
            node = cytoplasm_find_near(des, cytoplasm)

            if node is None or node in found:
                print "\tUnable to find anything similar to " + des
                break
            else:
                found.append(node)
                node.status = 'pending'

        else:
            found.append(node)
            node.status = 'pending'

    returned = []
    for n in found:
        n.status = 'free'
    if len(found) == len(desired):
        # If we are here, we now have found all of our desired nodes
        # partials would be codelet_create_block()

        for codelet in new_partials:
            # this assumes our partials take positional arguments corresponding to what we found
            returned.append(functools.partial(codelet, *found))

    else:
        if attempt < 2:
            # Give it another shot... maybe this is more about reducing urgency?
            returned.append(functools.partial(codelet_seek_reasonable_fascimile, desired, proposed, new_partials,
                                              attempt=attempt + 1))

    return returned


def codelet_match_target(cytoplasm=None, pnet=None):
    print "CODELET: match_target"

    item = cytoplasm_find_exact(numboinput['target'], cytoplasm, allowed_types=['block'])
    if item:
        # TODO: We should perhaps just have access to the rack and clear it
        print "Found solution!"
        print str(item)
        sys.exit()
    return None


def codelet_find_syntactically_similar(needle, pnet=None, cytoplasm=None):
    """
    Identify PNet nodes which are "similar" to the given number
    """
    print "CODELET: find_similar: " + str(needle)
    if type(needle) is str:
        as_str = needle
    elif type(needle) is int:
        as_str = str(needle)
    else:
        as_str = needle.label
    the_len = len(as_str)
    # if we don't have it, then likely it is bigger than our low
    # numbers, so let's "reduce" it, first by converting it into a base number
    i = 0
    new_val = ""
    for c in as_str:
        if i == 0:
            new_val = c
        else:
            new_val += "0"
        i += 1

    print "\tPerhaps " + new_val + " is available?"
    codelets = []
    similar = pnet.getNode(new_val)
    if similar:
        # TODO: do this as a codelet
        codelets.extend(similar.activate(level=10))
        print "\t" + str(type(needle))
        needle.pnetNode = similar
    assert similar

    return codelets


def codelet_create_operation(pnet, cytoplasm):
    return []


def codelet_propose_operation(proposed_op, target_node=None, pnet=None, cytoplasm=None):
    """
    What this node should do is, based on the target node and "this" node
    take the required parameters and put in a codelet to identify blocks or bricks
    which are "similar" to the "inputs" into the operation
    and, if found, put on the codelet which actually does the operation
    :param proposed_op:
    :param target_node: the
    :return:
    """
    print "CODELET: propose_operation from " + target_node.long_desc
    print target_node.link_str()

    # Fetch inputs
    parent = target_node.parent

    inputs = []
    produces = None
    for l in parent.links:
        if str(l.relationship) == 'requires':
            needed = l.node2.label
            links = target_node.find_links(needed)
            found = False
            if links:
                for nl in links:
                    if nl.node2 not in inputs:
                        inputs.append(nl.node2)
                        found = True
                        break
                if not found:
                    print "\tERROR: all " + needed + " already used or not found"
                    return None
            else:
                print "\tERROR: Unable to find " + needed
                return None
        if str(l.relationship) == 'produces':
            needed = l.node2.label
            links = target_node.find_links(needed)
            if links:
                for nl in links:
                    produces = nl.node2.label
                    break
            else:
                print "\tERROR: Unable to find " + needed
                return None

    codelets = []
    inputs = list(map(lambda x: x.label, inputs))
    print "\tAdding codelet seek_reasonable_fascimile of " + str(inputs)

    fasc = functools.partial(codelet_seek_reasonable_fascimile, inputs, produces, [proposed_op])
    codelets.append(fasc)
    return codelets


def cytoplasm_create_block(op, result, node1, node2, cytoplasm=None, pnet=None):
    # TODO: This codelet should actually determine if we *want* to create this block
    # e.g. will it get us closer to the goal (or even match the goal)
    node1.status = 'taken'
    node2.status = 'taken'
    pNode = pnet.getNode(str(result))
    codelets = [codelet_match_target]

    cNode = NumboCytoNode(str(result), NumboNodeType.BLOCK, networkNode=pNode)
    if not pNode:
        codelets.append(functools.partial(codelet_find_syntactically_similar, cNode))
    else:
        pNode.activate(level=5)
    cOpNode = NumboCytoNode(op, NumboNodeType.OPERATION)
    cOpNode.add_link(NetworkLink(cNode, node1, direction=LinkDirection.UNIDIRECTIONAL))
    cOpNode.add_link(NetworkLink(cNode, node2, direction=LinkDirection.UNIDIRECTIONAL))
    cNode.add_link(NetworkLink(cNode, cOpNode, direction=LinkDirection.UNIDIRECTIONAL))

    cytoplasm.append(cNode)
    return codelets


def codelet_operation_multiply(node1, node2, pnet, cytoplasm):
    print "CODELET: operation_multiply"
    if node1.status == 'free' and node2.status == 'free':
        a = int(node1.label)
        b = int(node2.label)
        c = a * b
        return cytoplasm_create_block("x", c, node1, node2, pnet=pnet, cytoplasm=cytoplasm)


def codelet_operation_add(node1, node2, pnet=None, cytoplasm=None):
    print "CODELET: operation_add: " + node1.label + " + " + node2.label
    if node1.status == 'free' and node2.status == 'free':
        node1.status = 'taken'
        node2.status = 'taken'
        a = int(node1.label)
        b = int(node2.label)
        c = a + b
        return cytoplasm_create_block("x", c, node1, node2, pnet=pnet, cytoplasm=cytoplasm)


def codelet_operation_subtract(node1, node2, pnet=None, cytoplasm=None):
    print "CODELET: operation_subtract: " + node1.label + " + " + node2.label
    if node1.status == 'free' and node2.status == 'free':
        node1.status = 'taken'
        node2.status = 'taken'
        a = int(node1.label)
        b = int(node2.label)
        c = a - b
        return cytoplasm_create_block("-", c, node1, node2, pnet=pnet, cytoplasm=cytoplasm)

def debug_network():
    print "CYTOPLASM"
    for p in cytoplasm:
        print p


# print "CODERACK"
#    for p in rack:
#        print p


network = initPnet()

# this set of inputs exercises the ability to identify sub-targets based on subtraction
# TODO: Implement a codelet_identify_subtarget

numboinput = dict(target="114", bricks=["12", "20", "7", "1", "6"])
cytoplasm = []

rack = Rack()

rack.add(functools.partial(codelet_read_target, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.HIGH)
for x in range(0, len(numboinput['bricks'])):
    rack.add(functools.partial(codelet_read_brick, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.MID)

if int(numboinput['target']) > 20:
    network.activate("multiplication")
    network.activate("addition")
    network.activate("subtraction")
else:
    network.activate("addition")
    network.activate("subtraction")

debug_network()
# Here starts our main run loop, which should probably get encapsulated
while len(rack) > 0:

    codelet = rack.take()
    new_codelets = codelet()
    # TODO: this should likely be a set of tuples of (codelet, urgency)
    # or perhaps we just give each codelet access to the rack
    if new_codelets is not None:
        for c in new_codelets:
            rack.add(functools.partial(c, pnet=network, cytoplasm=cytoplasm), RackUrgency.MID)
    debug_network()


