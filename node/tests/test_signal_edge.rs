mod helpers;

use can_ros2_bridge::signal::{decode_signal, encode_signal};
use helpers::make_signal;

#[test]
fn encode_decode_roundtrip_all_vel_signals() {
    let starts = [0u8, 16, 32, 48];
    let values = [0.0, 100.0, -50.0, 225.0, -225.0];
    for start in starts {
        let sig = make_signal(start, 16, true, 0.02, 0.0);
        for &val in &values {
            let mut data = [0u8; 8];
            encode_signal(&mut data, &sig, val);
            assert!((decode_signal(&data, &sig) - val).abs() < 0.02);
        }
    }
}

#[test]
fn multiple_signals_in_same_frame() {
    let mut data = [0u8; 8];
    let sigs = [
        make_signal(0, 16, true, 0.02, 0.0),
        make_signal(16, 16, true, 0.02, 0.0),
        make_signal(32, 16, true, 0.02, 0.0),
        make_signal(48, 16, true, 0.003, 0.0),
    ];
    let vals = [120.0, -30.0, 123.46, -5.1];
    let tols = [0.02, 0.02, 0.02, 0.003];

    for (sig, &val) in sigs.iter().zip(&vals) {
        encode_signal(&mut data, sig, val);
    }
    for ((sig, &val), &tol) in sigs.iter().zip(&vals).zip(&tols) {
        assert!((decode_signal(&data, sig) - val).abs() < tol);
    }
}

#[test]
fn zero_value_signals() {
    let sig = make_signal(0, 16, true, 0.02, 0.0);
    assert_eq!(decode_signal(&[0u8; 8], &sig), 0.0);
}

#[test]
fn max_unsigned_value() {
    let sig = make_signal(0, 16, false, 1.0, 0.0);
    assert_eq!(decode_signal(&[0xFF, 0xFF, 0, 0, 0, 0, 0, 0], &sig), 65535.0);
}

#[test]
fn single_bit_signals() {
    for bit in 0..8u8 {
        let sig = make_signal(bit, 1, false, 1.0, 0.0);
        let data = [1u8 << bit, 0, 0, 0, 0, 0, 0, 0];
        assert_eq!(decode_signal(&data, &sig), 1.0, "bit {bit}");
    }
}

#[test]
fn signed_min_max_16bit() {
    let sig = make_signal(0, 16, true, 1.0, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 32767.0);
    assert_eq!(decode_signal(&data, &sig), 32767.0);
    encode_signal(&mut data, &sig, -32768.0);
    assert_eq!(decode_signal(&data, &sig), -32768.0);
}

#[test]
fn three_byte_signal() {
    let sig = make_signal(32, 24, false, 0.001, 0.0);
    let mut data = [0u8; 8];
    encode_signal(&mut data, &sig, 1234.567);
    assert!((decode_signal(&data, &sig) - 1234.567).abs() < 0.001);
}

#[test]
fn encode_preserves_other_bits() {
    let mut data = [0xFF; 8];
    let sig = make_signal(0, 8, false, 1.0, 0.0);
    encode_signal(&mut data, &sig, 0.0);
    assert_eq!(data[0], 0x00);
    assert_eq!(data[1], 0xFF);
}
