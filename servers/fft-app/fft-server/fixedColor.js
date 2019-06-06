const dgram = require('dgram');

const PORT = 4210;
const HOST = '224.3.29.71';

const client = dgram.createSocket('udp4');

module.exports = {
    sendFixedColor(color) {
        const message = Buffer.from([
            3, // 3 lights
            0, // broadcast
            0, // ID (unused)
            0, // reserved

            // Single color is (r, g, b)
            // Spread it out to all three lights, and
            // set W to 0.
            color.r, color.g, color.b, 0,
            color.r, color.g, color.b, 0,
            color.r, color.g, color.b, 0,
        ]);

        client.send(message, 0, message.length, PORT, HOST, function(err, bytes) {
            if (err) {
                console.log(err);
            }
        });
    }
};
