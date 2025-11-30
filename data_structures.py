from abc import ABC, abstractmethod

class TreeNode(ABC):
    """Abstract method for a Node in a Tree."""

    def __init__(self, name, inode = None):
        """Initializes a Node in a Tree.

        Args:
            name (str): The file's path on the disk.
            inode (int, optional): The id number of the file.
        """
        self.__name = name
        self.__inode = inode

    #property getter and setters
    @property
    def name(self):
        return self.__name

    @property
    def inode(self):
        return self.__inode

    @inode.setter
    def inode(self, inode):
        self.__inode = inode

    @property
    @abstractmethod
    def size(self):
        return self.size

    #start of actual methods
    def __repr__(self):
        """Returns a string that represents the node.

        Returns:
            str: The string representation of the node.
        """
        return f'{self.__name} - {self.size}'

    @abstractmethod
    def __eq__(self, other):
        """An abstract method that compares one instance of a node to another.

        Returns:
            bool: True if the instances of nodes are equal, False otherwise.
        """
        pass

    @abstractmethod
    def __hash__(self):
        """An abstract method that creates a hash for our object. This method allows
        a node to be used as a key in a dictionary or to be used in sets.
        """
        pass

class DirectoryNode(TreeNode):
    """Initializes a node for the directory tree."""

    def __init__(self, name, inode = None):
        """Initializes a node from the parent constructor.

        Args:
            name (str): The file's path on the disk.
            inode (int, optional): The id number of the file.
            children (set): Children nodes of the current node.
        """
        super().__init__(name, inode)
        self.__children = {}

    #property getter and setters.
    @property
    def children(self):
        return self.__children
    @property
    def size(self):
        """Recursively iterates over the node's children and sums the total size of all files therein."""
        return self.size

    #start of methods
    def add_child(self, child_node):
        """Check if the child node that is passed in has an inode value.
        Args:
            child_node (TreeNode): The child node to be added.
        Returns:
            ValueError (Exception): If the child node pass has no inode value.
        """
        pass

    def __repr__(self):
        """Returns the super class's representation.

        Returns:
            str: len(self.__children_) children
        """
        return f'({len(self.__children)} children'

    def __eq__(self, other):
        """Check if our name and our children are equal to the other node's name and other node's children.

        Returns:
            bool: True if the name and children are equal, False otherwise.
        """
        pass

    def __hash__(self):
        """Creates a hash for our object.

        Returns:
            hash: hash((self.name, frozenset(self.__children.items()))
        """
        return hash((self.name, frozenset(self.__children.items())))





