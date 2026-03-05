use r2r::{self, std_msgs::msg::Float64, QosProfile};
use std::collections::HashMap;

pub struct RosNode {
    node: r2r::Node,
    publishers: HashMap<String, r2r::Publisher<Float64>>,
}

impl RosNode {
    pub fn new(topics: Vec<String>) -> Result<Self, Box<dyn std::error::Error>> {
        let ctx = r2r::Context::create()?;
        let mut node = r2r::Node::create(ctx, "can_bridge", "")?;
        let mut publishers = HashMap::new();

        for topic in topics {
            let pub_ = node.create_publisher::<Float64>(&topic, QosProfile::default())?;
            publishers.insert(topic, pub_);
        }

        Ok(Self {
            node,
            publishers,
        })
    }

    pub fn spin_once(&mut self) {
        self.node.spin_once(std::time::Duration::ZERO);
    }

    pub fn publish_value(&self, topic: &str, value: f64) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(pub_) = self.publishers.get(topic) {
            let msg = Float64 { data: value };
            pub_.publish(&msg)?;
        }
        Ok(())
    }
}
