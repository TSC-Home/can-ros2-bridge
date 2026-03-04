use can_ros2_bridge::config::SignalMapping;

pub fn make_signal(start_bit: u8, length: u8, signed: bool, scale: f64, offset: f64) -> SignalMapping {
    SignalMapping {
        name: "test".into(),
        start_bit,
        length,
        byte_order: "little_endian".into(),
        signed,
        scale,
        offset,
        topic: "/test".into(),
    }
}
