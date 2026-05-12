import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

import cv2
from cv_bridge import CvBridge


MIN_H_RED,   MAX_H_RED   = 171, 180
MIN_H_GREEN, MAX_H_GREEN = 64,  82
MIN_S,       MAX_S       = 100, 245
MIN_V,       MAX_V       = 100, 245
MIN_AREA,    MAX_AREA    = 200, 30000


class BlobPublisher(Node):

    def __init__(self):
        super().__init__('blob_publisher')
        self.bridge = CvBridge()

        sub_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        pub_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        self.subscription = self.create_subscription(
            CompressedImage,
            '/camera/image_raw/compressed',
            self._callback,
            sub_qos,
        )
        self.publisher = self.create_publisher(CompressedImage, '/camera/image_raw/blobs/compressed', pub_qos)

    def _callback(self, msg: CompressedImage):
        img = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask_red   = cv2.inRange(hsv, (MIN_H_RED,   MIN_S, MIN_V), (MAX_H_RED,   MAX_S, MAX_V))
        mask_green = cv2.inRange(hsv, (MIN_H_GREEN, MIN_S, MIN_V), (MAX_H_GREEN, MAX_S, MAX_V))

        for contour in cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            area = cv2.contourArea(contour)
            if MIN_AREA < area < MAX_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(img, f'Area: {int(area)}', (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        for contour in cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            area = cv2.contourArea(contour)
            if MIN_AREA < area < MAX_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, f'Area: {int(area)}', (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        out_msg = self.bridge.cv2_to_compressed_imgmsg(img)
        out_msg.header = msg.header
        self.publisher.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BlobPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
