import cv2
import numpy as np

""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """


# constants
RGB_FACTOR = 255.0
OFFSET_CHROMATICITY_DIVISOR = 1e-6
INDEX_CHANNEL_RED = 0
INDEX_CHANNEL_BLUE = 2
INDEX_CHANNEL_GREEN = 1

class McKennaMethod:
    #  initialize method with parameters
    def __init__(self, alpha=0.8, beta=0.1, chromaticity_edge_thresholds=(3, 1)):
        self.alpha = alpha  # learning rate for updating gaussian model
        self.beta = beta  # learning rate for updating edge model
        self.chromaticity_edge_thresholds = chromaticity_edge_thresholds  # chromaticity_value and edge chromaticity_edge_thresholds
        self.mean_gaussian = None  # gaussian model mean
        self.variance_gaussian = None  # gaussian model variance
        self.mean_edge = None  # edge mean
        self.variance_edge = None  # edge variance

    # processes one frame (RBG image)
    def process_one_frame(self, frame):
        # processes one frame 
        frame = frame.astype(np.float32) / RGB_FACTOR
        
        # calculates chromaticity_value values for the frame
        chromaticity_value = frame[:, :, [INDEX_CHANNEL_RED, INDEX_CHANNEL_BLUE]] / (frame[:, :, INDEX_CHANNEL_GREEN][:, :, np.newaxis] + OFFSET_CHROMATICITY_DIVISOR)

        # calculates x,y gradient to indicate x,y edges in the frame
        x_gradient, y_gradient = np.gradient(frame, axis=(0, 1))
        x_edges, y_edges = x_gradient, y_gradient
   
        if self.mean_gaussian is None:
            # calculate mean and variance for chromaticity and edges
            self.mean_gaussian = np.mean(chromaticity_value, axis=(0, 1))
            self.variance_gaussian = np.var(chromaticity_value, axis=(0, 1))
            self.mean_edge = np.mean(np.stack([x_edges, y_edges]), axis=(0, 1, 2))
            self.variance_edge = np.var(np.stack([x_edges, y_edges]), axis=(0, 1, 2))

        # by using calculated means/variances updates gaussian and edge models 
        self.mean_gaussian = self.alpha * np.mean(chromaticity_value, axis=(0, 1)) + (1 - self.alpha) * self.mean_gaussian
        self.variance_gaussian = self.alpha * np.var(chromaticity_value, axis=(0, 1)) + (1 - self.alpha) * self.variance_gaussian
        self.mean_edge = self.beta * np.mean(np.stack([x_edges, y_edges]), axis=(0, 1, 2)) + (1 - self.beta) * self.mean_edge
        self.variance_edge = self.beta * np.var(np.stack([x_edges, y_edges]), axis=(0, 1, 2)) + (1 - self.beta) * self.variance_edge

        # calculate difference for chromaticity_value
        chromaticity_difference = np.abs(chromaticity_value - self.mean_gaussian)
        
        # calculate difference for edge
        edge_difference_x = np.abs(x_edges - self.mean_edge)
        edge_difference_y = np.abs(y_edges - self.mean_edge)
        edge_difference_sum = np.sum(np.stack([edge_difference_x, edge_difference_y]), axis=-1)
  
        # make sures that compatible for broadcasting - shape: (360, 640, 1)
        edge_difference_sum = edge_difference_sum[..., np.newaxis]  

        # make sure that it's scalar for broadcasting
        scalar_edge_variance = self.variance_edge if np.isscalar(self.variance_edge) else np.mean(self.variance_edge)

        # pixels classification (foreground or background) based on the calculated thresholds
        mckenna_foreground_mask = (chromaticity_difference > self.chromaticity_edge_thresholds[0] * self.variance_gaussian) | \
                        (edge_difference_sum > self.chromaticity_edge_thresholds[1] * scalar_edge_variance)
     
        # update shape and convert to a three channel image
        mckenna_foreground_mask = mckenna_foreground_mask.any(axis=-1).astype(np.uint8)
        mckenna_foreground_mask = cv2.cvtColor(mckenna_foreground_mask, cv2.COLOR_GRAY2BGR)
      
        # return foreground mask with detected motion
        return mckenna_foreground_mask

# References:
# https://www.researchgate.net/profile/Zoran-Duric/publication/221292566_Tracking_Interacting_People/links/00b49517ed34926c3c000000/Tracking-Interacting-People.pdf
# https://www2.informatik.uni-stuttgart.de/bibliothek/ftp/medoc_restrict.ustuttgart_fi/DIP-2982/DIP-2982.pdf
# https://www.researchgate.net/publication/224254837_Evaluation_of_background_subtraction_techniques_for_video_surveillance
# https://numpy.org/doc/stable/reference/generated/numpy.var.html
# https://en.wikipedia.org/wiki/Image_gradient
# https://docs.opencv.org/4.x/df/d5d/tutorial_py_bg_subtraction.html
# https://answers.opencv.org/question/175684/video-frame-to-numpy-array/
# https://github.com/kkroening/ffmpeg-python/issues/246
# https://github.com/kkroening/ffmpeg-python/issues/78
# https://stackoverflow.com/questions/45670487/numpy-cov-exception-float-object-has-no-attribute-shape
# https://de.mathworks.com/matlabcentral/answers/487068-i-need-help-with-my-code-using-gaussian-elimination
# https://www.sharpsightlabs.com/blog/numpy-variance/
# https://www.geeksforgeeks.org/compute-the-mean-standard-deviation-and-variance-of-a-given-numpy-array/
# https://numpy.org/doc/stable/reference/generated/numpy.isscalar.html
# https://numpy.org/doc/stable/reference/generated/numpy.absolute.html
# https://numpy.org/doc/stable/reference/generated/numpy.gradient.html
# https://numpy.org/doc/stable/reference/generated/numpy.var.html
# https://machinelearningmastery.com/learning-rate-for-deep-learning-neural-networks/
# https://stackoverflow.com/questions/54170933/convert-a-one-dimensional-dataframe-into-a-3-dimensional-for-rgb-image
# https://de.mathworks.com/help/matlab/ref/im2frame.html

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. """
