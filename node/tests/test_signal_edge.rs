use can_ros2_bridge::config::SignalMapping;
use can_ros2_bridge::signal::{decode_signal, encode_signal};

fn make_signal(start_bit: u8, length: u8, signed: bool, scale: f64, offset: f64) -> SignalMapping {
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

#[test]
fn encode_decode_roundtrip_all_vel_signals() {
    let signals = [
        (0u8, "VelXPoi"), (16, "VelYPoi"), (32, "VelAPoi"), (48, "AngSPoi"),
    ];
    let values = [0.0, 100.0, -50.0, 225.0, -225.0];
    for (start, _name) in &signals {
        let sig = make_signal(*start, 16, true, 0.02, 0.0);
        for &val in &values {
            let mut data = [0u8; 8];
            encode_signal(&mut data, &sig, val);
            let decoded = decode_signal(&data, &sig);
            assert!((decoded - val).abs() < 0.02, "failed for {_name} val={val}");
        }
    }
}

#[test]
fn multiple_signals_in_same_frame() {
    // Simulate VelAndAngPOI frame with all 4 signals
    let mut data = [0u8; 8];
    let vel_x = make_signal(0, 16, true, 0.02, 0.0);
    let vel_y = make_signal(16, 16, true, 0.02, 0.0);
    let vel_a = make_signal(32, 16, true, 0.02, 0.0);
    let ang_s = make_signal(48, 16, true, 0.003, 0.0);

    encode_signal(&mut data, &vel_x, 120.0);
    encode_signal(&mut data, &vel_y, -30.0);
    encode_signal(&mut data, &vel_a, 123.46);
    encode_signal(&mut data, &ang_s, -5.1);

    assert!((decode_signal(&data, &vel_x) - 120.0).abs() < 0.02);
    assert!((decode_signal(&data, &vel_y) - (-30.0)).abs() < 0.02);
    assert!((decode_signal(&data, &vel_a) - 123.46).abs() < 0.02);
    assert!((decode_signal(&data, &ang_s) - (-5.1)).abs() < 0.003);
}

#[test]
fn zero_value_signals() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let data = [0u8; 8];
    assert_eq!(decode_signal(&data, &sig), 0.0);
}

#[test]
fn max_unsigned_value() {
    let sig = make_signal(0, 16, false, 1.0, 0.0);
    let data = [0xFF, 0xFF, 0, 0, 0, 0, 0, 0];
    assert_eq!(decode_signal(&data, &sig), 65535.0);
}

#[test]
fn single_bit_signals() {
    // Test all 8 bit positions in first byte (like Status message flags)
    for bit in 0..8u8 {
        let sig = make_signal(bit, 1, false, 1.0, 0.0);
        let data = [1u8 << bit, 0, 0, 0, 0, 0, 0, 0];
        assert_eq!(decode_signal(&data, &sig), 1.0, "bit {bit}");
    }
}

#[test]
fn signed_min_max_16bit() {
    let sig = make_signal(0, 16, true, 1.0, 0.0);
    // Max positive: 32767
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 32767.0);
    assert_eq!(decode_signal(&data, &sig), 32767.0);
    // Min negative: -32768
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -32768.0);
    assert_eq!(decode_signal(&data, &sig), -32768.0);
}

#[test]
fn three_byte_signal() {
    // SampleTime: start_bit=32, length=24, unsigned, scale=0.001
    let sig = make_signal(32, 24, false, 0.001, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 1234.567);
    let val = decode_signal(&data, &sig);
    assert!((val - 1234.567).abs() < 0.001);
}

#[test]
fn encode_preserves_other_bits() {
    let mut data = [0xFF; 8];
    let sig = make_signal(0, 8, false, 1.0, 0.0);
    encode_signal(&mut data, &sig, 0.0);
    assert_eq!(data[0], 0x00);
    assert_eq!(data[1], 0xFF); // untouched
}
