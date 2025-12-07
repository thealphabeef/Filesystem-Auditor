from data_structures import *
from pathlib import Path
import datetime
import hashlib
import argparse
import pickle
import os

class Auditor:
    """Class for our command-line tool."""

    def __init__(self):
        """Initializes an Auditor for our tree."""

        #Create our argument parser object.
        parser = argparse.ArgumentParser()

        #Path is just the directory name that we want to audit. It could be something like My_Documents or Downloads
        #Path is the ONLY thing thats required.
        parser.add_argument("path", help="Directory to audit", type=str)

        #Our auditor compares an older snapshot of a directory to the current state of the directory. This flag lets us
        #specify which prior audit file to use. the default value is audit.log
        parser.add_argument("-i", "--input-file", help="Previous audit log file", type=str)

        #This controls where we write the new log to. It defaults to audit.log as well.
        parser.add_argument("-o", "--output-file", help="New audit log file", type=str)

        #If we use this flag, we are saying we want the full output instead of a short summary.
        parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")

        #This flag will cause the program to print our directory out in a nicely indented tree format.
        parser.add_argument("-t", "--tree", help="Print directory tree", action="store_true")
        args = parser.parse_args()

        self.__path = args.path
        self.__input_file = args.input_file or 'audit.log'
        self.__output_file = args.output_file or 'audit.log'
        self.__verbose = args.verbose
        self.__tree = args.tree
        self.__start_time = datetime.datetime.now()

        #This will hold the starting node of the tree that represents our previous audit.
        self.__old_root = None

        #This holds the starting node of the tree representing our current audit.
        self.__new_root = None
        self.audit()

    def show(self, msg):
        """Helper function to see if we are using verbose mode to print."""

        if self.__verbose:
            print(msg)

    def write_tree(self, root, path):
        """Take an object from a pickled file and restore it to memory.

        Args:
            root (TreeNode): Represents the top of our tree
            path: The place in which we wish to save to on the disk.
        """
        if not isinstance(root, TreeNode):
            raise IOError
        if not Path(path).parent.exists():
            raise OSError("The destination directory doesn't exist")

        with open(path, 'wb') as f:
            pickle.dump(root, f)

    def read_tree(self, path):
        """Take an object from a pickled file and restore it to memory.

        Args:
            path: The directory to restore to.
        """
        if not Path(path).exists():
            raise OSError("The file is not there.")
        with open(path, 'rb') as f:
            return pickle.load(f)

    def fingerprint_file(self, path, algo='sha256'):
        """Fingerprint a file by running all of our bytes through a hashing function.

        Args:
            path: The directory to fingerprint to.
            algo: The hashing algorithm to use. By default, it's set to 'sha256'.
        """

        hash_func = hashlib.new(algo)
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
            return hash_func.hexdigest()

    def get_tree(self, root, level=0):
        """Recursive function to be able ot visualize the tree.

        Args:
            root: The current node we are starting from.
            level: Used to figure out how much to indent.
        """

        #Create a string of spaces, There should be three times the value of level spaces.
        tree_str = " " * (3 * level)
        #Add to the string the '|' Character.
        tree_str += "|"
        #Add to the string '-' characters. Add three for each level.
        tree_str += "-" * (3 * level)

        #Check if the current node (root) is a DirectoryNode. If it is add the current node's name and a newline to the
        #string. This should add the entire path of the directory to the string.
        if isinstance(root, DirectoryNode):
            tree_str += f"{root.name}\n"
            #If it was not a directory, add only the part of the path that is the file's name. For instance if you had
            #/SavedStuff/Documents/my_file, only add 'my_file' to the string.
            for child in root.children.values():
                tree_str += self.get_tree(child, level + 1)
        else:
            #If the node is a directory, loop over every child, and call the function recursively with that child. Pass the
            #value of level + 1 for the recursive call.
            tree_str += f"{Path(root.name).name}\n"

        #Return the string
        return tree_str

    def find_files_and_folders(self, directory):
        """Takes a directory, and recursively lists all of the files and folders within it."""

        #using pathlib library to create a Path object.
        path = Path(directory)

        #this will be the file (or folder)'s unique id.
        inode = path.stat().st_ino

        directorynode = DirectoryNode(path.absolute(), inode)

        #get a list of all the files and folders in the current dictionary.

        #Loop over that list
        for entry in path.iterdir():
            #for each iteration of the loop, get the st_ino and store it to a variable.
            entry_stat = entry.stat()
            inode = entry_stat.st_ino
            #call the is_dir method on the current object from the list, if it returns true, createa  variable called
            #sub_node and set it equal to self.find_files_and_folder
            if entry.is_dir():
                sub_node = self.find_files_and_folders(entry)
                directorynode.add_child(sub_node)
            else:
                #if the call is false, we should be dealing with a file and not a directory.
                newfile = FileNode(entry.absolute(), inode, entry_stat.st_size)

                #add the new FileNode to the DirectoryNode create above
                directorynode.add_child(newfile)
        return directorynode

    def get_rest(self, node, removed=True):
        """Helper function to start at a node, and make a list of strings that provide info about children nodes.

        Args:
            node: The node to start at.
            removed (bool): To determine whether we are removing or not. Defaults to True.

        Returns:
            lst: The list of strings the function creates.
        """

        # Create an empty list
        lst = []

        #Base case is when a node has no more children nodes.
        if not isinstance(node, DirectoryNode) or not node.children:
            return lst

        # iterate over any children that the node might have
        for child in node.children.values():
            # then add a string of the form 'Added' or 'Removed' depending on whether the removed parameter was True or False
            if removed:
                lst.append((child.name, 'Removed'))
            else:
                lst.append((child.name, 'Added'))
            # Call itself recursively on any directory nodes it encounters.
            if isinstance(child, DirectoryNode):
                lst.extend(self.get_rest(child, removed))

        # return the list of strings the function creates
        return lst

    def compare_trees(self, tree1, tree2):
        """Compare two trees.

        Args:
            tree1: The first tree to compare.
            tree2: The second tree to compare.
        """

        #differences will hold strings with info about differences in two trees.
        differences = []

        #our base cases are when either tree1 or tree2 are empty. In those cases they will hold None.
        if not tree1:
            tree1 = None
            return self.get_rest(tree2, removed=False)
        if not tree2:
            tree2 = None
            return self.get_rest(tree1, removed=True)

        if not isinstance(tree1, DirectoryNode) or not isinstance(tree2, DirectoryNode):
            return differences

        #make two sets, the dictionaries are keyed on the files' inodes
        keys1 = set(tree1.children.keys())
        keys2 = set(tree2.children.keys())

        #find the difference of the second set from the first
        difference = keys2 - keys1

        #iterate over the difference.
        for dif in difference:
            #For each entry in the difference, add an entry to our differences list that says something along the lines of "Added ".
            current_node = tree2.children[dif]
            differences.append((current_node.name, 'Added'))

            # Get the Node from the second tree's children with the current key.
            currentkey = tree2.children[dif]

            # Call get_rest on that Node with removed=False. Extend the differences list with the list that you got back from get_rest by using the extend() function of lists.
            # This purpose of this code is to show which files have been added to a Node since our last audit.
            currentlst = self.get_rest(currentkey, removed=False)
            differences.extend(currentlst)

        #do the same fo keys1-keys2. instead of an add message for each entry, provide a Removed <filename> message.
        #dont forget to use remove=True in your call to get_rest

        for dif in keys1 - keys2:
            current_node = tree1.children[dif]
            differences.append((current_node.name, 'Removed'))
            currentlst = self.get_rest(current_node, removed=True)
            differences.extend(currentlst)

        #find common keys in both trees
        intersection = keys1 & keys2

        #iterate over the intersection.
        for common_key in intersection:
            #retrieve the nodes for the common key
            node1 = tree1.children[common_key]
            node2 = tree2.children[common_key]

            #if both nodes are directories and their sizes differ, record the change.
            if isinstance(node1, DirectoryNode) and isinstance(node2, DirectoryNode):
                if node1.size != node2.size:
                    differences.append((node1.name, f'Size changed from {node1.size} to {node2.size}'))

                #recursively compare the children of the directory nodes.
                differences.extend(self.compare_trees(node1, node2))

            #if both nodes are files, compare their fingerprints.
            elif isinstance(node1, FileNode) and isinstance(node2, FileNode):
                if node1.fingerprint != node2.fingerprint:
                    differences.append((node1.name, f'Fingerprint changed from {node1.fingerprint} to {node2.fingerprint}'))

        return differences

    def audit(self):
        """Run an audit of the configured path."""

        print(f"Audit started at {self.__start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            self.__old_root = self.read_tree(self.__input_file)
        except OSError:
            self.__old_root = None

        self.__new_root = self.find_files_and_folders(self.__path)

        differences = self.compare_trees(self.__old_root, self.__new_root)

        self.write_tree(self.__new_root, self.__output_file)

        end_time = datetime.datetime.now()
        print(f'Audit finished at {end_time.strftime("%Y-%m-%d %H:%M:%S")}')

        if self.__tree:
            print(self.get_tree(self.__new_root))

        if len(differences) == 0:
            print('No differences were found.')
        else:
            for name, change in differences:
                print(f'{change}: {name}')










