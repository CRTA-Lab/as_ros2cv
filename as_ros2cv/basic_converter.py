import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

import cv2
from cv_bridge import CvBridge


class BasicConverter(Node):

    def __init__(self):
        super().__init__('basic_converter')
        self.bridge = CvBridge()

        self.declare_parameter('topic', '/camera/image_raw/compressed')
        topic = self.get_parameter('topic').get_parameter_value().string_value

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self.subscription = self.create_subscription(
            CompressedImage,
            topic,
            self._callback,
            qos,
        )
        self.get_logger().info(f'Listening on {topic}')

    def _callback(self, msg: CompressedImage):
        cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
        cv2.imshow('basic_converter', cv_image)
        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BasicConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
