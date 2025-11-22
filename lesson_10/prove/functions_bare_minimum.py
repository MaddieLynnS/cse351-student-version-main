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
When server returns none, that means you have the whole tree
So get family, then for husband and wife separately, call their family based off parent_id
New thread when calling the next generation up (when call family from the server)


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
THREADS = 50

# collection of people and families
# retrieved = server details, API calls = sum of server details
# depth/breadth how to traverse, but not really when to process
# get the family, find parents, start threads to find parent families, then process current family
# get the family, make a Family, add Family to tree, call for husband, add him as a Person to Tree, start threads (pass in Tree), make all the children, add children to Tree
# check for child I came from to make sure I don't add them again

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree:Tree):
    # since this is main thread, make an add_to_tree lock
    add_to_tree = threading.Lock()
    
    data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    #print(f"Here is the data: {data}")
    family = Family(data)
    #print(family)
    with add_to_tree:
        tree.add_family(family)

    # use ids to get husband and wife, then get their data from API
    husband_id = family.get_husband()
    wife_id = family.get_wife()

    husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
    wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')

    # make them both people and add them to the tree
    husband = Person(husband_data)
    wife = Person(wife_data)
    with add_to_tree:
        tree.add_person(husband)
        tree.add_person(wife)

    # recursively look at each person's original family via their parent_id
    # will also eventually need threads to handle this as well
    t = threading.Thread(target=recursive_people, args=(husband.get_parentid(), tree, add_to_tree))
    wt = threading.Thread(target=recursive_people, args=(wife.get_parentid(), tree, add_to_tree))

    t.start()
    wt.start()

    # then, make all the children and add them to the tree as well
    for i in family.get_children():
        if not tree.does_person_exist(i):
            child = Person(get_data_from_server(f'{TOP_API_URL}/person/{i}'))
            with add_to_tree:
                tree.add_person(child)

    t.join()
    wt.join()

def recursive_people(family_id, tree: Tree, add_to_tree: threading.Lock):
    #make API call, then see if both parents are None, meaning that there are no more generations
    data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    #print(f"Here is the data: {data}")
    if (data is None):
        return
    
    family = Family(data)
    #print(family)
    with add_to_tree:
        tree.add_family(family)

    # use ids to get husband and wife, then get their data from API
    husband_id = family.get_husband()
    wife_id = family.get_wife()

    husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
    wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')

    # make them both people and add them to the tree

    husband = Person(husband_data)
    wife = Person(wife_data)
    with add_to_tree:
        tree.add_person(husband)
        tree.add_person(wife)

    # use threads to recursively look at each person's original family via their parent_id
    t = threading.Thread(target=recursive_people, args=(husband.get_parentid(), tree, add_to_tree))
    wt = threading.Thread(target=recursive_people, args=(wife.get_parentid(), tree, add_to_tree))

    t.start()
    wt.start()

    for i in family.get_children():
        if not tree.does_person_exist(i):
            child = Person(get_data_from_server(f'{TOP_API_URL}/person/{i}'))
            with add_to_tree:
                tree.add_person(child)

    t.join()
    wt.join()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree:Tree):
    # this one doesn't use recursion so it might be a bit simpler - OR MAYBE NOT

    #initialize queue and lock
    processing_queue = queue.Queue()
    add_to_tree = threading.Lock()

    processing_queue.put(family_id)

    data = get_data_from_server(f'{TOP_API_URL}/family/{processing_queue.get()}')
    # print(f"Here is the data: {data}")
    family = Family(data)
    # print(family)
    with add_to_tree:
        tree.add_family(family)

    # use ids to get husband and wife, then get their data from API
    husband_id = family.get_husband()
    wife_id = family.get_wife()

    husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
    wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')

    # make them both people and add them to the tree
    husband = Person(husband_data)
    wife = Person(wife_data)
    with add_to_tree:
        tree.add_person(husband)
        tree.add_person(wife)

    processing_queue.put(husband.get_parentid())
    processing_queue.put(wife.get_parentid())

    for i in family.get_children():
        if not tree.does_person_exist(i):
            child = Person(get_data_from_server(f'{TOP_API_URL}/person/{i}'))
            with add_to_tree:
                tree.add_person(child)

    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=call_API_worker, args=(tree, add_to_tree, processing_queue))
        t.start()
        threads.append(t)

    # for _ in range(THREADS):
    #     processing_queue.put(None)

    for t in threads:
        t.join()


    # uses start id and like starts with the family, puts it in the queue, then gets individuals and puts them in the queue too
    # it looks like putting a family in, then getting husband and wife and putting them in the queue, then getting their parents
    # things get pulled from queue and processed in a specific order
    # each thread would take care of the next API call, like worker threads

def call_API_worker(tree:Tree, add_to_tree: threading.Lock, process_queue : queue.Queue):
    while True:
        next_id = process_queue.get()
        if next_id is None:
            break
        
        #get data from API to process
        data = get_data_from_server(f'{TOP_API_URL}/family/{next_id}')
        # print(f"Here is the data: {data}")
        if (data is None):
            continue
        
        family = Family(data)
        #print(family)
        with add_to_tree:
            tree.add_family(family)

        # use ids to get husband and wife, then get their data from API
        husband_id = family.get_husband()
        wife_id = family.get_wife()

        husband_data = get_data_from_server(f'{TOP_API_URL}/person/{husband_id}')
        wife_data = get_data_from_server(f'{TOP_API_URL}/person/{wife_id}')

        # make them both people and add them to the tree
        husband = Person(husband_data)
        wife = Person(wife_data)
        with add_to_tree:
            tree.add_person(husband)
            tree.add_person(wife)

        process_queue.put(husband.get_parentid())
        process_queue.put(wife.get_parentid())

        for i in family.get_children():
            if not tree.does_person_exist(i):
                child = Person(get_data_from_server(f'{TOP_API_URL}/person/{i}'))
                with add_to_tree:
                    tree.add_person(child)

    process_queue.put(None)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # this means that it's like a limited number of consumer threads
    print("the other breadth I like to eat")
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    pass