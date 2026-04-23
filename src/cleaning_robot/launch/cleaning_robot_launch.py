import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    cleaning_robot = get_package_share_directory('cleaning_robot')

    # Launch Gazebo with TurtleBot3
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(turtlebot3_gazebo, 'launch', 'turtlebot3_world.launch.py')
        )
    )

    # Launch Nav2
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup, 'launch', 'navigation_launch.py')
        )
    )

    # Launch SLAM
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'),
                        'launch', 'online_async_launch.py')
        )
    )

    # Cleaning node (starts after 10 seconds)
    cleaning_node = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='cleaning_robot',
                executable='coverage_cleaner',
                name='cleaning_robot',
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        gazebo,
        slam,
        nav2,
        cleaning_node,
    ])
