import { fileURLToPath } from "url";

const datagram = require('dgram')

const HOST = '127.0.0.1'
const PORT = 5000
const APP_NAME = "place_holder"

function sendLog(log) {
    const client = datagram.createSocket('UDP4');

    const payload = {
        target: APP_NAME,
        log: log,
        // timestamp: new Date().toISOString()
    }

    const data = Buffer.from(JSON.stringify(payload), "UTF8");

    client.send(data, PORT, HOST, (error) => {
        if (error) {
            console.error(error);
        }
        client.close();
    });
}

sendLog("Hello world")

