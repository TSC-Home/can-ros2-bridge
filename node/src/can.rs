use socketcan::{CanFrame, CanSocket, EmbeddedFrame, Frame, Socket};
use std::collections::HashSet;
use std::time::Duration;

pub struct CanBus {
    socket: CanSocket,
    filter_ids: HashSet<u32>,
}

impl CanBus {
    pub fn open(interface: &str, filter_ids: Vec<u32>) -> Result<Self, socketcan::Error> {
        let socket = CanSocket::open(interface)?;
        socket.set_read_timeout(Duration::from_millis(100))?;
        let filter_ids: HashSet<u32> = filter_ids.into_iter().collect();
        Ok(Self { socket, filter_ids })
    }

    pub fn read_frame(&self) -> Result<Option<(u32, Vec<u8>)>, socketcan::Error> {
        let frame = match self.socket.read_frame() {
            Ok(f) => f,
            Err(e) if e.kind() == std::io::ErrorKind::WouldBlock || e.kind() == std::io::ErrorKind::TimedOut => {
                return Ok(None);
            }
            Err(e) => return Err(socketcan::Error::Io(e)),
        };
        if let CanFrame::Data(data_frame) = frame {
            let id = data_frame.raw_id() & 0x1FFFFFFF;
            if self.filter_ids.is_empty() || self.filter_ids.contains(&id) {
                return Ok(Some((id, data_frame.data().to_vec())));
            }
        }
        Ok(None)
    }

    pub fn write_frame(&self, id: u32, data: &[u8]) -> Result<(), socketcan::Error> {
        let frame = CanFrame::new(
            socketcan::StandardId::new(id as u16).expect("invalid CAN ID"),
            data,
        )
        .expect("invalid frame data");
        self.socket.write_frame(&frame)?;
        Ok(())
    }
}
