# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: 
# DESCRIPTION: image parser entry file

import os
import cv2
import numpy as np

class Image:

    # Initialize all variables
    def __init__(self, path) -> None:

        if not os.path.exists(path):
            print(f"File in path {path} does not exist!")
            print("Exiting...")

            exit(0)

        self.image = cv2.imread(path)

        self.color_gradation = False
        self.two_color_gradation = False

    def execute(self) -> None:
        # Convert image to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Use Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Apply HoughLinesP method to directly obtain line end points
        lines = cv2.HoughLinesP(
            edges,                  # Input edge image
            1,                      # Distance resolution in pixels
            np.pi / 180,            # Angle resolution in radians
            threshold=100,          # Min number of votes for valid line
            minLineLength=5,        # Min allowed length of line
            maxLineGap=10           # Max allowed gap between lines for joining them
        )

        if lines is not None:
            # Calculate the maximum and minimum line lengths
            line_lengths = [np.sqrt((x2 - x1)**2 + (y2 - y1)**2) for [[x1, y1, x2, y2]] in lines]
            max_length = max(line_lengths)
            min_length = min(line_lengths)

            # Define a threshold to classify thick vs thin lines
            length_threshold = (max_length + min_length) / 2

            # Iterate over detected lines
            for i, points in enumerate(lines):
                # Extracted points
                x1, y1, x2, y2 = points[0]

                # Calculate the length of the line
                line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                if self.color_gradation:
                    # Normalize the length to the range [0, 1]
                    norm_length = (line_length - min_length) / (max_length - min_length)

                    if self.two_color_gradation:
                        # Green to Red gradient
                        # Green (0, 255, 0) -> Red (0, 0, 255)
                        red_value = int(norm_length * 255)   # Red increases as line gets thinner
                        green_value = int(255 - norm_length * 255)  # Green decreases as line gets thinner
                        color = (0, green_value, red_value)  # BGR format: Blue, Green, Red

                    else:
                        # Light red to Dark red gradient
                        red_intensity = int(139 + norm_length * (255 - 139))  # Darker red for thicker lines
                        color = (0, 0, red_intensity)  # BGR format: (Blue, Green, Red)

                    # Set line thickness based on normalized length (optional)
                    thickness = int(1 + norm_length * 5)  # Range from 1 to 5

                else:
                    # Use two colors based on length threshold
                    if line_length >= length_threshold:
                        color = (0, 255, 0)  # Green for thicker lines
                        thickness = 4  # Thicker line

                    else:
                        color = (0, 0, 255)  # Red for thinner lines
                        thickness = 2  # Thinner line

                # Draw the lines on the image
                cv2.line(self.image, (x1, y1), (x2, y2), color, thickness)

        # Save the result image
        cv2.imwrite('detectedLines.png', self.image)
