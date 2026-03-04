mod helpers;

use can_ros2_bridge::signal::{decode_signal, encode_signal};
use helpers::make_signal;

// --- VelAndAngPOI (ID 1536) tests ---

#[test]
fn decode_vel_x_positive() {
    let data = [0x88, 0x13, 0, 0, 0, 0, 0, 0]; // raw=5000, *0.02 = 100
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    assert!((decode_signal(&data, &sig) - 100.0).abs() < 0.001);
}

#[test]
fn decode_vel_x_negative() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -50.0);
    assert!((decode_signal(&data, &sig) - (-50.0)).abs() < 0.001);
}

#[test]
fn decode_vel_y_at_offset() {
    let sig = make_signal(16, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 25.5);
    assert!((decode_signal(&data, &sig) - 25.5).abs() < 0.02);
}

#[test]
fn decode_ang_s_poi() {
    let sig = make_signal(48, 16, true, 0.003, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 15.0);
    assert!((decode_signal(&data, &sig) - 15.0).abs() < 0.003);
}

// --- AccHor (ID 1539) tests ---

#[test]
fn decode_acc_x_positive() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 9.81);
    assert!((decode_signal(&data, &sig) - 9.81).abs() < 0.02);
}

#[test]
fn decode_acc_negative() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -9.81);
    assert!((decode_signal(&data, &sig) - (-9.81)).abs() < 0.02);
}

// --- Status (ID 1547) tests ---

#[test]
fn decode_standstill_flag() {
    let sig = make_signal(0, 1, false, 1.0, 0.0);
    assert_eq!(decode_signal(&[0x01, 0, 0, 0, 0, 0, 0, 0], &sig), 1.0);
    assert_eq!(decode_signal(&[0x00, 0, 0, 0, 0, 0, 0, 0], &sig), 0.0);
}

#[test]
fn decode_temp_sensor() {
    let sig = make_signal(16, 16, true, 0.1, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 25.0);
    assert!((decode_signal(&data, &sig) - 25.0).abs() < 0.1);
}

#[test]
fn decode_temp_sensor_negative() {
    let sig = make_signal(16, 16, true, 0.1, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, -10.0);
    assert!((decode_signal(&data, &sig) - (-10.0)).abs() < 0.1);
}
