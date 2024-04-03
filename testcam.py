import cv2

def main():
    cap = cv2.VideoCapture(4)

    if not cap.isOpened():
        print("error could not open device")
        return


    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error cant receive frame")
                break
            cv2.imshow('Camera Feed', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
