# CAN-ROS2 Bridge

A Rust-based bridge that decodes CAN signals (via SocketCAN) and publishes them as ROS2 topics. Configuration is done through XML files, generated from DBC files using the included Python tool (GUI or CLI).

## Project Structure

```
node/           Rust bridge (SocketCAN -> ROS2)
tools/          Python DBC mapper (GUI + CLI)
config/         XML configurations
dbc/            DBC files
test-pipeline/  Integration tests with virtual CAN
docker/         Dockerfile + test scripts
launch/         ROS2 launch file
systemd/        systemd service unit
```

## Quick Start: Full Test Suite

One command - builds a Docker container with ROS2 + Rust, then runs all tests using your DBC and XML config:

```bash
bash docker/test_ros2.sh \
    dbc/SensoricSolutionsOMSRace.dbc \
    config/config_SensoricSolutionsOMSRace_040326_1846.xml
```

This automatically:
1. Creates a vcan0 interface (requires sudo)
2. Builds the Docker image (ROS2 Humble + Rust + Python)
3. Runs all tests inside the container:
   - Rust unit tests (26 tests)
   - Python unit tests (14 tests)
   - Integration test with filter verification
   - ROS2 end-to-end test (verifies real topic values)

## Installation

### Fedora

```bash
sudo dnf install -y rust cargo python3-pip python3-devel \
    kernel-modules-extra iproute
pip install -r tools/requirements.txt pytest
cd node && cargo build --release
```

### Ubuntu/Debian

```bash
sudo apt install -y rustc cargo python3-pip iproute2
pip install -r tools/requirements.txt pytest
cd node && cargo build --release
```

### Docker for ROS2 Tests (required on Fedora)

ROS2 Humble only supports Ubuntu natively. On Fedora, use Docker:

```bash
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Log out and back in, then:
docker build -t can-ros2-bridge -f docker/Dockerfile .
```

## Testing

### All Tests at Once (recommended)

```bash
bash docker/test_ros2.sh <dbc_file> <xml_config>
```

Builds the Docker image, creates vcan, runs all 4 test stages in the container.

### Individual Test Stages

#### 1. Rust Unit Tests

```bash
cd node && cargo test
```

26 tests: config parsing, signal decoding (signed/unsigned), encode/decode roundtrips, edge cases.

#### 2. Python Unit Tests

```bash
cd tools && python3 -m pytest test_parser.py test_xml_export.py -v
```

14 tests: DBC parser, XML export, roundtrip compatibility.

#### 3. Integration Test (local, no ROS2 needed)

Verifies the bridge **only passes through signals defined in the XML config**.

```bash
# Create vcan (once)
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# Filter test: only VelAndAngPOI + AccHor allowed, rest blocked
python3 test-pipeline/run_integration.py \
    dbc/SensoricSolutionsOMSRace.dbc \
    config/test_partial.xml
```

Checks 4 criteria:
- Allowed signals **must** appear in output
- Non-configured messages **must not** pass through
- Non-configured signals within allowed messages **must not** pass through
- Unknown CAN IDs are ignored

#### 4. ROS2 End-to-End Test (Docker)

Verifies signals **actually arrive as ROS2 topics with correct values**.

```bash
docker run --rm --privileged --network host \
    -v $(pwd):/ws can-ros2-bridge bash -c "
    source /opt/ros/humble/setup.bash
    ip link show vcan0 || (ip link add dev vcan0 type vcan && ip link set up vcan0)
    python3 /ws/test-pipeline/run_ros2_test.py \
        /ws/dbc/SensoricSolutionsOMSRace.dbc \
        /ws/config/config_SensoricSolutionsOMSRace_040326_1846.xml
"
```

Checks:
- Expected ROS2 topics exist (`ros2 topic list`)
- Each topic delivers the correct value (`ros2 topic echo --once`)
- Blocked messages produce **no** topics

## Creating a Config (DBC Mapper)

### GUI

```bash
python3 tools/cli.py gui
```

Opens a Qt window: load a DBC file, select signals via checkboxes, edit ROS2 topic names, export as XML.

### CLI

```bash
python3 tools/cli.py map dbc/SensoricSolutionsOMSRace.dbc -o config/my_config.xml
```

## Running the Bridge

```bash
can-ros2-bridge --config config/my_config.xml --can-interface can0
```

Options:
- `--config` / `-c` - path to XML config (default: `config.xml`)
- `--can-interface` / `-i` - CAN interface (default: `can0`)

## Installing from GitHub Release

Download the `.deb` or `.rpm` from the [Releases](../../releases) page.

