"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Maddie Smith :)

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

I would start with a base path, then have each thread get their own copy of the path to add to. Only the thread
that makes it to the end of the maze would return its path

Why would it work?

The path up to the split would be passed to a new thread, and it would add to it from there. If it doesn't reach the end,
it doesn't return anything. That means only the successful thread will return a complete path, and will also avoid the 
need for any locks since each thread would be altering its own version of the path

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


#race condition, colliding threads >:(
#return true when reaches end, otherwise false?
#call get_color when creating a new thread
#locks for each individual space??
#list can be passed in to put all the threads in
def recursive_function(maze: Maze, position, threads_list, stop_lock: threading.Lock, move_lock: threading.Lock, color):
    x, y = position

    global stop
    global thread_count

    if stop:
        return
    
    #print(f"It's a new day yo. Here's the pos: ({x}, {y})")
    if maze.at_end(x,y):
        stop_lock.acquire()
        stop = True
        stop_lock.release()
        print("All threads joined!")
        return True
        
    possible_moves = maze.get_possible_moves(x, y)
    for move in possible_moves:
        move_x, move_y = move
        with move_lock:
            if not maze.can_move_here(move_x,move_y):
                possible_moves.remove(move)

    if not possible_moves:
        return

    if (len(possible_moves) > 1):
        for i in range(len(possible_moves)-1):
            move_x, move_y = possible_moves[i]
            # make a new thread for all but last
            new_color = get_color()
            with move_lock:
                if maze.can_move_here(move_x, move_y):
                    maze.move(move_x, move_y, new_color)
            t = threading.Thread(target=recursive_function, args=(maze,(move_x,move_y), threads_list, stop_lock, move_lock, new_color))
            t.start()
            threads_list.append(t)

    # for move in possible_moves:
    #     print(move)            
    move_x = possible_moves[-1][0]
    move_y = possible_moves[-1][1]
    with move_lock:
        if maze.can_move_here(move_x, move_y):
            maze.move(move_x, move_y, color)
    recursive_function(maze, (move_x,move_y), threads_list, stop_lock, move_lock, color)
                



def solve_find_end(maze: Maze):
    """ Finds the end position using threads. Nothing is returned. """
    # this is my defacto "main"
    # lock/variable for if done, join all and return true
    # When one of the threads finds the end position, stop all of them.
    # create move_lock in here, if it returns false
    global stop
    global thread_count
    stop = False
    maze_threads = []
    # create locks
    move_lock = threading.Lock()
    stop_lock = threading.Lock()
    # get color for initial call
    t = threading.Thread(target=recursive_function, args=(maze, maze.get_start_pos(), maze_threads, stop_lock, move_lock, get_color()))
    t.start()
    print("thread started")
    maze_threads.append(t)

    for t in maze_threads:
        t.join()

    thread_count = len(maze_threads)




def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()