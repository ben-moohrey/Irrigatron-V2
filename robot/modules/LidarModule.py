from modules.BaseModule import BaseModule
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
# from roboviz import MapVisualizer


class LidarModule(BaseModule):
    def __init__(
        self,
        topics,
        thread_id,
        settings,
        LIDAR_DEVICE,
        MIN_SAMPLES,
    ):
        super().__init__(topics, thread_id, settings)

        self.lidar_frame_topic = topics.get_topic('lidar_frame')

        self.LIDAR_DEVICE = LIDAR_DEVICE
        self.MAP_SIZE_PIXELS = 500
        self.MAP_SIZE_METERS = 10

        self.OBSTRUCTED_MIN_ANGLE = 180-20
        self.OBSTRUCTED_MAX_ANGLE = 180+20

        self.MIN_SAMPLES = MIN_SAMPLES
        self.setup()

    def setup(self):
        self.lidar = Lidar(self.LIDAR_DEVICE, baudrate=115200, timeout=3)

        self.slam = RMHC_SLAM(
            LaserModel(),
            self.MAP_SIZE_PIXELS,
            self.MAP_SIZE_METERS,
        )

        # self.viz      = M
        self.trajectory = []
        self.mapbytes = bytearray(self.MAP_SIZE_PIXELS * self.MAP_SIZE_PIXELS)

        self.iterator = self.lidar.iter_scans()
        self.prev_distances = None
        self.prev_angles = None

        self.x = 0
        self.y = 0
        self.theta = 0

        next(self.iterator)

    def run(self, shutdown_flag):
        items = [item for item in next(self.iterator)]

        distances = []
        angles = []
        for q, angle, distance in items:
            real_angle = (-angle+360)%360
            if real_angle >= self.OBSTRUCTED_MIN_ANGLE and real_angle <= self.OBSTRUCTED_MAX_ANGLE:
                continue
            # if angle >= OBSTRUCTED_MIN_ANGLE and angle <= OBSTRUCTED_MAX_ANGLE:
            #     continue
            distances.append(distance)
            angles.append(real_angle)
            # distances.append(distance)
            # angles.append((-angle+360)%360)

        if len(distances) > self.MIN_SAMPLES:
            self.slam.update(distances, scan_angles_degrees=angles)
            self.prev_distances = distances.copy()
            self.prev_angles = angles.copy()

        elif self.prev_distances is not None:
            self.slam.update(
                self.prev_distances,
                scan_angles_degrees=self.prev_angles,
            )

        self.x, self.y, self.theta = self.slam.getpos()
        print(self.x, self.y, self.theta)

    def shutdown(self):
        self.lidar.stop()
        self.lidar.disconnect()
