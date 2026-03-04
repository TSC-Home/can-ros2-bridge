use quick_xml::de::from_str;
use serde::Deserialize;
use std::fs;

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct BridgeConfig {
    #[serde(rename = "message", default)]
    pub messages: Vec<MessageMapping>,
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct MessageMapping {
    #[serde(rename = "@id")]
    pub id: u32,
    #[serde(rename = "@name")]
    pub name: String,
    #[serde(rename = "signal", default)]
    pub signals: Vec<SignalMapping>,
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct SignalMapping {
    #[serde(rename = "@name")]
    pub name: String,
    #[serde(rename = "@start_bit")]
    pub start_bit: u8,
    #[serde(rename = "@length")]
    pub length: u8,
    #[serde(rename = "@byte_order", default = "default_byte_order")]
    pub byte_order: String,
    #[serde(rename = "@signed", default)]
    pub signed: bool,
    #[serde(rename = "@scale", default = "default_scale")]
    pub scale: f64,
    #[serde(rename = "@offset", default)]
    pub offset: f64,
    #[serde(rename = "@topic")]
    pub topic: String,
}

fn default_byte_order() -> String {
    "little_endian".to_string()
}

fn default_scale() -> f64 {
    1.0
}

pub fn load_config(path: &str) -> Result<BridgeConfig, Box<dyn std::error::Error>> {
    let xml = fs::read_to_string(path)?;
    parse_config(&xml)
}

pub fn parse_config(xml: &str) -> Result<BridgeConfig, Box<dyn std::error::Error>> {
    let config: BridgeConfig = from_str(xml)?;
    Ok(config)
}
