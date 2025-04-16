from .types import *

def test_chatnode_initialization():
    node = ChatNode(name="root", type="text", content="Hello, world!")
    assert node.name == "root"
    assert node.type == "text"
    assert node.content == "Hello, world!"
    assert node.children == []

def test_chatnode_add_child():
    parent = ChatNode(name="parent", type="text", content="Parent node")
    child = ChatNode(name="child", type="text", content="Child node")
    
    returned_child = parent.addChild(child)
    
    assert len(parent.children) == 1
    assert parent.children[0] == child
    assert returned_child == child