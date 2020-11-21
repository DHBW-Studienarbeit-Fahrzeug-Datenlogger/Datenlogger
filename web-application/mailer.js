var nodemailer = require('nodemailer');
var jwt = require('jsonwebtoken');
var getIP = require('./getIP.js');
var fs = require('fs');

function mailer(id, email, mode) {
    // Callback function for mailer()
    jwt.sign(
     // First argument
    {
        user: id,
        },
        // Second argument
        process.env.MAIL_SECRET,
        // ^Third argument
    {
        expiresIn: '1d',
        },
    // Callback function for jwt.sign()
        (err, emailToken) => {
        // Creates Transport ???
        var transporter = nodemailer.createTransport({
            // Arguments for nodemailer.createTransport
            service: 'gmail',
            auth: {
                user: process.env.MAIL_NAME,
                pass: process.env.MAIL_PASSWORD
            }
        });


        // Get the local IP
        var add = getIP();
        if (mode === "confirmation") {
            // Create Page on localhost port 3000
            const url = `http://${add}:3000/confirmation/${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Confirm your email!',
                html: `Please click this link to confirm your email: <a href="${url}">${url}</a>`
            };
        } else if (mode === "resetpw") {
            const url = `http://${add}:3000/resetpw${emailToken}`;
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: email,
                subject: 'Reset your password!',
                html: `Please click this link to reset your password: <a href="${url}">${url}</a>`
            };


            /*
             If there is a new local IP (because the server location changed), 
             the user gets an email with the link to the new local server homepage.
             */
        } else if (mode === "getIP") {
            // Create page on the local IP at port 3000
            const url = `http://${add}:3000`;
            // Get file ip.json as ip
            var ip = require("./ip.json");
            // log the IP from ip
            console.log("IP-test: " + ip.ip);
            // If the saved IP is not the local one, write the local IP to the JSON file
            if (ip.ip != add) {
                fs.writeFileSync("./ip.json", JSON.stringify({ "ip": add }));
                // Send a mail
                mail = email;
            } else {
                // IP is the same --> Send no mail
                mail = none;
            }
            // Define mail options for sending a link to the server homepage
            var mailOptions = {
                from: process.env.MAIL_NAME,
                to: mail,
                subject: 'Your Server-Homepage!',
                html: `Please click this link to connect to the Server-Homepage: <a href="${url}">${url}</a>`
            };
        } // Ifs finished

        // Send the mail with the defined mail options
        transporter.sendMail(mailOptions, async (error, info) => {
            if (error) {
                console.log(error);
            } else {
                console.log('Email sent: ' + info.response);
            }
        });
    });
}
module.exports = mailer; 