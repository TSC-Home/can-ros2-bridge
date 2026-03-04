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

// --- VelAndAngPOI (ID 1536) tests ---

#[test]
fn decode_vel_x_positive() {
    // VelXPoi: 100 km/h → raw = 100/0.02 = 5000 = 0x1388
    let data = [0x88, 0x13, 0, 0, 0, 0, 0, 0];
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let val = decode_signal(&data, &sig);
    assert!((val - 100.0).abs() < 0.001);
}

#[test]
fn decode_vel_x_negative() {
    // VelXPoi: -50 km/h → raw signed = -2500 → unsigned 16bit = 63036 = 0xF63C
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -50.0);
    let val = decode_signal(&data, &sig);
    assert!((val - (-50.0)).abs() < 0.001);
}

#[test]
fn decode_vel_y_at_offset() {
    // VelYPoi at start_bit=16: 25.5 km/h → raw = 1275
    let sig = make_signal(16, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 25.5);
    let val = decode_signal(&data, &sig);
    assert!((val - 25.5).abs() < 0.02);
}

#[test]
fn decode_ang_s_poi() {
    // AngSPoi: start_bit=48, scale=0.003, 15 degrees → raw = 5000
    let sig = make_signal(48, 16, true, 0.003, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 15.0);
    let val = decode_signal(&data, &sig);
    assert!((val - 15.0).abs() < 0.003);
}

// --- AccHor (ID 1539) tests ---

#[test]
fn decode_acc_x_positive() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 9.81);
    let val = decode_signal(&data, &sig);
    assert!((val - 9.81).abs() < 0.02);
}

#[test]
fn decode_acc_negative() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -9.81);
    let val = decode_signal(&data, &sig);
    assert!((val - (-9.81)).abs() < 0.02);
}

// --- Status (ID 1547) tests ---

#[test]
fn decode_standstill_flag() {
    let sig = make_signal(0, 1, false, 1.0, 0.0);
    let data = [0x01, 0, 0, 0, 0, 0, 0, 0];
    assert_eq!(decode_signal(&data, &sig), 1.0);
    let data_off = [0x00, 0, 0, 0, 0, 0, 0, 0];
    assert_eq!(decode_signal(&data_off, &sig), 0.0);
}

#[test]
fn decode_temp_sensor() {
    // TempSensor: start_bit=16, length=16, signed, scale=0.1
    // 25.0°C → raw = 250
    let sig = make_signal(16, 16, true, 0.1, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 25.0);
    let val = decode_signal(&data, &sig);
    assert!((val - 25.0).abs() < 0.1);
}

#[test]
fn decode_temp_sensor_negative() {
    let sig = make_signal(16, 16, true, 0.1, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -10.0);
    let val = decode_signal(&data, &sig);
    assert!((val - (-10.0)).abs() < 0.1);
}
