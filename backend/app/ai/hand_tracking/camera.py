import cv2


class Camera:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Unable to access webcam.")

    def read_frame(self):
        success, frame = self.cap.read()

        if not success:
            return None

        return frame

    def release(self):
        if self.cap:
            self.cap.release()

        cv2.destroyAllWindows()