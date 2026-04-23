# Autonomous Cleaning Robot
### MAR Mini Project 

A fully autonomous cleaning robot simulation built using ROS2, Gazebo, Nav2, and SLAM Toolbox. The robot autonomously maps an indoor environment, detects dirty areas, plans an optimal coverage path using the Boustrophedon algorithm, and cleans the entire floor without any human intervention.

## Team Members
| Member | Role |
|--------|------|
| Member 1 | ROS2 Setup + Gazebo World Design |
| Member 2 | SLAM Mapping + Nav2 Navigation |
| Member 3 | Coverage Path Planning Algorithm |
| Member 4 | Visualization + Report + Evaluation |

##Problem Statement
In indoor environments, manual cleaning is time-consuming, labor-intensive, and inconsistent. This project simulates an autonomous cleaning robot that can independently map an unknown environment, detect dirty areas, plan an optimal coverage path, and clean the entire floor area without any human intervention — mimicking real-world robotic vacuum cleaners like Roomba.

## Objective
To design and simulate a robot that:
- Autonomously builds a map of an unknown indoor environment using SLAM
- Localizes itself accurately on the map using AMCL
- Plans a complete coverage path using the Boustrophedon algorithm
- Detects and cleans dirty areas autonomously
- Avoids obstacles dynamically using Nav2
- Returns to home position after completing the cleaning mission

## Tools and Technologies
| Tool | Version | Purpose |
|------|---------|---------|
| ROS2 | Humble | Robot middleware framework |
| Gazebo | Classic | 3D physics simulation |
| TurtleBot3 Burger | - | Robot platform with LiDAR |
| SLAM Toolbox | - | Autonomous mapping |
| Nav2 | - | Autonomous navigation + obstacle avoidance |
| AMCL | - | Robot localization on map |
| Boustrophedon Algorithm | Custom | Coverage path planning |
| RViz2 | - | Visualization |
| Python3 | 3.10 | scripting language |
| Ubuntu | 22.04 LTS | Operating system |

## Installation and Setup
### Prerequisites
- Ubuntu 22.04 LTS
- ROS2 Humble
- Gazebo Classic

### Step 1 — Install ROS2 Humble
Follow the official ROS2 Humble installation guide:
https://docs.ros.org/en/humble/Installation.html

### Step 2 — Install Dependencies
```bash
sudo apt install ros-humble-navigation2 -y
sudo apt install ros-humble-nav2-bringup -y
sudo apt install ros-humble-slam-toolbox -y
sudo apt install ros-humble-turtlebot3* -y
sudo apt install ros-humble-turtlebot3-gazebo -y
sudo apt install ros-humble-gazebo-ros-pkgs -y
```

### Step 3 — Clone Repository
```bash
git clone https://github.com/Shravaniii03/Autonomous_cleaning_robot.git
cd Autonomous_cleaning_robot
```

### Step 4 — Build Workspace
```bash
colcon build --symlink-install
source install/setup.bash
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
source ~/.bashrc
```

## How to Run

### Phase 1 — SLAM Mapping (One time only)

#### Terminal 1 — Launch Gazebo
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

#### Terminal 2 — Launch SLAM
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```

#### Terminal 3 — Launch RViz
```bash
ros2 launch nav2_bringup rviz_launch.py
```

#### Terminal 4 — Drive robot to build map
```bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```

#### Terminal 5 — Save map when complete
```bash
ros2 run nav2_map_server map_saver_cli -f ~/cleaning_robot_ws/src/cleaning_robot/maps/cleaning_map
```

### Phase 2 — Autonomous Cleaning
#### Terminal 1 — Launch Gazebo
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

#### Terminal 2 — Launch Nav2 with saved map
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch nav2_bringup bringup_launch.py \
  map:=$HOME/cleaning_robot_ws/src/cleaning_robot/maps/cleaning_map.yaml \
  use_sim_time:=True
```

#### Terminal 3 — Launch RViz
```bash
ros2 launch nav2_bringup rviz_launch.py
```

#### Terminal 4 — Set Initial Pose in RViz
1)Click "2D Pose Estimate" button
2)Click on map where robot is located
3)Hold and drag in direction robot faces
4)Release mouse
5)Wait for green particles to appear


#### Terminal 5 — Run Cleaning Script
```bash
cd ~/cleaning_robot_ws
source install/setup.bash
ros2 run cleaning_robot coverage_cleaner
```

#### Terminal 6 — Monitor Progress
```bash
ros2 topic echo /cleaning_progress
```

## Coverage Algorithm — Boustrophedon

The robot uses the Boustrophedon (lawnmower) pattern for complete floor coverage

## Results

| Metric | Value |
|--------|-------|
| Total waypoints | 34 |
| Coverage achieved | 100% |
| Algorithm | Boustrophedon |
| Obstacle avoidance | Nav2 Costmap |
| Localization method | AMCL |
| Simulation platform | Gazebo Classic |

## How Autonomy Works

| Stage | Component | What it does |
|-------|-----------|-------------|
| Sensing | LiDAR | Detects walls and obstacles 360° |
| Mapping | SLAM Toolbox | Builds map of environment |
| Localization | AMCL | Tracks robot position on map |
| Path Planning | Boustrophedon | Generates coverage waypoints |
| Navigation | Nav2 | Moves robot safely to each waypoint |
| Cleaning | coverage_cleaner.py | Detects dirt and cleans each cell |
| Completion | coverage_cleaner.py | Returns robot home after 100% coverage |


## References
- ROS2 Humble Documentation: https://docs.ros.org/en/humble
- Nav2 Documentation: https://navigation.ros.org
- SLAM Toolbox: https://github.com/SteveMacenski/slam_toolbox
- TurtleBot3 Manual: https://emanual.robotis.com/docs/en/platform/turtlebot3/overview
- Choset, H. (2001). Coverage for robotics — A survey of recent results. Annals of Mathematics and Artificial Intelligence



