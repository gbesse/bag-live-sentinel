"""Optional ROS 2 topic subscriber that updates a heartbeat file."""

import argparse
import os
from pathlib import Path
import sys


ERROR = {"fr": "Abonnement ROS 2 impossible", "en": "ROS 2 subscription failed", "es": "Falló la suscripción ROS 2"}


def subscribe(topic, message_type, heartbeat_file):
    try:
        import rclpy
        from rclpy.qos import qos_profile_sensor_data
        from rosidl_runtime_py.utilities import get_message
    except ImportError as exc:
        raise RuntimeError("rclpy/rosidl_runtime_py") from exc
    path = Path(heartbeat_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = rclpy.create_node("bag_live_heartbeat")

    def received(_message):
        path.touch()
        os.utime(path, None)

    node.create_subscription(get_message(message_type), topic, received, qos_profile_sensor_data)
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def main(argv=None):
    parser = argparse.ArgumentParser(description="ROS 2 heartbeat / Battement ROS 2 / Latido ROS 2")
    parser.add_argument("topic")
    parser.add_argument("message_type")
    parser.add_argument("heartbeat_file")
    parser.add_argument("--locale", choices=ERROR, default="en")
    args = parser.parse_args(argv)
    try:
        subscribe(args.topic, args.message_type, args.heartbeat_file)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"{ERROR[args.locale]}: {exc if args.locale == 'en' else type(exc).__name__}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
