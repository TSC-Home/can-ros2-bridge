use crate::can::CanBus;
use crate::config::BridgeConfig;
use crate::signal::decode_signal;
use std::collections::HashMap;

pub struct Bridge {
    can: CanBus,
    config: BridgeConfig,
    msg_lookup: HashMap<u32, usize>,
    #[cfg(feature = "ros2")]
    ros: crate::ros::RosNode,
}

impl Bridge {
    pub fn new(config: BridgeConfig, interface: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let filter_ids: Vec<u32> = config.messages.iter().map(|m| m.id).collect();

        let mut msg_lookup = HashMap::new();
        for (i, msg) in config.messages.iter().enumerate() {
            msg_lookup.insert(msg.id, i);
        }

        #[cfg(feature = "ros2")]
        let topics: Vec<String> = config
            .messages
            .iter()
            .flat_map(|m| m.signals.iter().map(|s| s.topic.clone()))
            .collect();

        let can = CanBus::open(interface, filter_ids)?;

        Ok(Self {
            can,
            config,
            msg_lookup,
            #[cfg(feature = "ros2")]
            ros: crate::ros::RosNode::new(topics)?,
        })
    }

    pub fn run(&self) -> Result<(), Box<dyn std::error::Error>> {
        loop {
            if let Some((id, data)) = self.can.read_frame()? {
                self.process_frame(id, &data)?;
            }
        }
    }

    fn process_frame(&self, id: u32, data: &[u8]) -> Result<(), Box<dyn std::error::Error>> {
        let msg_idx = match self.msg_lookup.get(&id) {
            Some(idx) => *idx,
            None => return Ok(()),
        };
        let msg = &self.config.messages[msg_idx];

        for signal in &msg.signals {
            let value = decode_signal(data, signal);
            println!("[{}] {} = {:.4}", msg.name, signal.name, value);

            #[cfg(feature = "ros2")]
            self.ros.publish_value(&signal.topic, value)?;
        }
        Ok(())
    }
}
