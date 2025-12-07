from abc import ABC, abstractmethod

class TreeNode(ABC):
    """Abstract method for a Node in a filesystem tree."""

    def __init__(self, name, inode = None):
        """Initializes a Node in the Tree.

        Args:
            name (str): The file's path on the disk.
            inode (int, optional): The id number of the file.
        """
        self.__name = name
        self.__inode = inode

    @property
    def name(self):
        """Return the node's name."""

        return self.__name

    @property
    def inode(self):
        """Return the inode number assigned to the node."""

        return self.__inode

    @inode.setter
    def inode(self, inode):
        """Update the inode number for the node."""

        self.__inode = inode

    @property
    @abstractmethod
    def size(self):
        """Return the size of the node."""

    #start of actual methods
    def __repr__(self):
        """Returns a string that represents the node."""

        return f'{self.__name} - {self.size}'

    @abstractmethod
    def __eq__(self, other):
        """Compare two nodes for equality."""

    @abstractmethod
    def __hash__(self):
        """Return a hash of the node."""

class DirectoryNode(TreeNode):
    """Represents a directory in the filesystem tree."""

    def __init__(self, name, inode = None):
        """Initializes a directory node.

        Args:
            name (str): The file's path on the disk.
            inode (int, optional): The id number of the file.
        """
        super().__init__(name, inode)
        self.__children = {}

    @property
    def children(self):
        """Return the children of the directory."""

        return self.__children

    @property
    def size(self):
        """Sum the size of the directory's children."""

        return sum(child.size for child in self.__children.values())


    def add_child(self, child_node):
        """Add a child node to the directory.
        Args:
            child_node (TreeNode): The child node to add.

        Raises:
            ValueError: If the child node pass has no inode value.
        """
        if child_node is None or child_node.inode is None:
            raise ValueError("Child node must have an inode value")
        self.__children[child_node.inode] = child_node

    def __repr__(self):
        """Return a representation that includes the number of children."""

        return f'{self.name} ({len(self.__children)} children'

    def __eq__(self, other):
        """Compare directories by name and children."""

        if not isinstance(other, DirectoryNode):
            return False
        return self.name == other.name and self.__children == other.children

    def __hash__(self):
        """Return the hash of the directory node."""

        return hash((self.name, frozenset(self.__children.items())))

class FileNode(TreeNode):
    """Represents a leaf node in the filesystem tree."""
    def __init__(self, name, inode = None, size = 0):
        """Initialize a file node with its size.

        Args:
            name (str): The file's path on the disk.
            inode (int, optional): The id number of the file.
            size (int): The file's size in bytes.
        """
        super().__init__(name, inode)
        self.__size = size

    @property
    def size(self):
        """Return the size of the file."""

        return self.__size

    @property
    def fingerprint(self):
        """Return a fingerprint that uniquely identifies the file node."""

        return (self.name, self.inode, self.size)

    def __eq__(self, other):
        """Compare two file nodes for equality."""

        if not isinstance(other, FileNode):
            return False
        return (
            self.name == other.name
            and self.inode == other.inode
            and self.size == other.size
        )

    def __hash__(self):
        """Return the hash of the file node."""

        return hash((self.name, self.inode, self.size))

    def __repr__(self):
        """Return a string representation of the file node"""

        return f'{self.name} - {self.size}'