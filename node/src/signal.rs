use crate::config::SignalMapping;

pub fn decode_signal(data: &[u8], signal: &SignalMapping) -> f64 {
    let raw = extract_bits(data, signal.start_bit, signal.length, &signal.byte_order);
    let value = if signal.signed {
        to_signed(raw, signal.length) as f64
    } else {
        raw as f64
    };
    value * signal.scale + signal.offset
}

pub fn encode_signal(data: &mut [u8], signal: &SignalMapping, value: f64) {
    let raw_f = (value - signal.offset) / signal.scale;
    let raw = if signal.signed {
        from_signed(raw_f as i64, signal.length)
    } else {
        raw_f as u64
    };
    insert_bits(data, signal.start_bit, signal.length, &signal.byte_order, raw);
}

fn to_signed(value: u64, bit_length: u8) -> i64 {
    let sign_bit = 1u64 << (bit_length - 1);
    if value & sign_bit != 0 {
        value as i64 - (1i64 << bit_length)
    } else {
        value as i64
    }
}

fn from_signed(value: i64, bit_length: u8) -> u64 {
    if value < 0 {
        (value + (1i64 << bit_length)) as u64
    } else {
        value as u64
    }
}

fn extract_bits(data: &[u8], start_bit: u8, length: u8, byte_order: &str) -> u64 {
    let mut value: u64 = 0;
    let is_big = byte_order == "big_endian";
    for i in 0..length as u64 {
        let bit_pos = start_bit as u64 + i;
        let byte_idx = (bit_pos / 8) as usize;
        let bit_idx = if is_big { 7 - (bit_pos % 8) } else { bit_pos % 8 };
        let out_bit = if is_big { length as u64 - 1 - i } else { i };
        if byte_idx < data.len() && (data[byte_idx] >> bit_idx) & 1 == 1 {
            value |= 1 << out_bit;
        }
    }
    value
}

fn insert_bits(data: &mut [u8], start_bit: u8, length: u8, byte_order: &str, value: u64) {
    let is_big = byte_order == "big_endian";
    for i in 0..length as u64 {
        let bit_pos = start_bit as u64 + i;
        let byte_idx = (bit_pos / 8) as usize;
        let bit_idx = if is_big { 7 - (bit_pos % 8) } else { bit_pos % 8 };
        let val_bit = if is_big { length as u64 - 1 - i } else { i };
        if byte_idx < data.len() {
            if (value >> val_bit) & 1 == 1 {
                data[byte_idx] |= 1 << bit_idx;
            } else {
                data[byte_idx] &= !(1 << bit_idx);
            }
        }
    }
}
