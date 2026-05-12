import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage

import cv2
import numpy as np
from cv_bridge import CvBridge


class BasicBlobFinder(Node):

    def __init__(self):
        super().__init__('basic_blob_finder')
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

        cv2.namedWindow('Object Detection', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Contours Red', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('Contours Green', cv2.WINDOW_AUTOSIZE)

        cv2.createTrackbar('Min H Red',   'Object Detection', 171,   180, lambda x: None)
        cv2.createTrackbar('Max H Red',   'Object Detection', 180,   180, lambda x: None)
        cv2.createTrackbar('Min H Green', 'Object Detection', 64,    180, lambda x: None)
        cv2.createTrackbar('Max H Green', 'Object Detection', 82,    180, lambda x: None)
        cv2.createTrackbar('Min S',       'Object Detection', 100,   255, lambda x: None)
        cv2.createTrackbar('Max S',       'Object Detection', 245,   255, lambda x: None)
        cv2.createTrackbar('Min V',       'Object Detection', 100,   255, lambda x: None)
        cv2.createTrackbar('Max V',       'Object Detection', 245,   255, lambda x: None)
        cv2.createTrackbar('Min Area',    'Object Detection', 200,  100000, lambda x: None)
        cv2.createTrackbar('Max Area',    'Object Detection', 30000, 100000, lambda x: None)
        cv2.createTrackbar('Median Blur', 'Object Detection', 0,     1,   lambda x: None)
        cv2.createTrackbar('Kernel Size', 'Object Detection', 1,     20,  lambda x: None)
        cv2.createTrackbar('Image Scale', 'Object Detection', 50,    200, lambda x: None)

        self.get_logger().info(f'Listening on {topic}')

    def _callback(self, msg: CompressedImage):
        original = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')

        min_h_red   = cv2.getTrackbarPos('Min H Red',   'Object Detection')
        max_h_red   = cv2.getTrackbarPos('Max H Red',   'Object Detection')
        min_h_green = cv2.getTrackbarPos('Min H Green', 'Object Detection')
        max_h_green = cv2.getTrackbarPos('Max H Green', 'Object Detection')
        min_s       = cv2.getTrackbarPos('Min S',       'Object Detection')
        max_s       = cv2.getTrackbarPos('Max S',       'Object Detection')
        min_v       = cv2.getTrackbarPos('Min V',       'Object Detection')
        max_v       = cv2.getTrackbarPos('Max V',       'Object Detection')
        min_area    = cv2.getTrackbarPos('Min Area',    'Object Detection')
        max_area    = cv2.getTrackbarPos('Max Area',    'Object Detection')
        median_blur = cv2.getTrackbarPos('Median Blur', 'Object Detection')
        kernel_size = cv2.getTrackbarPos('Kernel Size', 'Object Detection')
        image_scale = cv2.getTrackbarPos('Image Scale', 'Object Detection')

        if kernel_size % 2 == 0:
            kernel_size += 1
        if kernel_size < 1:
            kernel_size = 1

        scale = image_scale / 100.0
        new_size = (int(original.shape[1] * scale), int(original.shape[0] * scale))
        img = cv2.resize(original, new_size, interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        if median_blur:
            img = cv2.medianBlur(img, kernel_size)

        mask_red   = cv2.inRange(hsv, (min_h_red,   min_s, min_v), (max_h_red,   max_s, max_v))
        mask_green = cv2.inRange(hsv, (min_h_green, min_s, min_v), (max_h_green, max_s, max_v))

        contours_red,   _ = cv2.findContours(mask_red,   cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour_img_red   = cv2.bitwise_and(img, img, mask=mask_red)
        contour_img_green = cv2.bitwise_and(img, img, mask=mask_green)

        for contour in contours_red:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(img, f'Area: {int(area)}', (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        for contour in contours_green:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, f'Area: {int(area)}', (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow('Object Detection', img)
        cv2.imshow('Contours Red',     contour_img_red)
        cv2.imshow('Contours Green',   contour_img_green)
        cv2.waitKey(1)

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = BasicBlobFinder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
