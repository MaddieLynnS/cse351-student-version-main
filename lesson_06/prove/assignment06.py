"""
Course: CSE 351
Assignment: 06
Author: Maddie Smith :)

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

#Processes- change to test how fast we can make this thing
SMOOTH_PROCESSES = 75
GRAY_PROCESSES = 100
EDGY_PROCESSES = 50

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def add_from_folder_to_queue(input_folder, output_queue: mp.Queue, output_folder):
    print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")
    for filename in os.listdir(input_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(input_folder, filename)
        output_image_path = os.path.join(output_folder, filename)
        output_queue.put((input_image_path, output_image_path))



# ---------------------------------------------------------------------------
def process_images_in_queue( input_queue,               # input queue with all images
                             output_folder,             # output folder for processed images
                             barrier,                   # barrier that will ensure the processes wait
                             processing_function,       # function to process the image (ie., task_...())
                             load_args=None,            # Optional args for cv2.imread
                             processing_args=None):     # Optional args for processing function

    create_folder_if_not_exists(output_folder)
    processed_count = 0
    #print(f"Processing images from queue and putting in '{output_folder}'")

    while True:
        img_tuple_to_process = input_queue.get()

        if img_tuple_to_process is None:
            break

        #if there's something in the queue, reassign variable names
        input_image_path = img_tuple_to_process[0]
        output_image_path = img_tuple_to_process[1]

        try:
            # Read the image
            if load_args is not None:
                img = cv2.imread(input_image_path, load_args)
            else:
                img = cv2.imread(input_image_path)
            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            # Save the processed image
            cv2.imwrite(output_image_path, processed_img)

            processed_count += 1
            #print(f"{processed_count} going in {output_folder}") #COMMENT OUT WHEN DONE TESTING
        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")

    input_queue.put(None)
    print(f"Finished processing. {processed_count} images processed into '{output_folder}'.")

    #I Believe this will make the processes wait until all of them are done, then will let the program move on
    #print(f"WAIT!! {barrier.wait()}")
    if barrier.wait() == 0:
        input_queue.close()

# ---------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    # - you are free to change anything in the program as long as you
    #   do all requirements.

    #so I'll need to change the process implementation completely to work with tuples instead?
    #pull images from faces folder, add to queue as tuple
    #need to wait until they're all in the queue before starting processes

    # - create queues
    pre_smooth_queue = mp.Queue()
    pre_grayscale_queue = mp.Queue()
    pre_edge_queue = mp.Queue()

    # - create barriers
    #possibly will need barrier for each of the processes? yes
    smooth_b = mp.Barrier(SMOOTH_PROCESSES+1)
    gray_b = mp.Barrier(GRAY_PROCESSES+1)
    edgy_b = mp.Barrier(EDGY_PROCESSES+1)

    # - create the three processes groups
    smoothing_processes = []
    grayscale_processes = []
    edgy_processes = []


    # --- Step 1: Smooth Images ---
    add_from_folder_to_queue(INPUT_FOLDER, pre_smooth_queue, STEP1_OUTPUT_FOLDER)
    pre_smooth_queue.put(None)
    for _ in range(SMOOTH_PROCESSES):
        p = mp.Process(target=process_images_in_queue, args=(pre_smooth_queue, STEP1_OUTPUT_FOLDER, smooth_b,
                             task_smooth_image), kwargs={"processing_args": (GAUSSIAN_BLUR_KERNEL_SIZE,)})
        p.start()
        smoothing_processes.append(p)

    # process_images_in_queue(pre_smooth_queue, STEP1_OUTPUT_FOLDER, task_smooth_image,
    #                          processing_args=(GAUSSIAN_BLUR_KERNEL_SIZE,))
    
    smooth_b.wait()
    #the way mine is set up, we need to wait until the first one finishes to start the next step because the
    #add_from_folder function adds them all at once

    # --- Step 2: Convert to Grayscale ---
    add_from_folder_to_queue(STEP1_OUTPUT_FOLDER, pre_grayscale_queue, STEP2_OUTPUT_FOLDER)
    pre_grayscale_queue.put(None)
    for _ in range(GRAY_PROCESSES):
        p = mp.Process(target=process_images_in_queue, args=(pre_grayscale_queue, STEP2_OUTPUT_FOLDER, gray_b, task_convert_to_grayscale))
        p.start()
        grayscale_processes.append(p)
    # process_images_in_queue(pre_grayscale_queue, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale)

    gray_b.wait()

    # --- Step 3: Detect Edges ---
    add_from_folder_to_queue(STEP2_OUTPUT_FOLDER, pre_edge_queue, STEP3_OUTPUT_FOLDER)
    pre_edge_queue.put(None)
    for _ in range(EDGY_PROCESSES):
        p = mp.Process(target=process_images_in_queue, args=(pre_edge_queue, STEP3_OUTPUT_FOLDER, edgy_b, task_detect_edges,
                                    cv2.IMREAD_GRAYSCALE), kwargs={"processing_args": (CANNY_THRESHOLD1, CANNY_THRESHOLD2)})
        p.start()
        edgy_processes.append(p)
    # process_images_in_queue(pre_edge_queue, STEP3_OUTPUT_FOLDER, task_detect_edges,
    #                          load_args=cv2.IMREAD_GRAYSCALE,        
    #                          processing_args=(CANNY_THRESHOLD1, CANNY_THRESHOLD2))
    
    edgy_b.wait()
    for p in smoothing_processes + grayscale_processes + edgy_processes:
        p.join()

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
