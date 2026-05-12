from setuptools import find_packages, setup

package_name = 'as_ros2cv'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='Educational package for converting ROS2 images to OpenCV and back.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'basic_converter = as_ros2cv.basic_converter:main',
            'basic_blob_finder = as_ros2cv.basic_blob_finder:main',
            'basic_blob_publisher = as_ros2cv.basic_blob_publisher:main',
            'basic_aruco_cv_detector = as_ros2cv.basic_aruco_cv_detector:main',
            'basic_aruco_cv_transformation = as_ros2cv.basic_aruco_cv_transformation:main',
        ],
    },
)
