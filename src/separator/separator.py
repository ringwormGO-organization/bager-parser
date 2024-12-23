# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator entry file

import matplotlib.pyplot as plt
import numpy as np
import cv2
from shapely.geometry import LineString, Polygon

class Separator:

    # Initialize all variables
    def __init__(self, elements):
        self.elements = elements

        # Variable holding grid / divisions 
        self.grid = None

        # Variable holding polygon
        self.polygon = None

        # Variable holding grid size
        grid_size = 20

        polygon_result:int = self.create_polygon()
        if polygon_result != 0:
            return
        
        self.create_divisions(grid_size)

    # Create polygon from extracted entities
    def create_polygon(self) -> int:
        all_coords = []

        if len(self.elements['LINES']):
            for line in self.elements['LINES']:
                all_coords.extend(line.coords)

        elif len(self.elements['LWPOLYLINE']):
            for polyline in self.elements['LWPOLYLINE']:
                all_coords.extend(polyline.get_points('xy'))

        elif len(self.elements['POINTS']):
            # Sort points by angle or other strategy for meaningful polygon formation
            points = np.array(self.elements['POINTS'])
            hull = cv2.convexHull(points)  # Ensure a closed convex shape

            self.polygon = Polygon(hull.squeeze())
            return 0

        else:
            print("No element found to create polygon!")
            return 1

        self.polygon = Polygon(all_coords)
        return 0

    # Divide polygon into smaller pieces
    def create_divisions(self, division_number):
        min_x, min_y, max_x, max_y = self.polygon.bounds
        y_points = np.arange(min_y, max_y, division_number)
        
        horizontal_lines = []
        for y in y_points:
            horizontal_line = LineString([(min_x, y), (max_x, y)])
            horizontal_lines.append(horizontal_line)
        
        clipped_lines = []
        for line in horizontal_lines:
            clipped_line = self.polygon.intersection(line)
            if not clipped_line.is_empty:
                clipped_lines.append(clipped_line)
        
        self.grid = clipped_lines

    # Plot lines (LineString) on the screen
    def plot_lines(self):
        fig, ax = plt.subplots(figsize=(8, 8))

        # Loop over each detected line in the list
        for line in self.elements['LINES']:
            if isinstance(line, LineString):
                x, y = line.xy  # Get the coordinates of the line
                ax.plot(x, y, color='blue', lw=2)  # Plot the line in blue with a line width of 2

        # Show the plot with the lines
        plt.title("Detected Lines")
        plt.gca().set_aspect('equal', adjustable='box')  # Set equal aspect ratio
        plt.show()

    # Plot created shape (Polygon) on the screen
    def plot_shape(self):
        x, y = self.polygon.exterior.xy  # Extract x and y coordinates
        plt.figure(figsize=(8, 8))
        plt.plot(x, y, color='blue', linewidth=2)
        plt.fill(x, y, color='lightblue', alpha=0.5)  # Optional: fill the polygon
        plt.title('Polygon Plot')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.grid(True)
        plt.show()
    
    # Plot divided polygon on the screen
    def plot_grid(self) -> None:
        fig, ax = plt.subplots()
    
        # Plot the polygon
        x, y = self.polygon.exterior.xy
        ax.plot(x, y, color='black')

        # Plot the divisions
        for division in self.grid:
            if isinstance(division, LineString):
                x, y = division.xy
                ax.plot(x, y, color='blue')
            elif isinstance(division, Polygon):
                for geom in division.geoms:
                    x, y = geom.exterior.xy
                    ax.plot(x, y, color='blue')

        plt.show()

    def get_grid(self):
        return self.grid
