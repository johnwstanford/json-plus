use std::io::Write;
use std::net::{Ipv4Addr, TcpListener};
use std::time::Duration;

const HEARTBEAT: [u8; 20] = [
    0x4A, 0x53, 0x4F, 0x4E, 0x50, 0x4C, 0x55, 0x53,     // "JSONPLUS"
    0x00, 0x00, 0x00, 0x00,     // Overall length (including 20 bytes of header)
    0x00, 0x00, 0x00, 0x00,     // JSON length
    0x00, 0x00, 0x00, 0x00,     // Payload length
];

const HEARTBEAT_RATE: Duration = Duration::from_secs(10);

fn main() -> Result<(), &'static str> {

    println!("JSON Plus Server");

    let out_port: u16 = 30009;

    let listener = TcpListener::bind(format!("0.0.0.0:{}", out_port))
        .map_err(|_| "Unable to bind")?;

    for stream in listener.incoming() {
        let mut stream = stream.map_err(|_| "Stream creation failed")?;
        println!("Connected to {:?}", stream.peer_addr());

        loop {
            stream.write_all(&HEARTBEAT).map_err(|_| "Unable to send heartbeat")?;
            std::thread::sleep(HEARTBEAT_RATE);
        }
    }

    Ok(())

}