"""
Python implementation of Numbo
Based on reading in _Fluid Concepts and Creative Analogies_
"""

from coderack import Rack
from coderack import RackUrgency
from network import Network, LinkDirection, NetworkLink, NetworkNode
import functools
import random


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


    def __str__(self):
        return self.ntype + ":" + self.label + "(" + self.status + ")"


def initPnet():
    pnet = Network()
    # Add our small numbers
    one = pnet.addNode(label="1")
    two = pnet.addNode(label="2")
    three = pnet.addNode(label="3")
    four = pnet.addNode(label="4")
    five = pnet.addNode(label="5")
    six = pnet.addNode(label="6")
    seven = pnet.addNode(label="7")
    eight = pnet.addNode(label="8")
    nine = pnet.addNode(label="9")
    ten = pnet.addNode(label="10")
    eleven = pnet.addNode(label="11")
    twelve = pnet.addNode(label="12")

    addopt = pnet.addNode("additive operand")
    thesum = pnet.addNode("sum")
    requires = pnet.addNode("requires")
    produces = pnet.addNode("produces")  # does this make sense to do vs just saying we require these nodes
    inheritnode = pnet.addNode("inherits")

    # Addition is a "concept" here
    addition = pnet.addNode("addition")
    addition.add_codelet(functools.partial(codelet_propose_operation, codelet_operation_add), children_only=True)
    # TODO: Should we have a special way of defining quantity?
    addition.add_link(NetworkLink(addition, addopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    addition.add_link(NetworkLink(addition, addopt, direction=LinkDirection.UNIDIRECTIONAL, relationship=requires))
    addition.add_link(NetworkLink(addition, thesum, direction=LinkDirection.UNIDIRECTIONAL, relationship=produces))

    for a in range(1, 10):
        node = pnet.getNode(str(a))
        if not node:
            node = pnet.addNode(label=str(a))
        for b in range(1, 10):
            bnode = pnet.getNode(label=str(b))
            if not bnode:
                bnode = pnet.addNode(label=str(b))

            sum = pnet.getNode((str)(a + b))
            if not sum:
                sum = pnet.addNode((str)(a + b))

            # create the instance of addition for these numbers
            plus = NetworkNode("+", parent_type=addition, long_desc=(node.label + "+" + bnode.label))
            pnet.addNode(plus, False)
            sum.add_link(NetworkLink(thesum, plus, direction=LinkDirection.BIDIRECTIONAL, relationship=thesum))

            # TODO: Should these be bi-directional here?
            plus.add_link(NetworkLink(plus, node, direction=LinkDirection.BIDIRECTIONAL, relationship=addopt))
            plus.add_link(NetworkLink(plus, bnode, direction=LinkDirection.BIDIRECTIONAL, relationship=addopt))


    return pnet


def cytoplasm_find_exact(label, cytoplasm):
    for elem in cytoplasm:
        if elem.label == label:
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


def cytoplasm_find_near(label, cytoplasm):
    for elem in cytoplasm:
        if int(elem.label) == int(label) + 1 or int(elem.label) == int(label) - 1:
            print "\tFound one near of " + label + " in cytoplasm: " + elem.label
            if elem.status == "free":
                return elem
            else:
                print "\tBut it is not free..."
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
        codelets.extend(pNode.activate())
    else:
        codelets.add(functools.partial(codelet_find_similar, cNode))

    cytoplasm.append(cNode)

    return codelets


def codelet_read_brick(vision, pnet=None, cytoplasm=None):
    print "CODELET: read_brick"
    bricks = vision['bricks']
    codelets = []
    if len(bricks):
        b = bricks.pop(random.randint(0, len(bricks)-1))
        pNode = pnet.getNode(b)
        codelets.extend(pNode.activate())
        cNode = NumboCytoNode(b, NumboNodeType.BRICK, networkNode=pNode)
        cytoplasm.append(cNode)
        #codelets.append(functools.partial(codelet_find_similar, cNode))
    return codelets


def codelet_seek_reasonable_fascimile(desired, proposed, new_partials, pnet=None, cytoplasm=None):
    """
    Try to locate free Cyto nodes which are reasonably close
    to the given targets, and if available, push the next
    set of codelets
    desired - array of labels of nodes we would like to find (as numbers)
    proposed - the label for the item we plan on creating
    new_partials - the codelets that will get run if we succeed
    :return:
    """
    print "CODELET: seek_reasonable_fascimile: " + str(desired)

    found = []
    for des in desired:
        node = cytoplasm_find_exact(des, cytoplasm)
        if node is None or node in found:
            node = cytoplasm_find_near(des, cytoplasm)

            if node is None or node in found:
                print "\tUnable to find anything similar to " + des
                return

            found.append(node)

    if len(found) == len(desired):
        # If we are here, we now have found all of our desired nodes
        # partials would be codelet_create_block()
        returned = []
        for codelet in new_partials:
            # this assumes our partials take positional arguments corresponding to what we found
            returned.append(functools.partial(codelet, *found))

        return returned
    else:
        return None


def codelet_find_similar(needle, pnet=None,cytoplasm=None):
    """
    Identify PNet nodes which are "similar" to the given number
    """
    print "CODELET: find_similar"
    codelets = []
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

    # Fetch inputs
    parent = target_node.parent

    inputs = []
    produces = None
    for l in parent.links:
        if str(l.relationship) == 'requires':
            needed = l.node2.label
            print "\tNeed to find " + needed
            links = target_node.find_links(needed)
            if links:
                for nl in links:
                    if nl.node2 not in inputs:
                        inputs.append(nl.node2)
            else:
                print "\tERROR: Unable to find " + needed
                return None
        if str(l.relationship) == 'produces':
            needed = l.node2.label
            print "\tLooking for production of " + needed
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

    fasc = functools.partial(codelet_seek_reasonable_fascimile, inputs, produces, [proposed_op])
    codelets.append(fasc)
    return codelets

def codelet_operation_multiply(node1, node2, pnet, cytoplasm):
    print "CODELET: operation_multiply"
    if node1.status == 'free' and node2.status == 'free':
        node1.status = 'taken'
        node2.status = 'taken'
        a = int(node1.label)
        b = int(node2.label)
        c = a * b
        pNode = pnet.getNode(str(c))
        cNode = NumboCytoNode(c, NumboNodeType.BLOCK, networkNode=pNode)
        cOpNode = NumboCytoNode("x", NumboNodeType.OPERATION)
        cOpNode.addLink(NetworkLink(cNode, node1))
        cOpNode.addLink(NetworkLink(cNode, node2))
        cNode.addLink(NetworkLink(cNode, cOpNode))


def codelet_operation_add(node1, node2, pnet=None, cytoplasm=None):
    print "CODELET: operation_add: " + node1.label + " + " + node2.label
    if node1.status == 'free' and node2.status == 'free':
        node1.status = 'taken'
        node2.status = 'taken'
        a = int(node1.label)
        b = int(node2.label)
        c = a + b
        pNode = pnet.getNode(str(c))
        cNode = NumboCytoNode(str(c), NumboNodeType.BLOCK, networkNode=pNode)
        cOpNode = NumboCytoNode("+", NumboNodeType.OPERATION)
        cOpNode.add_link(NetworkLink(cNode, node1))
        cOpNode.add_link(NetworkLink(cNode, node2))
        cNode.add_link(NetworkLink(cNode, cOpNode))

        cytoplasm.append(cNode)

def debug_network():
    print "CYTOPLASM"
    for p in cytoplasm:
        print p
    print "CODERACK"
    for p in rack:
        print p


network = initPnet()

numboinput = dict(target="10", bricks=["2", "3", "5"])
cytoplasm = []

rack = Rack()

rack.add(functools.partial(codelet_read_target, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.HIGH)
rack.add(functools.partial(codelet_read_brick, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.HIGH)
rack.add(functools.partial(codelet_read_brick, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.HIGH)
rack.add(functools.partial(codelet_read_brick, numboinput, pnet=network, cytoplasm=cytoplasm), RackUrgency.HIGH)

network.activate("multiplication")
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


