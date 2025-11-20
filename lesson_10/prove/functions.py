"""
Course: CSE 351, week 10
File: functions.py
Author: Maddie Smith :)

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


Person class is a data table, as is couple relationship?
Parent_id = parent/sibling family?
Family_id = married/children family?
People that are parents in one relationship will be children in another, but we only want to add them once
Person, family, tree
If guy, husband_id should be same as his own id, wife_id is wife's id
don't build a tree, just add everything that's in the tree
follow your heart when it comes to order for depth-first
create helper func

--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe what strategy you implemented to speed up part 1

<Add your comments here>


Describe what strategy you implemented to speed up part 2

<Add your comments here>


Extra (Optional) 10% Bonus to speed up part 3 (WON'T run in under ten seconds)

<Add your comments here>

"""
from common import *
import queue
import threading
# because both will require threads (which is mad unfortunate because I don't know how to organize that yet but esta bien I shall conquer at length)
# QUESTION FOR MORNING: is there sample output we get to see??
# just using stuff from common.py file right?
# where do I use stuff from the queue?
# collection of people and families
# retrieved = server details, API calls = sum of server details
# don't create functions inside of functions

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree:Tree):
    # TODO - implement Depth first retrieval
    # probbaly make a recursive function that handles taking care of this
    # use preorder (root first), inorder (root middle), or postorder (root last)
    # will also eventually need threads to handle this as well
    # TODO - Printing out people and families that are retrieved from the server will help with debugging
    print("Hey itsa me Marioooo")
    pass

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree:Tree):
    # TODO - implement breadth first retrieval
    # this one doesn't use recursion so it might be a bit simpler
    print("this be the breadth of life")
    # TODO - Printing out people and families that are retrieved from the server will help with debugging

    pass

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    print("the other breadth I like to eat")
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass