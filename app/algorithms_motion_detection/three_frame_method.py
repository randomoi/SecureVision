import cv2
import numpy as np

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """

# constants 
KERNEL_SIZE_GAUSSIAN_BLUR = (3, 3)  # kernel size for gaussian blur
KERNEL_SIZE_DILATION = (5, 5)  # kernel size for dilation
THRESHOLD_VALUE_BINAEY = 40  # threshold for binary thresholding
THRESHOLD_VALUE_MAX = 255  # max value 
DILATION_ITERATIONS = 2  # iterations 
STD_DEVIATION_GAUSSIAN_BLUR = 0 # standard deviation for gaussian blur (set to 0 -> calculated based on kernel size)

# the method takes in current frame, a frame from 1 step ago and a frame from 2 steps ago (all frames in grayscale) for motion detection
def three_frame_differencing_method(current_frame, previous_frame_1, previous_frame_2):
    if previous_frame_1 is None or previous_frame_2 is None:
        return None
    
    # applies gaussian blur on each frame for noise reduction 
    blurred_current_frame = cv2.GaussianBlur(current_frame, KERNEL_SIZE_GAUSSIAN_BLUR, STD_DEVIATION_GAUSSIAN_BLUR)
    blurred_previous_frame_1 = cv2.GaussianBlur(previous_frame_1, KERNEL_SIZE_GAUSSIAN_BLUR, STD_DEVIATION_GAUSSIAN_BLUR)
    blurred_previous_frame_2 = cv2.GaussianBlur(previous_frame_2, KERNEL_SIZE_GAUSSIAN_BLUR, STD_DEVIATION_GAUSSIAN_BLUR)

    # calculates absolute diff between current and previous frames
    difference_1 = cv2.absdiff(blurred_previous_frame_1, blurred_current_frame)
    difference_2 = cv2.absdiff(blurred_previous_frame_2, blurred_current_frame)

    # used bitwise OR operator to combine differences from frames
    merged_difference_image = cv2.bitwise_or(difference_1, difference_2)

    # applies binary thresholding
    _, thresholded_image = cv2.threshold(merged_difference_image, THRESHOLD_VALUE_BINAEY, THRESHOLD_VALUE_MAX, cv2.THRESH_BINARY)

    # fills the gaps 
    kernel = np.ones(KERNEL_SIZE_DILATION, np.uint8)
    dilated_binary_mask = cv2.dilate(thresholded_image, kernel, iterations=DILATION_ITERATIONS)
    
    # returns binary mask with detected motion
    return dilated_binary_mask 


# Reference: 
# https://github.com/PacktPublishing/Artificial-Intelligence-with-Python/blob/master/Chapter%2013/code/frame_diff.py
# https://pdf.sciencedirectassets.com/278653/1-s2.0-S1877705812X00043/1-s2.0-S1877705812003864/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEN3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJHMEUCIQChfFTEyM8DVSkS%2B%2BBgXCZqR7AIfZ04WSJo3%2BcNpy9o3QIgVXnLmABnysbrJJrXoks0PYDi3LvykGmF3QuYu4vBna0qvAUIpf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDG83JISGD35qiyKl2iqQBZG8peSh80uKgSiRDLJ0H3P9TWeu9Q%2Bp%2F2GFwmCFGQsfsr96ofocPCiFTThQ8HJKD0g55cqUA%2FHPWXvLnO7%2FPi16eJ2ItesfXnt94owzRfybbSxFL%2B2NKuXgZVVRcrtlJQea2CidwroqnOLfGkcP7J23%2BkDwcu6BFzMNSHkysZAkatPPxLAKWvWG987Y81saBE3czZk6GkqUek%2FtYQp%2BA5yBVFy9ltDX6uraMiAkw62wY7ThK3IzwxrK4tidb10lSdAqLtkHJKeP%2FKG9fw2J973%2FNU6GULy%2B3aZZZzMLGPo1YGa81FAXLPdfRqvxfaXJL4r%2F4%2FE872MC%2F3yJVFekdZxYOzIBdu0rLVRffd0BpREmPtwsbiZw43JStjpGT0MkuGn4roa9mwCeCbXZj%2BZJZCM4WA39QpcI9OoFbyPP8qcti4a%2FzOZPYL2CF2rWsKbeDWbtK11t0%2Fh8cNaSmjtvNz6pxO1wLgfhctzDUXZwXUvfjCNPSw5NAGg9clF2W1UIbi54cUDUgw2DPsUX5BCLyjcIq9ZEz8e5YqGt%2FaXW7ZkWsmpSKMbVPv5ixGVzYy%2BcLH7BIOnxFd0kY2dgW8HdYI2VBoC3N62wj1T2iAqma8zglWhJEu3JsbXmqrn3Mh8b5QGe3uWS%2BuEs6tEnLoOBGUrwVpLJ%2F%2FbPlOeBCzu%2Ffc46LFkLI9Vi3yF2oicVl%2FQ85DGvHgKu5NaZYE5342pKxDIfkomfsSgcXWLH9R%2FT%2Faq5odbdTDT35akApmhoizRmdKLqDyCAC9r3ygVgvVU%2BxbeFAv6nyt47mmOL6BAMIn%2FcYpguK64yGW4BRCLn8kflVkpKxq1svAGWbIxqqaAEZlAYrs1Go7XoEnMd%2BETCz07%2BMNGlg64GOrEB2SAVlBmEGHo4EZ1fmGKpaJ9Ob3rVREfkP013AHoeIXX2a2xh7lXlGjyEjhz6rcREmu8cxv7HINvtiyHKKmLU2Ldt7k5eK60HslatGWOTJyWf15DGAqteeAWvi5LpNIHgQiISXk0nU%2BulHGl0TaAdl%2FizNpaOcMdLRDKneGShW%2FCyRfGEJEhR357qTEE%2BSqtqS8aHSH76AM1Q5mUa3XYgeeo09kquB05weINBzefm1pxn&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20240205T132938Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY7VVRG3XP%2F20240205%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=204309cd16b73bdcb455d2f5356905b3e236f780db4e069a7afc370577113ad8&hash=121581cef7baf12293a12b7b754a3396cabbe2b14013c0e42e38498cb406209a&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1877705812003864&tid=spdf-2a473cbc-c9de-4ae3-85fc-d34d4a41d5f3&sid=caf536f63e33494937294e745c21625d9d22gxrqa&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=1e035f52520d5c50045c5b&rr=850b80d98ab9372d&cc=de
# https://scialert.net/fulltext/?doi=itj.2014.1863.1867
# https://www.researchgate.net/publication/352240573_Deep_Learning-Driven_Gaussian_Modeling_and_Improved_Motion_Detection_Algorithm_of_the_Three-Frame_Difference_Method
# https://core.ac.uk/download/pdf/53189939.pdf
# https://debuggercafe.com/moving-object-detection-using-frame-differencing-with-opencv/
# https://docs.opencv.org/4.x/
# https://pyimagesearch.com/2021/01/19/opencv-bitwise-and-or-xor-and-not/
# https://www.tutorialspoint.com/how-to-perform-bitwise-or-operation-on-two-images-in-opencv-python
# https://docs.opencv.org/4.x/d0/d86/tutorial_py_image_arithmetics.html
# https://medium.com/@rohit-krishna/coding-gaussian-blur-operation-from-scratch-in-python-f5a9af0a0c0f
# https://stackoverflow.com/questions/65150972/difference-between-absdiff-and-normal-subtraction-in-opencv
# https://docs.opencv.org/master/d2/d55/group__bgsegm.html
# https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2
# https://sokacoding.medium.com/simple-motion-detection-with-python-and-opencv-for-beginners-cdd4579b2319
# https://www.youtube.com/watch?v=GeqSF8EV1Gs
# https://pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/
# https://blog.kronis.dev/tutorials/diy-surveillance-motion-detection-with-opencv-and-python
# https://answers.opencv.org/question/181877/frame-difference-based-tracker-stuck-with-first-frame/
# https://forum.image.sc/t/gaussian-blur-radius-scaled-units-micron/81865
# https://docs.opencv.org/3.4/d4/d13/tutorial_py_filtering.html
# https://pyimagesearch.com/2021/04/28/opencv-smoothing-and-blurring/
# https://stackoverflow.com/questions/65730493/cv2-gaussianblur-at-multiple-kernel-sizes
# https://www.opencv-srf.com/2018/03/gaussian-blur.html
# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
# https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html
# https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
# https://numpy.org/doc/stable/reference/generated/numpy.ones.html
# https://www.geeksforgeeks.org/numpy-ones-python/
# https://gist.github.com/gonzalo123/df3e43477f8627ecd1494d138eae03ae?permalink_comment_id=3514815
# https://answers.opencv.org/question/191387/detect-slow-gradual-change-in-background-with-live-video-and-python-3/
# https://stackoverflow.com/questions/71737841/opencv-c-sharp-frame-differencing
# https://stackoverflow.com/questions/67117928/how-to-decide-on-the-kernel-to-use-for-dilations-opencv-python

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """
