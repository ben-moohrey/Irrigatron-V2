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
            parameters =  cv2.aruco.DetectorParameters()
            self.detector = cv2.aruco.ArucoDetector(self.aruco_dict, parameters)
            self.arucode_locations_topic = self.topics.get_topic("arucode_locations_topic")


            # id, position from center
            self.arucode_locations_topic.write_data([])


    def run_camera(self):
        ret, frame = self.cap.read()

        if not ret:
            self.log("Error: can't receive frame")
            return

        # Calculate the center of the frame
        frame_center = np.array([frame.shape[1]/2, frame.shape[0]/2])

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ids = []
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(gray,)

        if len(corners) > 0:
            # aruco.drawDetectedMarkers(frame, corners, ids)

            ids_and_position = []
            for i, corner in zip(ids.flatten(), corners):
                # Calculate the centroid of the marker
                c = corner[0]
                centroid = c.mean(axis=0)

                # Calculate position relative to the center of the frame
                position_from_center = centroid - frame_center

                # Calculate area using the Shoelace formula
                x = c[:, 0]  # All x coordinates of the corners
                y = c[:, 1]  # All y coordinates of the corners
                area = 0.5*np.abs(np.dot(x, np.roll(y,1)) - np.dot(y, np.roll(x,1)))

                # Log ID, centroid, and position relative to center
                ##self.log(f"ID: {i}, Centroid: {centroid}, Position from Center: {position_from_center}")
                ids_and_position.append((i,position_from_center.tolist(),area))
                
                # self.log(position_from_center[0])
            last_ids_and_position = self.arucode_locations_topic.read_data()

            if (last_ids_and_position != ids_and_position):
                self.arucode_locations_topic.write_data(ids_and_position)
        else:
            last_ids_and_position = self.arucode_locations_topic.read_data()
            if (not (len(last_ids_and_position) == 0)):
                self.arucode_locations_topic.write_data([])


        
                



    
    def run(self, shutdown_flag):
        self.run_camera()
    
    def shutdown(self):
        self.cap.release()
        return 1
