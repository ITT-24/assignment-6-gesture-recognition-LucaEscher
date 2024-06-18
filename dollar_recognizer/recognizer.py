# $1 gesture recognizer

import config
from dollarpy import Recognizer
import math
import numpy as np
import os
from scipy.signal import resample
from sklearn.preprocessing import StandardScaler
import xml.etree.ElementTree as ET

dataset_path = './dataset/xml_logs/s01'

class Recognizer:

    def __init__(self, gestures) -> None:
        super(Recognizer, self).__init__()
        self.gestures = gestures
        self.templates = self.load_data(self.gestures)
        self.new_templates = []

    def load_data(slef, gestures):
        data = []
        labels = []

        for root, subdirs, files in os.walk(dataset_path):
            if 'ipynb_checkpoint' in root:
                continue
            if len(files) > 0:
                for f in files:
                    if '.xml' in f:
                        fname = f.split('.')[0]
                        label = fname[:-2]

                        xml_root = ET.parse(f'{root}/{f}').getroot()

                        points = []
                        for element in xml_root.findall('Point'):
                            x = element.get('X')
                            y = element.get('Y')
                            points.append([x, y])

                        points = np.array(points, dtype=float)

                        scaler = StandardScaler()
                        points = scaler.fit_transform(points)

                        resampled = resample(points, config.RecognizerSetup.NUM_POINTS)

                        if not label in labels and label in gestures:
                            data.append((label, resampled))
                            labels.append(label)

                        if len(labels) == len(gestures):
                            print(f'{len(data)} files loaded -> success!')
                            return data
        
        print(f'{len(data)} files were loaded > success!')
        return data

    # ------- measure distance -------

    def get_distance(self, x1, y1, x2, y2):
        distance = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance

    # ------- rotate to zero -------

    def centroid(self, arr):
        length = len(arr)
        sum_x = np.sum(arr[:][0])
        sum_y = np.sum(arr[:][1])
        return sum_x/length, sum_y/length

    def indicative_angle(self, points):
        c = np.mean(points, 0)
        return np.arctan2(c[1] - points[0][1], c[0] - points[0][0])

    def rotate_to_indicative_angle(self, points):
        angle_to_rotate = self.indicative_angle(points)
        newPoints = self.rotate_points_around_center(points, 0, -angle_to_rotate)
        return newPoints

    def rotate_points_around_center(self, pts, cnt, ang=np.pi/4):
        """ 
        Function description generated with chatgpt and code from https://gis.stackexchange.com/questions/23587/rotating-the-polygon-about-anchor-point-using-python-script:

        Rotates a set of 2D points around a specified center by a given angle.

        Args:
            pts (array-like): An array of points to be rotated, each point represented as a 2-element array [x, y].
            cnt (array-like): The center point [x, y] around which the points are rotated.
            ang (float): The angle in radians by which to rotate the points. The default angle is pi/4 (45 degrees).

        Returns:
            numpy.ndarray: The array of rotated points, each represented as a 2-element array [x, y].

        Description:
            This function takes an array of 2D points and rotates them around a specified center point by a given angle.
            The rotation is performed counterclockwise by default. The transformation is achieved using matrix
            multiplication to apply the rotation matrix to each point relative to the center point. 
        """
        return np.dot(np.array(pts)-cnt, np.array([[np.cos(ang), np.sin(ang)], [-np.sin(ang), np.cos(ang)]]))+cnt

    def rotate_by(self, points, omega):
        newPoints = np.zeros((1, 2))
        c = np.mean(points, 0)
        for point in points:
            q_x = (point[0] - c[0]) * math.cos(omega) - (point[1] - c[1]) * math.sin(omega) + c[0]
            q_y = (point[0] - c[0]) * math.sin(omega) - (point[1] - c[1]) * math.cos(omega) + c[1]
            newPoints = np.append(newPoints, [(q_x, q_y)], 0)
        return newPoints[1:]

    # ------- scaling and translating -------

    def bounding_box(self, points):
        minX, maxX = np.inf, -np.inf
        minY, maxY = np.inf, -np.inf
        for point in points:
            minX, maxX = min(minX, point[0]), max(maxX, point[0])
            minY, maxY = min(minY, point[1]), max(maxY, point[1])
        return minX, maxX, minY, maxY

    def scale_to(self, points, size):
        newPoints = np.zeros((1, 2))
        min_x, max_x, min_y, max_y = self.bounding_box(points)
        for point in points:
            q_x = point[0] * size / (max_x - min_x)
            q_y = point[1] * size / (max_y - min_y)
            newPoints = np.append(newPoints, [(q_x, q_y)], 0)

        return newPoints

    def translate_to(self, points, k):
        newPoints = np.zeros((1, 2))
        c = np.mean(points, 0)
        for point in points:
            q_x = point[0] + k - c[0]
            q_y = point[1] + k - c[1]
            newPoints = np.append(newPoints, [(q_x, q_y)], 0)

        return newPoints[1:]

    # ------- distance, recognition -------

    def path_distance(self, A, B):
        d = 0
        for i in range(len(A) - 1):
            d += self.get_distance(A[i][0], A[i][1], B[i][0], B[i][1])

        return d / len(A)

    def distance_at_angle(self, points, temp_points, theta):
        new_points = self.rotate_by(points, theta)
        d = self.path_distance(new_points, temp_points)
        return d

    def distance_at_best_angle(self, points, template, theta_a, theta_b, delta_theta):
        temp_name, temp_points = template
        phi = 0.5 * (-1 + np.sqrt(5))
        x_1 = phi * theta_a + (1 - phi) * theta_b
        f_1 = self.distance_at_angle(points, temp_points, x_1)
        x_2 = phi * theta_b + (1 - phi) * theta_a
        f_2 = self.distance_at_angle(points, temp_points, x_2)

        while abs(theta_b - theta_a) > delta_theta:
            if f_1 < f_2:
                theta_b = x_2
                x_2 = x_1
                f_2 = f_1
                x_1 = phi * theta_a + (1 - phi) * theta_b
                f_1 = self.distance_at_angle(points, temp_points, x_1)
            else:
                theta_a = x_1
                x_1 = x_2
                f_1 = f_2
                x_2 = phi * theta_b + (1 - phi) * theta_a
                f_2 = self.distance_at_angle(points, temp_points, x_2)

        return min(f_1, f_2)

    def recognize(self, points):
        templates = self.templates
        points = resample(points, 50)
        points = self.rotate_to_indicative_angle(points)
        points = self.scale_to(points, 250)
        points = self.translate_to(points, 0)
        b = np.inf
        theta = np.pi/4
        delta_theta = np.pi/90
        size = 250
        for template in templates:
            d = self.distance_at_best_angle(points, template, -theta, theta, delta_theta)
            if d < b:
                b = d
                new_template = template
        score = 1 - b/0.5 * np.sqrt(size ^ 2 + size ^ 2)
        return new_template, score

    # ------- initialize functions -------

    def addTemplate(self, template):
        name, points = template
        points = self.rotate_to_indicative_angle(points)
        points = self.scale_to(points, 250)
        points = self.translate_to(points, 0)
        self.new_templates.append([name, points])

    def initialize(self):
        for template in self.templates:
            self.addTemplate(template)


if __name__ == "__main__":
    dollar_recognizer = Recognizer(config.Gestures.FIVE)
    dollar_recognizer.initialize()
