use clap::Parser;

#[derive(Parser)]
#[command(name = "can-ros2-bridge", about = "CAN to ROS2 bridge")]
struct Args {
    #[arg(short, long, default_value = "config.xml")]
    config: String,

    #[arg(short = 'i', long, default_value = "can0")]
    can_interface: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    println!("Loading config: {}", args.config);

    let config = can_ros2_bridge::config::load_config(&args.config)?;
    println!(
        "Loaded {} message(s), bridging on {}",
        config.messages.len(),
        args.can_interface
    );

    let bridge = can_ros2_bridge::bridge::Bridge::new(config, &args.can_interface)?;
    bridge.run()
}
