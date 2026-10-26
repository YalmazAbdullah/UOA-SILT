import dgram from 'node:dgram';

const HOST = '127.0.0.1'
const PORT = 5000

function sendLog(log) {
    
    try {
        const client = dgram.createSocket('udp4');

        const payload = {
            target_time: new Date().toISOString(),
            source: 'target',
            target: 'jstest',
            event: 'sending_log_js',
            data: { message: log }
        };

        const data = Buffer.from(JSON.stringify(payload), 'UTF8');

        client.send(data, PORT, HOST, (error) => {
            if (error) {
                console.error('Failed to send UDP packet:', error);
            }

            client.close();
        });
    } catch (error) {
        console.error('Unexpected error:', error);
    }

}

sendLog('Hello world');
