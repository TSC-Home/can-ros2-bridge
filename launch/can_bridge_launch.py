"""ROS2 launch file for can-ros2-bridge."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        DeclareLaunchArgument("config", default_value="config/example.xml"),
        DeclareLaunchArgument("can_interface", default_value="can0"),
        ExecuteProcess(
            cmd=[
                "can-ros2-bridge",
                "--config", LaunchConfiguration("config"),
                "--can-interface", LaunchConfiguration("can_interface"),
            ],
            output="screen",
        ),
    ])
