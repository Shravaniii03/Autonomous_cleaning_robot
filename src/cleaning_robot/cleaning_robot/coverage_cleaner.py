#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool, String, Float32
from visualization_msgs.msg import Marker, MarkerArray
import math

class CleaningRobot(Node):
    def __init__(self):
        super().__init__('cleaning_robot')
       
        # Action client for Nav2
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
       
        # Publishers
        self.status_pub = self.create_publisher(Bool, '/cleaning_status', 10)
        self.progress_pub = self.create_publisher(String, '/cleaning_progress', 10)
        self.coverage_pub = self.create_publisher(Float32, '/coverage_percentage', 10)
       
        # Dirt visualization markers
        self.dirt_pub = self.create_publisher(MarkerArray, '/dirt_markers', 10)
        self.cleaned_pub = self.create_publisher(MarkerArray, '/cleaned_markers', 10)
       
        # Room boundaries
        self.x_min = -4.0
        self.x_max = 4.0
        self.y_min = -4.0
        self.y_max = 4.0
        self.step = 0.5

        # Cleaning state tracking
        self.total_waypoints = 0
        self.completed_waypoints = 0
        self.cleaned_cells = []      # cells successfully cleaned
        self.failed_cells = []       # cells robot couldn't reach
        self.dirt_cells = []         # simulated dirt locations

        self.get_logger().info(' Autonomous Cleaning Robot Started!')
        self.get_logger().info(' LiDAR Active — Obstacle Detection ON')
        self.get_logger().info(' Nav2 Active — Dynamic Replanning ON')

    def generate_dirt_locations(self, waypoints):
        """Simulate dirt/dust in the environment"""
        # Place dirt at every waypoint (simulates dirty floor)
        import random
        random.seed(42)
        # Randomly mark 70% of waypoints as dirty
        dirty = [(x, y) for (x, y) in waypoints if random.random() > 0.3]
        self.get_logger().info(f' Detected {len(dirty)} dirty cells out of {len(waypoints)} total cells')
        return dirty

    def publish_dirt_markers(self, dirt_cells):
        """Visualize dirt as red markers in RViz"""
        marker_array = MarkerArray()
        for i, (x, y) in enumerate(dirt_cells):
            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'dirt'
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.01
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.3
            marker.scale.y = 0.3
            marker.scale.z = 0.01
            # Red color = dirty
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0
            marker.color.a = 0.8
            marker_array.markers.append(marker)
        self.dirt_pub.publish(marker_array)
        self.get_logger().info('Dirt markers published in RViz')

    def publish_cleaned_marker(self, x, y, cell_id):
        """Visualize cleaned cell as green marker in RViz"""
        marker_array = MarkerArray()
        marker = Marker()
        marker.header.frame_id = 'map'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'cleaned'
        marker.id = cell_id
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        marker.pose.position.x = x
        marker.pose.position.y = y
        marker.pose.position.z = 0.01
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.4
        marker.scale.y = 0.4
        marker.scale.z = 0.01
        # Green color = cleaned
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 0.6
        marker_array.markers.append(marker)
        self.cleaned_pub.publish(marker_array)

    def is_dirt_at(self, x, y):
        """Check if there is dirt at this location"""
        for (dx, dy) in self.dirt_cells:
            if abs(dx - x) < 0.3 and abs(dy - y) < 0.3:
                return True
        return False

    def generate_boustrophedon_path(self):
        """Lawnmower/boustrophedon pattern — full coverage path"""
        waypoints = []
        y = self.y_min
        direction = 1
        while y <= self.y_max:
            if direction == 1:
                waypoints.append((self.x_min, y))
                waypoints.append((self.x_max, y))
            else:
                waypoints.append((self.x_max, y))
                waypoints.append((self.x_min, y))
            y = round(y + self.step, 2)
            direction *= -1
        self.get_logger().info(f' Generated {len(waypoints)} waypoints using Boustrophedon algorithm')
        return waypoints

    def create_pose(self, x, y):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation.w = 1.0
        return pose

    def send_goal(self, x, y):
        """Send robot to waypoint with Nav2 — handles obstacle avoidance automatically"""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = self.create_pose(x, y)
        self._action_client.wait_for_server()
        future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
       
        if not goal_handle.accepted:
            self.get_logger().warn(f' Goal ({x}, {y}) rejected by Nav2 — obstacle detected, replanning...')
            self.failed_cells.append((x, y))
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return True

    def clean_cell(self, x, y, cell_id):
        """Simulate cleaning action at current position"""
        if self.is_dirt_at(x, y):
            self.get_logger().info(f' Dirt detected at ({x:.1f}, {y:.1f}) — Cleaning...')
            # Simulate cleaning time
            import time
            time.sleep(0.1)
            self.get_logger().info(f' Cell ({x:.1f}, {y:.1f}) cleaned!')
        else:
            self.get_logger().info(f' Cell ({x:.1f}, {y:.1f}) already clean — moving on')
       
        # Mark as cleaned in RViz
        self.publish_cleaned_marker(x, y, cell_id)
        self.cleaned_cells.append((x, y))

    def start_cleaning(self):
        """Main autonomous cleaning routine"""
        self.get_logger().info('=' * 50)
        self.get_logger().info(' AUTONOMOUS CLEANING STARTED')
        self.get_logger().info('=' * 50)
        self.status_pub.publish(Bool(data=True))

        # Generate path
        waypoints = self.generate_boustrophedon_path()
        self.total_waypoints = len(waypoints)

        # Generate and publish dirt locations
        self.dirt_cells = self.generate_dirt_locations(waypoints)
        self.publish_dirt_markers(self.dirt_cells)

        dirty_count = len(self.dirt_cells)
        self.get_logger().info(f'  Room scan complete — {dirty_count} dirty areas found')
        self.get_logger().info(f' Starting coverage of {self.total_waypoints} cells...')

        # Navigate and clean each waypoint
        for i, (x, y) in enumerate(waypoints):
            if rclpy.ok() is False:
                break

            self.get_logger().info(f' Waypoint {i+1}/{self.total_waypoints}: ({x:.1f}, {y:.1f})')
           
            # Navigate to waypoint (Nav2 handles obstacle avoidance)
            success = self.send_goal(x, y)

            if success:
                # Perform cleaning at this cell
                self.clean_cell(x, y, i)
                self.completed_waypoints += 1
            else:
                self.get_logger().warn(f' Skipping unreachable cell ({x:.1f}, {y:.1f})')

            # Publish coverage percentage
            coverage = (self.completed_waypoints / self.total_waypoints) * 100
            coverage_msg = Float32()
            coverage_msg.data = coverage
            self.coverage_pub.publish(coverage_msg)

            progress_msg = String()
            progress_msg.data = (
                f'Waypoint: {i+1}/{self.total_waypoints} | '
                f'Coverage: {coverage:.1f}% | '
                f'Cleaned: {len(self.cleaned_cells)} cells | '
                f'Failed: {len(self.failed_cells)} cells'
            )
            self.progress_pub.publish(progress_msg)
            self.get_logger().info(f'Coverage: {coverage:.1f}%')

        # Mission complete summary
        self.get_logger().info('=' * 50)
        self.get_logger().info(' CLEANING MISSION COMPLETE!')
        self.get_logger().info(f'Total waypoints:     {self.total_waypoints}')
        self.get_logger().info(f'Successfully cleaned: {len(self.cleaned_cells)} cells')
        self.get_logger().info(f'Unreachable cells:   {len(self.failed_cells)} cells')
        final_coverage = (len(self.cleaned_cells) / self.total_waypoints) * 100
        self.get_logger().info(f'Final coverage:      {final_coverage:.1f}%')
        self.get_logger().info('=' * 50)

        self.status_pub.publish(Bool(data=False))

        # Return home
        self.get_logger().info('Returning home')
        self.send_goal(0.0, 0.0)
        self.get_logger().info(' Robot docked at home')


def main(args=None):
    rclpy.init(args=args)
    robot = CleaningRobot()
    robot.start_cleaning()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
