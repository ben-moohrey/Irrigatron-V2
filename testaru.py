import cv2
import cv2.aruco as aruco

def main():
    cap = cv2.VideoCapture(4)

    if not cap.isOpened():
        print("error could not open device")
        return


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    #parameters = aruco.DetectorParameters_create()

    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error cant receive frame")
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict)

            if len(corners) > 0:
                aruco.drawDetectedMarkers(frame, corners, ids)

            print(ids)
            cv2.imshow('Camera Feed', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
