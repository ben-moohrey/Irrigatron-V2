from modules.BaseModule import BaseModule
import cv2
import cv2.aruco as aruco
import numpy as np

class CameraModule(BaseModule):
    def __init__(
        self,
        topics,
        thread_id,
        settings,
        ): 
            super().__init__(topics, thread_id, settings)

            self.cap = cv2.VideoCapture(0)


            if not self.cap.isOpened():
                self.log("error could not open device")
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
            parameters =  aruco.DetectorParameters()
            self.detector = aruco.ArucoDetector(self.aruco_dict, parameters)

            self.arucode_topic = self.topics.get_topic("arucode_topic")

            # id, position from center
            self.arucode_topic.write_data([])
            self.last_aruco_infomation = []
            # /home/irrigatron/Irrigatron-V2/robot/data/camera_matrix.npy
            self.camera_matrix = np.load('/home/irrigatron/Irrigatron-V2/robot/data/camera_matrix.npy')
            self.dist_coeffs = np.load('/home/irrigatron/Irrigatron-V2/robot/data/dist_coeffs.npy')

            self.focal_length = self.camera_matrix[0, 0]
            self.frame_center_x=640/2
            self.frame_center_y = 480 / 2

    def rotation_matrix_to_euler_angles(self, R):
        # Assuming the rotation matrix is of the form [R | t]
        sy = np.sqrt(R[0, 0] ** 2 +  R[1, 0] ** 2)
        singular = sy < 1e-6

        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0

        return np.array([x, y, z])

    def run_camera(self):
        ret, frame = self.cap.read()



        if not ret:
            self.log("Error: can't receive frame")
            return

        # frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)
        # Calculate the center of the frame
        frame_center = np.array([frame.shape[1]/2, frame.shape[0]/2])

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ids = []
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(gray)

        # aruco_information[i][0]=id
        # aruco_information[i][1]=distance
        # aruco_information[i][2]=euler_angle
        # aruco_information[i][3]=distance_from_center_x (left,right)
        aruco_information = []
        if corners is not None and len(corners) > 0:
            # self.log("TEST")

            for i, corner in enumerate(corners):
                id = ids[i][0]

                # Calculate the centroid of the marker
                centroid_x = np.mean(corner[0][:, 0])
                # centroid_y = np.mean(corner[0][:, 1])

                # Calculate normalized distance from center (x-axis and y-axis)
                normalized_x = 2 * ((centroid_x - self.frame_center_x) / frame.shape[1])
                # normalized_y = 2 * ((centroid_y - self.frame_center_y) / frame.shape[0])
                # self.log("x:",normalized_x)
                # self.log("y:",normalized_y)
                # Assuming you still want to track distance and angles
                rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(corner, 0.08, self.camera_matrix, self.dist_coeffs)
                distance_to_marker = tvecs[0][0][2]
                R, _ = cv2.Rodrigues(rvecs[0][0])
                euler_angles = self.rotation_matrix_to_euler_angles(R)
                euler_angles_deg = np.degrees(euler_angles)

                # Store the information
                aruco_information.append([id, distance_to_marker, euler_angles_deg[1], normalized_x])

        # if corners is not None and len(corners) > 0:
        #     # aruco.drawDetectedMarkers(frame, corners, ids)


        #     # aruco_information[i][0]=id
        #     # aruco_information[i][1]=distance
        #     # aruco_information[i][2]=euler_angle
        #     # aruco_information[i][3]=distance_from_center (left,right)
        #     ids_and_position = []
        #     aruco_information = []
        #     rvecs, tvecs, _objPoints = cv2.aruco.estimatePoseSingleMarkers(corners, 0.1, self.camera_matrix, self.dist_coeffs)
        #     # self.log(rvecs, tvecs, _objPoints)
        #     for id, tvec, rvec, corners in zip(ids.flatten(), tvecs, rvecs, corners):
        #         self.log("ID: ", id)

        #         distance_to_marker = tvec[0][2]
        #         R, _ = cv2.Rodrigues(rvec)
        #         euler_angles = self.rotation_matrix_to_euler_angles(R)
        #         euler_angles_deg = np.degrees(euler_angles)  # Convert from radians to degrees if necessary
        #         # self.log("Euler Angles:", euler_angles_deg)
        #         # theta = cv2.decomposeProjectionMatrix(cv2.hconcat([R, np.zeros((3, 1))]))[-1]
        #         # theta = np.rad2deg(theta).flatten()[:3]
        #         normalized_x = 2 * ((centroid_x - frame_center_x) / frame.shape[1])
        #         normalized_y = 2 * ((centroid_y - frame_center_y) / frame.shape[0])
        #         self.log(tvec)
        #         x_distance = tvec[0][0]
        #         z_distance = tvec[0][2]
        #         normalized_x = (x_distance / z_distance) / (frame.shape[1] / (2 * self.focal_length))
        #         self.log("normalized_x: ",normalized_x)
        #         # self.log("Distance: ",distance_to_marker)

        #         aruco_information.append([id,distance_to_marker,euler_angles_deg[1]])
            # # self.log("Theta:", theta)
            # for i, corner in zip(ids.flatten(), corners):

                
                
            #     # Calculate the centroid of the marker
            #     c = corner[0]
            #     centroid = c.mean(axis=0)

            #     # Calculate position relative to the center of the frame
            #     position_from_center = centroid - frame_center
                

            #     # Calculate area using the Shoelace formula
            #     x = c[:, 0]  # All x coordinates of the corners
            #     y = c[:, 1]  # All y coordinates of the corners
            #     area = 0.5*np.abs(np.dot(x, np.roll(y,1)) - np.dot(y, np.roll(x,1)))

            #     # Log ID, centroid, and position relative to center
            #     ##self.log(f"ID: {i}, Centroid: {centroid}, Position from Center: {position_from_center}")
            #     ids_and_position.append((i,position_from_center.tolist(),area))

                
            #     # self.log(position_from_center[0])
            self.last_aruco_infomation = self.arucode_topic.read_data()

            if (self.last_aruco_infomation != aruco_information):
                self.arucode_topic.write_data(aruco_information)
        else:
            self.last_aruco_infomation = self.arucode_topic.read_data()
            if (not (len(self.last_aruco_infomation) == 0)):
                self.arucode_topic.write_data([])


        
                



    
    def run(self, shutdown_flag):
        self.run_camera()
    
    def shutdown(self):
        self.cap.release()
        return 1
