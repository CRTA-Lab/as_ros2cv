# as_ros2cv

Educational ROS2 package demonstrating how to convert between ROS2 image messages and OpenCV, with practical examples including blob detection and ArUco marker detection.

## Prerequisites

```bash
sudo apt install ros-humble-cv-bridge ros-humble-tf2-ros python3-opencv
```

## Build

```bash
cd ~/camera_ws
colcon build --packages-select as_ros2cv --symlink-install
source install/setup.bash
```

## Nodes

### basic_converter

Subscribes to a compressed image topic and displays it in an OpenCV window. The simplest possible example of ROS2 → OpenCV conversion.

**Subscriptions:**
- `/camera/image_raw/compressed` — `sensor_msgs/msg/CompressedImage`

**Run:**
```bash
ros2 run as_ros2cv basic_converter
```

**Remap topic:**
```bash
ros2 run as_ros2cv basic_converter --ros-args -r /camera/image_raw/compressed:=/your/topic
```

---

### basic_blob_finder

Subscribes to a compressed image topic, detects red and green blobs using HSV colour filtering with OpenCV trackbars, and displays the results in OpenCV windows. Use the trackbars to tune HSV thresholds, area limits, and image scale in real time.

**Subscriptions:**
- `/camera/image_raw/compressed` — `sensor_msgs/msg/CompressedImage`

**Run:**
```bash
ros2 run as_ros2cv basic_blob_finder
```

**Trackbars:**

| Trackbar | Description |
|----------|-------------|
| Min/Max H Red | Hue range for red blobs |
| Min/Max H Green | Hue range for green blobs |
| Min/Max S | Saturation range (shared) |
| Min/Max V | Value range (shared) |
| Min/Max Area | Contour area filter in pixels |
| Median Blur | Toggle median blur on/off |
| Kernel Size | Median blur kernel size |
| Image Scale | Resize input image (%) |

---

### basic_blob_publisher

Same blob detection as `basic_blob_finder` but uses hardcoded default HSV values and publishes the annotated image as a ROS2 topic instead of displaying it. Suitable for use with `rqt_image_view`.

**Default HSV values:**

| Parameter | Value |
|-----------|-------|
| Red hue | 171 – 180 |
| Green hue | 64 – 82 |
| Saturation | 100 – 245 |
| Value | 100 – 245 |
| Area | 200 – 30000 px |

**Subscriptions:**
- `/camera/image_raw/compressed` — `sensor_msgs/msg/CompressedImage` (RELIABLE)

**Publications:**
- `/camera/image_raw/blobs/compressed` — `sensor_msgs/msg/CompressedImage` (BEST_EFFORT)

**Run:**
```bash
ros2 run as_ros2cv basic_blob_publisher
```

**Visualise:**
```bash
rqt_image_view
# Select: /camera/image_raw/blobs/compressed
```

---

### basic_aruco_cv_detector

Detects ArUco markers (7×7 dictionary) in a compressed image stream, draws bounding boxes and marker IDs, and publishes the annotated image. Dictionary size is configurable at runtime.

**Subscriptions:**
- `/camera/camera/color/image_raw/compressed` — `sensor_msgs/msg/CompressedImage`

**Publications:**
- `/camera/camera/color/aruco/compressed` — `sensor_msgs/msg/CompressedImage`

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dictionary` | `250` | ArUco dictionary size: `50`, `100`, `250`, `1000` |

**Run:**
```bash
ros2 run as_ros2cv basic_aruco_cv_detector
```

**Change dictionary:**
```bash
ros2 run as_ros2cv basic_aruco_cv_detector --ros-args -p dictionary:=50
```

**Visualise:**
```bash
rqt_image_view
# Select: /camera/camera/color/aruco/compressed
```

---

### basic_aruco_cv_transformation

Detects ArUco markers, estimates their 6-DOF pose using camera intrinsics from `camera_info`, draws the coordinate frame axes on the image, and broadcasts each marker as a TF frame (`aruco_<id>`). Visualise the frames in RViz using the TF display.

**Subscriptions:**
- `/camera/camera/color/image_raw/compressed` — `sensor_msgs/msg/CompressedImage` (BEST_EFFORT)
- `/camera/camera/color/camera_info` — `sensor_msgs/msg/CameraInfo` (RELIABLE)

**Publications:**
- `/camera/camera/color/aruco/compressed` — `sensor_msgs/msg/CompressedImage`
- `/tf` — marker transforms as `aruco_<id>` relative to the camera frame

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dictionary` | `250` | ArUco dictionary size: `50`, `100`, `250`, `1000` |
| `marker_size` | `0.15` | Physical marker size in metres (default: 150 mm) |

**Run:**
```bash
ros2 run as_ros2cv basic_aruco_cv_transformation
```

**Override marker size:**
```bash
ros2 run as_ros2cv basic_aruco_cv_transformation --ros-args -p marker_size:=0.10
```

**Visualise in RViz:**
1. Launch RViz: `rviz2`
2. Set **Fixed Frame** to your camera frame (e.g. `camera_color_optical_frame`)
3. Add a **TF** display
4. Add an **Image** display, subscribe to `/camera/camera/color/aruco/compressed`

---

## Playing a bag file

Bag files for testing are stored in the `bags/` directory inside this package.
Always play bag files from the workspace root (`~/camera_ws`).

```bash
cd ~/camera_ws
ros2 bag play src/as_ros2cv/bags/<bag_folder>/ --loop
```

To record a new bag directly into the `bags/` directory:

```bash
cd ~/camera_ws/src/as_ros2cv/bags
ros2 bag record /camera/image_raw/compressed -o <bag_folder>
```

## QoS notes

| Situation | Use |
|-----------|-----|
| Subscribing to a bag | `RELIABLE` |
| Subscribing to a live camera | `BEST_EFFORT` |
| Publishing for `rqt_image_view` | `BEST_EFFORT` |
