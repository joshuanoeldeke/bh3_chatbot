from .repliers import *

from .types import ChatNode

def test_hi_replier():
    replier = HiReplier()

    # Always expect one hi response
    for i in range(1,3):
        request = ChatNode("req", "i", "hi")
        response = replier.reply(request)
        assert len(response) == 1
    
    # Expect no response on "ende"
    request = ChatNode("ende", "i", "ende")
    response = replier.reply(request)
    assert len(response) == 0

def test_hi_replier_get_start():
    """Test that HiReplier.get_start returns the correct start node"""
    replier = HiReplier()
    start = replier.get_start()
    assert isinstance(start, list)
    assert len(start) == 1
    node = start[0]
    assert node.name == "start"
    assert node.type == "o"
    assert node.content == "Hi!"

from .types import ChatNode

def test_graph_replier_get_start_and_reply():
    """Test GraphReplier.get_start and reply methods"""
    # Create a small graph
    root = ChatNode("root", "o", "root content")
    child1 = ChatNode("child1", "o", "child1 content")
    child2 = ChatNode("child2", "c", "child2 content")
    root.addChild(child1)
    root.addChild(child2)

    replier = GraphReplier(root)
    # get_start should return the root as a single-item list
    assert replier.get_start() == [root]
    # reply should return the children of the given node
    assert replier.reply(root) == [child1, child2]
