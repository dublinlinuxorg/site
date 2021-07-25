from typing import List

class Trie:
    def __init__(self, name):
        self.name = name
        self.root = Node('$', '/', '.')
        self.paths_from_root = ['/']
        self.paths_and_subpaths_from_root = ['/']

    def walk_all_paths(self, node = None, paths = [], path = ""):
        """
        collects all linked children of root and 
        adds the paths to paths_from_root 
        """
        if node is None:
            self.paths_from_root = []
            self.paths_and_subpaths_from_root = []
            node = self.root
        if node.children == []:
            self.paths_from_root.append(path)
            elements = path.split('/')
            for n in range(1, len(elements)):
                self.paths_and_subpaths_from_root.append('/'.join(elements[0: n+1]))
        for child in node.children:
            self.walk_all_paths(node=child, path=(path + '/' + (child.path_from_root.split('/')[-1])))
    
    def print_paths(self):
        self.walk_all_paths()
        print(self.paths_from_root)
    
    def has_path(self: object, path: str, node: object = None, depth: int = 0):
        self.walk_all_paths()
        self.print_paths()
        print(self.paths_and_subpaths_from_root)
        if path not in self.paths_and_subpaths_from_root:
            return False
        return True

    def get_node_by_path(self, path: str, node: object=None, depth: int=1):
        """
        given a string path, returns the last node of the path
        or None, if path doesn't exist 
        """
        if node == None:
            if not self.has_path(path):
                print('path does not exist')
                return None
            node = self.root
        if len(path.split('/')) == depth:
            return node
        depth += 1 # the path has a starting `/` so there is an extra element in the path list
        node = [n for n in node.children if n.path_from_root == '/'.join(path.split('/')[0:depth])][0]
        return self.get_node_by_path(path, node, depth)

    def add_leaf_node_with_path(self, node_name, path, page_url):
        if self.has_path(path):
            print("changing existing node")
        # TODO: finish

class Node:
    def __init__(self, name, path_from_root, page_url=None):
        self._name = name
        self.path_from_root = path_from_root
        self._page_url = page_url
        self._children = []
    
    def __repr__(self):
        # return f'Node {self.name}, path_from_root: {self.path_from_root}, page_url: {self.page_url}, children: {self.children}'
        return f'children: {self.children}'
    
    @property
    def page_url(self) -> str:
        return self._page_url

    @page_url.setter
    def page_url(self, val) -> None:
        self._page_url = val
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> List[object]:
        return self._children
    
    @property
    def child_names(self) -> List[str]:
        names = []
        for child in self._children:
            names.append(child.name)
        return names
    
    @property
    def kids(self) -> str:
        return self._kids

    def get_child_by_name(self, name) -> object:
        for child in self._children:
            if child.name == name:
                return child
        raise AttributeError(f'no child named "{name}"')

    def add_child(self, val) -> None:
        if val.name in self.child_names:
            raise IndexError(f"node already has a child with the name {val.name}")
        self._children.append(val)

    def print_children(self):
        for child in self.children:
            print(f'{child.name}, {child.path_from_root}')

if __name__ == '__main__':
    node = Node('test_node', '/test_node', 'test_node')
    node2 = Node('test_node2', '/test_node/test_node2', 'test_node2')
    node3 = Node('test_node3', '/test_node/test_node2/test_node3', 'test_node3')
    node4 = Node('test_node4', '/test_node4', 'test_node4')
    node.add_child(node2)
    node2.add_child(node3)
    # node.add_child(node3)
    trie = Trie('t')
    trie.root.add_child(node)
    trie.root.add_child(node4)
    # n4 = node.get_child_by_name('test_node2')
    # print(trie.has_path(['test_node', 'test_node7']))
    # trie.walk_all_paths()
    # trie.print_paths()
    print(trie.has_path('/test_node/test_node2/test_node4'))
    print(trie.get_node_by_path('/test_node4').name)
    print(trie.get_node_by_path('/test_node/test_node2').name)
    print(trie.get_node_by_path('/test_node/test_node2/test_node3').name)
    if trie.get_node_by_path('/test_node/test_node2/test_node4') is None:
        print('none')
    # print([n.name for n in node3.children])
    # print(node.name + '->' + ','.join([n.name for n in node.children]))
    # print(node2.name + '->' + ','.join([n.name for n in node2.children]))
    # print(node3.name + '->' + ','.join([n.name for n in node3.children]))