### Ubuntu/Debian

```bash
sudo dpkg -i can-ros2-bridge_*_amd64.deb
```

### Fedora

```bash
sudo rpm -i can-ros2-bridge-*.x86_64.rpm
```

This installs:
- `/usr/bin/can-ros2-bridge` - the bridge binary
- `/etc/can-ros2-bridge/config.xml` - example config
- `/lib/systemd/system/can_ros_bridge.service` - systemd unit

## Using the Bridge in Your ROS2 Project

The bridge runs as a standalone process alongside your ROS2 nodes. It publishes `std_msgs/msg/Float64` on the topics you defined in your XML config.

### Step 1: Install the bridge

```bash
# From release package
sudo dpkg -i can-ros2-bridge_*_amd64.deb   # Ubuntu
sudo rpm -i can-ros2-bridge-*.x86_64.rpm    # Fedora

# Or build from source
cd node && cargo build --release --features ros2
sudo cp target/release/can-ros2-bridge /usr/bin/
```

### Step 2: Create your config

Use the GUI to select which CAN signals you need and map them to topic names:

```bash
python3 tools/cli.py gui
# Save as /etc/can-ros2-bridge/config.xml
```

Example: if your config maps `VelXPoi` to `/vel/x`, the bridge publishes a `Float64` on `/vel/x` every time a CAN frame with that signal arrives.

### Step 3: Add to your ROS2 launch file

In your existing ROS2 project, include the bridge in your launch file:

```python
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    # Start the CAN-ROS2 bridge
    bridge = ExecuteProcess(
        cmd=[
            "can-ros2-bridge",
            "--config", "/etc/can-ros2-bridge/config.xml",
            "--can-interface", "can0",
        ],
        output="screen",
    )

    # Your own node that subscribes to the CAN signals
    my_node = Node(
        package="my_package",
        executable="my_node",
    )

    return LaunchDescription([bridge, my_node])
```

### Step 4: Subscribe to the topics in your node

The bridge publishes `std_msgs/msg/Float64` on each configured topic. Subscribe in your node like any other ROS2 topic:

**Python:**
```python
from std_msgs.msg import Float64

class MyNode(Node):
    def __init__(self):
        super().__init__("my_node")
        # Subscribe to CAN signals published by the bridge
        self.sub_vel = self.create_subscription(
            Float64, "/vel/x", self.on_velocity, 10)
        self.sub_acc = self.create_subscription(
            Float64, "/acc/x", self.on_acceleration, 10)

    def on_velocity(self, msg: Float64):
        self.get_logger().info(f"Velocity X: {msg.data} km/h")

    def on_acceleration(self, msg: Float64):
        self.get_logger().info(f"Acceleration X: {msg.data} m/s^2")
```

**C++:**
```cpp
#include <std_msgs/msg/float64.hpp>

class MyNode : public rclcpp::Node {
public:
    MyNode() : Node("my_node") {
        sub_vel_ = create_subscription<std_msgs::msg::Float64>(
            "/vel/x", 10,
            [this](std_msgs::msg::Float64::SharedPtr msg) {
                RCLCPP_INFO(get_logger(), "Velocity X: %.2f km/h", msg->data);
            });
    }
private:
    rclcpp::Subscription<std_msgs::msg::Float64>::SharedPtr sub_vel_;
};
```

### Step 5: Run as a systemd service (optional)

For production use, run the bridge as a background service:

```bash
# Edit config and interface if needed
sudo vim /lib/systemd/system/can_ros_bridge.service

# Enable and start
sudo systemctl enable --now can_ros_bridge

# Check logs
sudo journalctl -u can_ros_bridge -f
```

The bridge will auto-restart on failure and start on boot.

### Available topics

To see which topics the bridge publishes, check your XML config or run:

```bash
ros2 topic list | grep -v /parameter_events
ros2 topic echo --once /vel/x   # read a single value
ros2 topic hz /vel/x             # check publish rate
```

## XML Config Format

```xml
<bridge>
    <message id="1536" name="VelAndAngPOI">
        <signal name="VelXPoi" start_bit="0" length="16"
                byte_order="little_endian" signed="true"
                scale="0.02" offset="0" topic="/vel/x" />
    </message>
</bridge>
```

Signal attributes:
- `start_bit` / `length` - position in CAN frame
- `byte_order` - `little_endian` or `big_endian`
- `signed` - `true` for signed values
- `scale` / `offset` - physical value = raw * scale + offset
- `topic` - ROS2 topic name (publishes `std_msgs/msg/Float64`)

## License

MIT License - see [LICENSE](LICENSE).
