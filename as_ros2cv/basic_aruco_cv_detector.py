import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

import cv2
from cv_bridge import CvBridge

ARUCO_DICTS = {
    50:   cv2.aruco.DICT_7X7_50,
    100:  cv2.aruco.DICT_7X7_100,
    250:  cv2.aruco.DICT_7X7_250,
    1000: cv2.aruco.DICT_7X7_1000,
}

ARUCO_PARAMS = cv2.aruco.DetectorParameters_create()


class BasicArucoCvDetector(Node):

    def __init__(self):
        super().__init__('basic_aruco_cv_detector')
        self.bridge = CvBridge()

        self.declare_parameter('dictionary', 250)
        dict_size = self.get_parameter('dictionary').get_parameter_value().integer_value
        if dict_size not in ARUCO_DICTS:
            self.get_logger().warn(f'Unknown dictionary {dict_size}, falling back to 250')
            dict_size = 250
        self.aruco_dict = cv2.aruco.Dictionary_get(ARUCO_DICTS[dict_size])
        self.get_logger().info(f'Using DICT_7X7_{dict_size}')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.subscription = self.create_subscription(
            CompressedImage,
            '/camera/camera/color/image_raw/compressed',
            self._callback,
            qos,
        )
        self.publisher = self.create_publisher(
            CompressedImage,
            '/camera/camera/color/aruco/compressed',
            qos,
        )

    def _callback(self, msg: CompressedImage):
        img = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')

        corners, ids, _ = cv2.aruco.detectMarkers(img, self.aruco_dict, parameters=ARUCO_PARAMS)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            for i, marker_id in enumerate(ids.flatten()):
                cx = int(corners[i][0][:, 0].mean())
                cy = int(corners[i][0][:, 1].mean())
                cv2.putText(img, f'ID: {marker_id}', (cx - 20, cy - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        out_msg = self.bridge.cv2_to_compressed_imgmsg(img)
        out_msg.header = msg.header
        self.publisher.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BasicArucoCvDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
