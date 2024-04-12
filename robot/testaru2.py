import cv2
import cv2.aruco as aruco

def main():
    # Initialize the video capture from the first webcam
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    # Set up the predefined dictionary and parameters for ArUco detection
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters()

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect ArUco markers in the grayscale image
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

            # If markers are detected, draw them on the frame
            if ids is not None:
                aruco.drawDetectedMarkers(frame, corners, ids)

            # Display the resulting frame
            cv2.imshow('Frame', frame)

            # Press 'q' to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # When everything done, release the capture and close all windows
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
