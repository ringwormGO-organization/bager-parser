# AUTHOR Andrej Bartulin
# PROJECT: B.A.G.E.R. parser
# LICENSE: Polyform Shield License 1.0.0
# DESCRIPTION: Separator entry file

import matplotlib.pyplot as plt
import numpy as np
import cv2
from shapely.geometry import LineString, Point, Polygon, MultiPolygon

class Separator:

    # Initialize all variables
    def __init__(self, elements):
        self.elements = elements

        # [Polygon A, Polygon B]
        # [Grid of polygon A, Grid of polygon B]
        # [Division 1 of grid A, Division 1 of grid B]
        # [Division 2 of grid A, Division 2 of grid B]
        # [Division 3 of grid A, Division 3 of grid B]

        # Variable holding grids (divided shapes)
        self.grids = []

        # Variable holding polygons (undivided shapes)
        self.polygons = []

        # Variable holding grid size
        self.grid_size = 20

        polygon_result:int = self.create_polygon()
        if polygon_result != 0:
            return
        
        self.create_divisions()

    # Create polygon from extracted Shapely elements
    def create_polygon(self) -> int:
        all_coords = []
        start_point = None

        if len(self.elements) == 0:
            print("No element found to create polygons!")
            return 1

        for circle in self.elements['CIRCLE']:
            self.polygons.append(circle)

        for ellipse in self.elements['ELLIPSE']:
            self.polygons.append(ellipse)

        for line in self.elements['LINE']:
            all_coords.extend(line.coords)

            # Check if the shape is closed
            if start_point is None:
                start_point = line.coords[0]
            elif Point(line.coords[-1]).distance(Point(start_point)) < 1e-6:  # Small threshold for floating-point precision
                self.polygons.append(Polygon(all_coords))
                all_coords = []
                start_point = None

        for polyline in self.elements['LWPOLYLINE']:
            all_coords.extend(polyline.coords)

            # Check if the shape is closed
            if (polyline.coords.xy[0][0] == polyline.coords.xy[0][-1]):
                self.polygons.append(Polygon(all_coords))
                all_coords = []

        for spline in self.elements['SPLINE']:
            all_coords.extend(spline.coords)

            # Check if the shape is closed
            if len(all_coords) > 2 and all_coords[0] == all_coords[-1]:
                self.polygons.append(Polygon(all_coords))
                all_coords = []

        if len(self.elements['POINTS']):
            # Create polygons from points using convex hulls
            points = np.array(self.elements['POINTS'])
            hull = cv2.convexHull(points)

            self.polygons.append(Polygon(hull.squeeze()))

        # If there are leftover lines, create a polygon from them
        if all_coords:
            self.polygons.append(Polygon(all_coords))

        return 0
    
    def _create_rectangles_for_strip(self, polygon, horizontal_line, y):
        """
        Create rectangles from the horizontal strip formed by intersecting horizontal line with the polygon.
        The longer side will be parallel to the X-axis.
        """
        min_x, min_y, max_x, max_y = polygon.bounds
        rectangles = []

        # Identify the intersections with the polygon's boundary
        left_x = max_x
        right_x = min_x
        
        # Check the horizontal line's intersections with the polygon
        intersection = polygon.intersection(horizontal_line)
        
        if intersection.geom_type == "LineString":
            coords = list(intersection.coords)
            # Take the start and end points of the intersection as the x-boundaries
            left_x = min(coords[0][0], coords[-1][0])
            right_x = max(coords[0][0], coords[-1][0])

            # Now we create a rectangle where the long side is parallel to the X-axis
            rect = Polygon([(left_x, y), (right_x, y), (right_x, y + self.grid_size), (left_x, y + self.grid_size)])
            rectangles.append(rect)

        return rectangles

    def create_divisions(self):
        for polygon in self.polygons:
            min_x, min_y, max_x, max_y = polygon.bounds
            y_points = np.arange(min_y, max_y + self.grid_size, self.grid_size)  # Ensure it covers the top edge
            
            horizontal_lines = []
            for y in y_points:
                horizontal_line = LineString([(min_x, y), (max_x, y)])
                horizontal_lines.append(horizontal_line)
            
            clipped_lines = []
            for line in horizontal_lines:
                intersection = polygon.intersection(line)
                if not intersection.is_empty:
                    if intersection.geom_type == "LineString":
                        clipped_lines.append(intersection)
                    elif intersection.geom_type == "MultiLineString":
                        clipped_lines.extend(intersection.geoms)  # Use geoms to extract individual LineStrings
            
            self.grids.append(clipped_lines)

    # Plot lines (LineString) on the screen
    def plot_lines(self):
        fig, ax = plt.subplots(figsize=(8, 8))

        # Loop over each detected line in the list
        for line in self.elements['LINE']:
            if isinstance(line, LineString):
                x, y = line.xy  # Get the coordinates of the line
                ax.plot(x, y, color='blue', lw=2)  # Plot the line in blue with a line width of 2

        # Show the plot with the lines
        plt.title("Detected Lines")
        plt.gca().set_aspect('equal', adjustable='box')  # Set equal aspect ratio
        plt.show()

    # Plot created shape (Polygon) on the screen
    def plot_shape(self):
        for polygon in self.polygons:
            x, y = polygon.exterior.xy  # Extract x and y coordinates
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

        for polygon, grid in zip(self.polygons, self.grids):
            # Plot the polygon
            x, y = polygon.exterior.xy
            ax.plot(x, y, color='black')

            # Plot the divisions
            for division in grid:
                if isinstance(division, LineString):
                    x, y = division.xy
                    ax.plot(x, y, color='blue')
                elif isinstance(division, Polygon):
                    x, y = division.exterior.xy  # Fix: Directly get exterior coordinates
                    ax.plot(x, y, color='blue')
                elif isinstance(division, MultiPolygon):
                    for geom in division.geoms:
                        x, y = geom.exterior.xy
                        ax.plot(x, y, color='blue')

        plt.show()

    def get_shapes(self):
        return (self.polygons, self.grids)
