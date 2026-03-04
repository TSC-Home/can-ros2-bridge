use can_ros2_bridge::config::parse_config;

const SENSORIC_XML: &str = r#"
<bridge>
    <message id="1536" name="VelAndAngPOI">
        <signal name="VelXPoi" start_bit="0" length="16"
                byte_order="little_endian" signed="true" scale="0.02" offset="0"
                topic="/vel/x" />
        <signal name="VelYPoi" start_bit="16" length="16"
                byte_order="little_endian" signed="true" scale="0.02" offset="0"
                topic="/vel/y" />
    </message>
    <message id="1539" name="AccHor">
        <signal name="AccXHor" start_bit="0" length="16"
                byte_order="little_endian" signed="true" scale="0.02" offset="0"
                topic="/acc/x" />
    </message>
    <message id="1547" name="Status">
        <signal name="Standstill" start_bit="0" length="1"
                byte_order="little_endian" scale="1" offset="0"
                topic="/status/standstill" />
    </message>
</bridge>"#;

#[test]
fn parse_sensoric_config_messages() {
    let config = parse_config(SENSORIC_XML).unwrap();
    assert_eq!(config.messages.len(), 3);
    assert_eq!(config.messages[0].name, "VelAndAngPOI");
    assert_eq!(config.messages[1].name, "AccHor");
    assert_eq!(config.messages[2].name, "Status");
}

#[test]
fn parse_sensoric_can_ids() {
    let config = parse_config(SENSORIC_XML).unwrap();
    assert_eq!(config.messages[0].id, 1536);
    assert_eq!(config.messages[1].id, 1539);
    assert_eq!(config.messages[2].id, 1547);
}

#[test]
fn parse_sensoric_signal_count() {
    let config = parse_config(SENSORIC_XML).unwrap();
    assert_eq!(config.messages[0].signals.len(), 2);
    assert_eq!(config.messages[1].signals.len(), 1);
    assert_eq!(config.messages[2].signals.len(), 1);
}

#[test]
fn parse_signal_attributes() {
    let config = parse_config(SENSORIC_XML).unwrap();
    let vel_x = &config.messages[0].signals[0];
    assert_eq!(vel_x.name, "VelXPoi");
    assert_eq!(vel_x.start_bit, 0);
    assert_eq!(vel_x.length, 16);
    assert!(vel_x.signed);
    assert_eq!(vel_x.scale, 0.02);
    assert_eq!(vel_x.topic, "/vel/x");
}

#[test]
fn parse_unsigned_signal() {
    let config = parse_config(SENSORIC_XML).unwrap();
    let standstill = &config.messages[2].signals[0];
    assert!(!standstill.signed);
    assert_eq!(standstill.length, 1);
}

#[test]
fn load_config_file() {
    let config = can_ros2_bridge::config::load_config("../config/sensoric_solutions.xml").unwrap();
    assert!(!config.messages.is_empty());
}

#[test]
fn load_config_missing_file() {
    let result = can_ros2_bridge::config::load_config("/nonexistent.xml");
    assert!(result.is_err());
}

#[test]
fn parse_empty_config() {
    let config = parse_config("<bridge></bridge>").unwrap();
    assert!(config.messages.is_empty());
}

#[test]
fn parse_message_without_signals() {
    let xml = r#"<bridge><message id="100" name="Empty"></message></bridge>"#;
    let config = parse_config(xml).unwrap();
    assert_eq!(config.messages[0].signals.len(), 0);
}
