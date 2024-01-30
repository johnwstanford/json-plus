use std::collections::VecDeque;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

const HEARTBEAT: [u8; 20] = [
    0x4A, 0x53, 0x4F, 0x4E, 0x50, 0x4C, 0x55, 0x53,     // "JSONPLUS"
    0x14, 0x00, 0x00, 0x00,     // Overall length (including 20 bytes of header)
    0x00, 0x00, 0x00, 0x00,     // JSON length
    0x00, 0x00, 0x00, 0x00,     // Payload length
];

const HEARTBEAT_RATE: Duration = Duration::from_secs(10);

#[derive(Debug)]
struct Header {
    title_word: [u8; 8],
    total_len: u32,
    json_len: u32,
    payload_len: u32,
}

fn main() -> Result<(), &'static str> {

    println!("JSON Plus Server");

    let in_port: u16  = 30008;
    let out_port: u16 = 30009;

    let in_streams: Arc<Mutex<VecDeque<TcpStream>>> = Arc::new(Mutex::new(VecDeque::new()));
    let out_streams: Arc<Mutex<VecDeque<TcpStream>>> = Arc::new(Mutex::new(VecDeque::new()));

    let transit: Arc<Mutex<VecDeque<Vec<u8>>>> = Arc::new(Mutex::new(VecDeque::new()));
    let recycle: Arc<Mutex<VecDeque<Vec<u8>>>> = Arc::new(Mutex::new(VecDeque::new()));

    let in_streams_listen = in_streams.clone();
    let in_listener = TcpListener::bind(format!("0.0.0.0:{}", in_port))
        .map_err(|_| "Unable to bind")?;
    std::thread::spawn(move || {

        for stream in in_listener.incoming() {
            if let Ok(stream) = stream {
                let addr = stream.peer_addr();
                println!("Connected to input from {:?}", addr);
                in_streams_listen.lock().unwrap().push_back(stream);
            }
        }
    });

    let out_streams_listen = out_streams.clone();
    let out_listener = TcpListener::bind(format!("0.0.0.0:{}", out_port))
        .map_err(|_| "Unable to bind")?;
    std::thread::spawn(move || {
        for stream in out_listener.incoming() {
            if let Ok(stream) = stream {
                let addr = stream.peer_addr();
                println!("New output subscription request from {:?}", addr);
                out_streams_listen.lock().unwrap().push_back(stream);
            }
        }

    });

    let in_streams_worker = in_streams.clone();
    let transit_worker = transit.clone();
    let recycle_worker = recycle.clone();
    std::thread::spawn(move || {
        let mut header_buff: [u8; 20] = [0; 20];
        loop {
            let opt_s = in_streams_worker.lock().unwrap().pop_front();
            if let Some(mut s) = opt_s {
                let r = s.read(&mut header_buff).ok();
                if r == Some(20) {
                    let header: Header = unsafe{ std::mem::transmute(header_buff.clone()) };
                    let n = header.total_len as usize;
                    println!("IN: {:?}", header);

                    let mut buff = recycle_worker.lock().unwrap().pop_front().unwrap_or_default();
                    buff.resize(n, 0);
                    if s.read(&mut buff[20..]).ok() == Some(n-20) {
                        if &header.title_word[..] == &HEARTBEAT[..8] {
                            println!("Checks OK, forwarding to subscribers");
                            transit_worker.lock().unwrap().push_back(buff);
                        }
                    }
                }

                if r.is_some() {
                    in_streams_worker.lock().unwrap().push_back(s);
                }

            }
        }
    });

    // Use the main thread to process output
    let mut last_heartbeat = Instant::now();
    loop {

        if let Some(buff) = transit.lock().unwrap().pop_front() {
            out_streams.lock().unwrap().retain(|mut s| s.write_all(&buff[..]).is_ok());
            recycle.lock().unwrap().push_back(buff);
        }

        if last_heartbeat.elapsed() > HEARTBEAT_RATE {
            last_heartbeat = Instant::now();

            // This is also a chance to prune connections
            out_streams.lock().unwrap().retain(|mut s| s.write_all(&HEARTBEAT).is_ok());
        }
    }

}