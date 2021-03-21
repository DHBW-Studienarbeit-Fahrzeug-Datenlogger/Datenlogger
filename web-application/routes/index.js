/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Contains the different routes of the web application. Defines the 
    backend behavior of the application.
    At the end of teh file there are some custom functions that are used in 
    the program.
    Exports the router object.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring

*/




// REQUIREMENTS

var express = require('express');
// Create router object to handle the requests --> Able to create miltiple routes with router.get()
var router = express.Router();

var passport = require('passport');
const bcrypt = require('bcrypt');
var fs = require('fs');
var jwt = require('jsonwebtoken');
// Own module mailser for handlich the mail messages to the user
var mailer = require('../mailer.js');


// Time needed to calculate a single BCrypt hash --> bruteforcing more difficult
const saltRounds = 10;



// ROUTES

// GET home page --> Route matches when / is requested
router.get('/', function (req, res) {
    // Render a view and send the rendered HTML string to client; rendering: not writing <b> but interpreting the HTML tag
    res.render('home', { title: 'Home', home: true });
});

// Route to confirm the email
router.get('/confirmation/:token', function (req, res) {
    // Verify whether the json web token matches with the mail secret
    var id = jwt.verify(req.params.token, process.env.MAIL_SECRET);
    // Log the confirmed user by its ID
    console.log("User to be confirmed: " + id);
    // Establish connection to database
    var db = require('../db.js');
    // Set the column confirmed of the user to 1
    db.query('UPDATE users SET confirmed = 1 WHERE id = ?', [id.user], function (err, results, fields) {
        // If error occures, throw it
        if(err) throw err;
    });
    // Get back to the login page
    res.redirect('/login');
});



// GET information about the cars of the given car type; authenticationMiddleware() --> possible only for authenticated users
router.get('/getCars/:token', authenticationMiddleware(), function (req, res) {
    // Establish connection with database
    var db = require('../db.js');
    // Log the car type; token comes from the :token in the URL
    console.log("Car type: " + req.params.token)
    // Get the data from the cars of the specified type
    db.query('SELECT consumption, capacity, power, name FROM cars WHERE type=?', [req.params.token], function(err, results, fields) {
        // If error occures, throw it
        if (err) throw err;
        // Define empty array for the data
        var data = [];
        // For every car in the result, append a dictionary of the data to the data array
        for(var i = 0; i < results.length; i++) {
            data.push({
            consumption: results[i].consumption,
            capacity: results[i].capacity,
            power: results[i].power,
            name: results[i].name
            })
        }
        // Send the http response as the array of data
        res.send(data);
    });
});



// GET the obd data of the given filename
router.get('/getOBD/:token', authenticationMiddleware(), function (req, res) {
    console.log("/getOBD/");
    // Get the JSON file with the specified filename
    var address = '../../datafiles/' + req.params.token;
    // Parse the JSON file as the JSON object data
    var data = JSON.parse(fs.readFileSync(address, 'utf8'));
    // Delete the GPS coordinates from the JSON object
    delete data['GPS_Long'];
    delete data['GPS_Lat'];
    delete data['GPS_Alt'];
    // Send the http response as the JSON object
    res.send(data);
});



// GET the additional data of the given filename
router.get('/getAddData/:token', authenticationMiddleware(), function (req, res) {
    console.log("/getAddData/");
    // Get the JSON file with the specified filename
    var address = '../../datafiles/' + req.params.token;
    // Parse the JSON file as the JSON object data
    var data = JSON.parse(fs.readFileSync(address, 'utf8'));

    // Send the http response as the JSON object
    res.send(data);
});



// GET the ID for the route from a given filename
router.get('/getID/:filename', authenticationMiddleware(), function (req, res) {
    console.log("getID: " + filename);
    var db = require('../db.js');
    var filename = req.params.filename;
    var data = [];
    if(filename === "undefined" || filename === undefined){
	console.log("filename is undefined");
    }
    else{
	console.log("Getting filename");
        db.query('SELECT id FROM data WHERE filename=?', [filename], function (err, results, fields)  {
            // If error occures, throw it
            if (err) throw err;

            // Send back the id from the results if a result is found, otherwise send back 'none'
            if (results.length != 0) {
                data.push(results[0].id);
            }
        });
    }
    res.send(data);
    console.log("getID ended");
});



// Get all ids of the routes in data
router.get('/getIDs', authenticationMiddleware(), function (req, res) {
    console.log("getIDs");
    var db = require('../db.js');

    var id_list = [];

    db.query('SELECT id FROM data', function (err, results, fields) {
        // If error occures, throw it
        if (err) throw err;

        // Extract the IDs from the result and push them into the array
        for (var i = 0; i < results.length; i++) {
            id_list.push(results[i].id)
        }

        // Send back the list of IDs
        res.send(id_list)
    });
});



// Get all cars
router.get('/getAllCars', authenticationMiddleware(), function (req, res) {
    console.log("getAllCars");
    var db = require('../db.js');

    var car_list = [];

    db.query('SELECT name FROM cars', function (err, results, fields) {
        // If error occures, throw it
        if (err) throw err;

        // Extract the IDs from the result and push them into the array
        for (var i = 0; i < results.length; i++) {
            car_list.push(results[i].name)
        }

        // Send back the list of cars
        res.send(car_list)
    });
});


// Create the simulation and get the ID of the created route
router.get('/createSimulation', authenticationMiddleware(), function (req, res) {
    console.log("Creating simulation");
    let { PythonShell } = require('python-shell')

    var options = {
        // Each line of data ending with '\n' is emitted as a message
        mode: 'text',
        args: ['hello'],
        pythonOptions: ['-u'],
        scriptPath: '../python'
    };

    var text_received = "none";

    PythonShell.run('call_simulation.py', options, function (err, result) {
        if (err) throw err;
        text_received = results[0];
    });
    res.send([text_received]);
});



// GET the gps data of the given filename
router.get('/getGPS/:token', authenticationMiddleware(), function (req, res) {
    // Get the JSON file with the specified filename
    var address = '../../datafiles/' + req.params.token;
    // Parse the JSON file as the JSON object data
    var data = JSON.parse(fs.readFileSync(address, 'utf8'));
    // Delete all data but the GPS coordinates from the object
    delete data['AMBIANT_AIR_TEMP'];
    delete data['RPM'];
    delete data['RELATIVE_ACCEL_POS'];
    delete data['FUEL_LEVEL'];
    delete data['MAF'];
    delete data['COMMANDED_EQUIV_RATIO'];
    delete data['SPEED'];
    delete data['ENGINE_LOAD'];
    // Send the http response as the JSON object
    res.send(data);
});



// GET the gps data of the given vin
router.get('/getAllGPS/:sim_real/:selector/:value', authenticationMiddleware(), function (req, res) {
    // Get the specified selector and value
    var value = req.params.value;
    var selector = req.params.selector;
    // Establish connetion to the database
    var db = require('../db.js');

    // Determine whether to get data from table data (real cycles) or table simulations (simulated cycles)
    var sim_or_real = req.params.sim_real;
    console.log("Getting from table: "+sim_or_real)
    // Get some driving cycle data
    db.query('SELECT id, filename, vin, totalKM, energyConsumption FROM ' + sim_or_real, function (err, results, fields) {
        // If error occures, throw it
        if (err) throw err;
        // Define tmp as an array
        var tmp = [];
        // For every driving cycle in the result, if the selectors value matches, append a dictionary of the cycle data to the array tmp
        for (var i = 0; i < results.length; i++) {
	        console.log("result")
            if (value == "none") {
                tmp.push({
                    filename: results[i].filename,
                    totalKM: results[i].totalKM,
                    energyConsumption: results[i].energyConsumption,
                    id: results[i].id
                })
            }
            else if (selector == "vin") {
                // The vin is saved as a hash in the database, so it has to be compared with bcrypt
                if (bcrypt.compareSync(value, results[i].vin)) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "km_min") {
                var km_min = parseFloat(value);
                console.log(km_min);
                if ((km_min != NaN) && (km_min <= results[i].totalKM)) {
                    console.log("File added: " + results[i].filename);
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "consumption_min") {
                var consumption_min = parseFloat(value);
                if (consumption_min != NaN && consumption_min <= results[i].energyConsumption) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "id") {
                var id = parseInt(value);
                if (id != NaN && id == results[i].id) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
        }
        // Define the array data
        var data = [];
        // Define some necessary variables
        var averageTripLength = 0;
        var longestTrip = 0;
        var vConsumption = 0;
        // For every driving cycle in the array tmp, log the JSON filename, parse the JSON file as an JSON object, delete all data but
        // the GPS coordinates and calculate the relevant values (average trip length, longest trip, total energy consumption).
        for(var i = 0; i < tmp.length; i++) {
            console.log("File: " + tmp[i].filename)
            var address = '../../datafiles/' + tmp[i].filename;
            data[i] = JSON.parse(fs.readFileSync(address));
            delete data[i]['AMBIANT_AIR_TEMP'];
            delete data[i]['RPM'];
            delete data[i]['RELATIVE_ACCEL_POS'];
            delete data[i]['FUEL_LEVEL'];
            delete data[i]['MAF'];
            delete data[i]['COMMANDED_EQUIV_RATIO'];
            delete data[i]['SPEED'];
            delete data[i]['ENGINE_LOAD'];
            // Add filename to dictionary
            data[i]['filename'] = tmp[i].filename;
            // Calculate the average trip length and the total energy consumption
            averageTripLength += tmp[i].totalKM / tmp.length;
            if(longestTrip <= tmp[i].totalKM) {
            longestTrip = tmp[i].totalKM;
            }
            vConsumption += tmp[i].energyConsumption;
        }
        // Log the average trip length
        console.log("averageTripLength: " + averageTripLength)
        // Append general information as a dictionary to the data array
        data.push({
            averageTripLength: averageTripLength,
            longestTrip: longestTrip,
            vConsumption: vConsumption / (tmp.length * averageTripLength) * 100
        })
	console.log("General information pushed to data");
        // Send the http response as the array of data
        res.send(data);
	console.log("GetAllGPS ended");
    });
});



// GET the waiting points for the given vin
router.get('/getWaitingTime/:sim_real/:selector/:value', authenticationMiddleware(), function (req, res) {
    // Get the specified selector and value
    var selector = req.params.selector;
    var value = req.params.value;
    // Establish connection to database
    var db = require('../db.js');

    // Determine whether to get data from table data (real cycles) or table simulations (simulated cycles)
    var sim_or_real = req.params.sim_real;

    // Get some driving cycle data 
    db.query('SELECT id, date, starttime, endtime, endLat, endLong, endDate, vin, totalKM, energyConsumption, filename FROM ' + sim_or_real, function (err, results, fields) {
        // If error occures, throw it
        if (err) throw err;
        // Define array tmp
        var tmp = [];
        // For every driving cycle in the result, if the selectors value matches, append a dictionary of the cycle data to the array tmp
        for (var i = 0; i < results.length; i++) {
            if (value == "none") {
                tmp.push({
                    filename: results[i].filename,
                    totalKM: results[i].totalKM,
                    energyConsumption: results[i].energyConsumption,
                    date: results[i].date,
                    starttime: results[i].starttime,
                    endtime: results[i].endtime,
                    endLat: results[i].endLat,
                    endLong: results[i].endLong,
                    endDate: results[i].endDate
                })
            }
            else if (selector == "vin") {
                // The vin is saved as a hash in the database, so it has to be compared with bcrypt
                if (bcrypt.compareSync(value, results[i].vin)) {
		    console.log("File added: " + results[i].filename);
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        date: results[i].date,
                        starttime: results[i].starttime,
                        endtime: results[i].endtime,
                        endLat: results[i].endLat,
                        endLong: results[i].endLong,
                        endDate: results[i].endDate
                    })
                }
            }
            else if (selector == "km_min") {
                var km_min = parseFloat(value);
                if (km_min != NaN && km_min <= results[i].totalKM) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        date: results[i].date,
                        starttime: results[i].starttime,
                        endtime: results[i].endtime,
                        endLat: results[i].endLat,
                        endLong: results[i].endLong,
                        endDate: results[i].endDate
                    })
                }
            }
            else if (selector == "consumption_min") {
                var consumption_min = parseFloat(value);
                if (consumption_min != NaN && consumption_min <= results[i].energyConsumption) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        date: results[i].date,
                        starttime: results[i].starttime,
                        endtime: results[i].endtime,
                        endLat: results[i].endLat,
                        endLong: results[i].endLong,
                        endDate: results[i].endDate
                    })
                }
            }
            else if (selector == "id") {
                var id = parseInt(value);
                if (id != NaN && id == results[i].id) {
                    tmp.push({
                        filename: results[i].filename,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        date: results[i].date,
                        starttime: results[i].starttime,
                        endtime: results[i].endtime,
                        endLat: results[i].endLat,
                        endLong: results[i].endLong,
                        endDate: results[i].endDate
                    })
                }
            }
        }
        // Define array data
        var data = [];
        // For every cycle in tmp, calculate the waiting time by creating the dates with endtimes and starttimes and subtract them. Push the 
        // waiting time with the GPS coordinates (without altitude) as a dictionary to the array data
        for(var i = 0; i < (tmp.length - 1); i++) {
	    console.log("File: " + tmp[i].filename);
            var tmp1 = (tmp[i].endtime).split(":");
            var date1 = (tmp[i].endDate).split("-");
            var tmp2 = (tmp[i+1].starttime).split(":");
            var date2 = (tmp[i+1].date).split("-");
            time1 = new Date(date1[2], date1[0], date1[1], tmp1[0], tmp1[1], tmp1[2]);
            time2 = new Date(date2[2], date2[0], date2[1], tmp2[0], tmp2[1], tmp2[2]);
            // Subtraction of two dates delivers the difference in seconds
            dateTotal = time2 - time1;
            data.push({
                waitingTime: dateTotal, 
                gpsLat: tmp[i].endLat,
                gpsLong: tmp[i].endLong
            });
        }
        // Send the http response as the array data
        res.send(data);
    });
});



// GET dashboard page
router.get('/dashboard', authenticationMiddleware(), function (req, res, next) {
    // Render the dashboard page; render() compiles template, inserts locals there and create html out of those two things --> hbs file
    res.render('dashboard', { title: 'Dashboard', dashboard: true});
});



// GET all trips of the given vin and date
router.get('/getTrips/:date/:sim_real/:selector/:value', authenticationMiddleware(), function (req, res) {
    // Get the specified date and VIN 
    var date = req.params.date;
    var selector = req.params.selector;
    var value = req.params.value;
    // If the date is "undefined", get the date of today adn create date string for variable date
    if(req.params.date === "undefined") {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth() + 1; // January is 0!
        var yyyy = today.getFullYear();
        if(dd < 10) {
            dd = '0'+ dd
        }
        if(mm < 10) {
            mm = '0'+ mm
        }
        date = mm + '-' + dd + '-' + yyyy;
    }
    // Establish connection to database
    var db = require('../db.js');

    // Determine whether to get data from table data (real cycles) or table simulations (simulated cycles)
    var sim_or_real = req.params.sim_real;

    // Get some driving cycle data from the cycles of the specified date
    db.query('SELECT id, filename, starttime, totalKM, vin, energyConsumption FROM ' + sim_or_real + ' WHERE date=?', [date], function (err, results, fields) {
        // If error occures, throw it
        if (err) throw err;
        // Define array data
        var data = [];
        // For every driving cycle in the result, if the selectors value matches, append a dictionary of the cycle data to the array tmp
        for (var i = 0; i < results.length; i++) {
            if (value == "none") {
                data.push({
                    filename: results[i].filename,
                    starttime: results[i].starttime,
                    totalKM: results[i].totalKM,
                    energyConsumption: results[i].energyConsumption,
                    id: results[i].id
                })
            }
            else if (selector == "vin") {
                // The vin is saved as a hash in the database, so it has to be compared with bcrypt
                if (bcrypt.compareSync(value, results[i].vin)) {
                    data.push({
                        filename: results[i].filename,
                        starttime: results[i].starttime,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "km_min") {
                var km_min = parseFloat(value);
                if (km_min != NaN && km_min <= results[i].totalKM) {
                    data.push({
                        filename: results[i].filename,
                        starttime: results[i].starttime,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "consumption_min") {
                var consumption_min = parseFloat(value);
                if (consumption_min != NaN && consumption_min <= results[i].energyConsumption) {
                    data.push({
                        filename: results[i].filename,
                        starttime: results[i].starttime,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
            else if (selector == "id") {
                var id = parseInt(value);
                if (id != NaN && id == results[i].id) {
                    data.push({
                        filename: results[i].filename,
                        starttime: results[i].starttime,
                        totalKM: results[i].totalKM,
                        energyConsumption: results[i].energyConsumption,
                        id: results[i].id
                    })
                }
            }
        }
        // Send http response as array data
        res.send(data);
    });
});



// GET login page
router.get('/login', function (req, res, next) {
    // If the request is authenticated, get to the dashboard, otherwise get to the login page
    if(req.isAuthenticated()) {
        res.redirect('/dashboard')
    }
    res.render('login', { title: 'Login', login: true });
});



// Handle POST of login page
// Use passport.authenticate with custom callbacks to authenticate the user
// See the official passport documentation: http://www.passportjs.org/docs/authenticate/ 
router.post('/login', function (req, res, next) {
    // Call passport.authenticate() for local
    passport.authenticate('local', function (err, user, info) {
        // If error occures, stop execution and execute next function, defined in the parameters of router.post()
        if (err) { return next(err); }
        // If authentication failed, log the info message with additional detail, set the request parameters to the info ones 
        // (what the user inserted) and execute next function
        if (!user) { 
            // See the possible messages in ../app.js
            console.log(info.message);
            req.data = info.message;
            req.id = info.user_id;
            req.email = info.email;
            return next(); 
        }
        // Create session for the user. If error occures, stop execution and execute next function, otherwise get to dashboard
        req.logIn(user, function(err) {
            if (err) { return next(err); }
            return res.redirect('/dashboard');
        });
    })(req, res, next);
}, function (req, res, next) { // More than one callback function, only called if login failed or mail needs to be confirmed
    // Define error as array of a dictionary with msg as key and the request data as value (message from info from passport.authenticate())
    var error = [{
        msg: req.data
    }]
    // If the request data says that the email needs to be confirmed, send a mail with the confirmation link
    if (req.data === 'Confirm your email!') {
        mailer(req.id, req.email, "confirmation");
    }
    // Log the login errors as a string of the array error
    console.log(`Login errors: ${JSON.stringify(error)}`);
    // Render the login page with login failed as title
    res.render('login', { 
        title: 'Login failed',
        errors: error,
        login: true
    });
});



// GET page to request a password reset
router.get('/resetpw', function (req, res, next) {
    // Render the page for password reset (hbs file)
    res.render('resetpw', { title: 'Reset your password' });
});



// Handle POST of reset password request page
router.post('/resetpw', function (req, res, next) {
    // Establish connection with database
    var db = require('../db.js');
    // Get the id and the email of the in the request body specified username
    db.query('SELECT id, email FROM users WHERE username = ?', [req.body.username], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
        // If erro occures, define array error as a dictionary with msg as key and the string as value that username doesn't exist
        // Log the error as JSON string and render the reset password page with the title that the resetting failed and the error message
        // that the username doesn't exist
        if (error) {
            var error = [{
                msg: 'Username doesn\'t exists.'
            }]
            console.log(`errors: ${JSON.stringify(error)}`);
            res.render('resetpw', { 
                title: 'Resetting password failed!',
                errors: error
            });
        } else if (results[0].email === req.body.email) {
            // If Email from database matches with users email (from request body), send an email with the purpose to reset password and 
            // get to login page
            mailer(results[0].id, req.body.email, "resetpw")
            res.redirect('/login');
        } else {
            // Else define array error with the msg that the email is wrong, log the username from the database and the error as JSON string
            // and render the reset password page with the title that resetting failed and the error
            var error = [{
                msg: 'Email is wrong.'
            }]
            console.log(results[0].username);
            console.log(`errors: ${JSON.stringify(error)}`);
            res.render('resetpw', { 
                title: 'Resetting password failed!',
                errors: error
            });
        }
    });
});



// GET page to reset the password
router.get('/resetpw:token', function (req, res, next) {
    // Render the reset password confirmed page
    res.render('resetpw_confirmed', { 
        title: 'Reset your password',
        token: req.params.token
    });
});



// Handle POST of reset password page
router.post('/resetpw_confirmed:token', function (req, res, next) {
    // Validate whether the password from the request matches the restrictions
    req.checkBody('password', 'Password must be between 8-100 characters long.').len(8, 100);
    req.checkBody("password", "Password must include one lowercase character, one uppercase character, a number, and a special character.").matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.* )(?=.*[^a-zA-Z0-9]).{8,}$/, "i");
    req.checkBody('passwordMatch', 'Password must be between 8-100 characters long.').len(8, 100);
    req.checkBody('passwordMatch', 'Passwords do not match, please try again.').equals(req.body.password);

    // Define constant error as the validation errors from the request
    const errors = req.validationErrors();

    // If errors occur, log them and render the reset password page with the token (previous GET route), the title resetting failed and the errors
    if(errors) {
        console.log(`errors: ${JSON.stringify(errors)}`);
        res.render(`resetpw${req.params.token}`, { 
            title: 'Resetting failed',
            errors: errors
        });
    } else {
        // If no errors occur, verify the token with the mail secret from the env and log the output (payload with user)
        var id = jwt.verify(req.params.token, process.env.MAIL_SECRET);
        console.log(id);

        // Define constant password as the new password from the request
        const password = req.body.password;

        // Establish connection to database
        var db = require('../db.js');
        // Hash password and insert it to the right user in the database
        bcrypt.hash(password, saltRounds, function(err, hash) {
            db.query('UPDATE users SET confirmed = 1, password = ? WHERE id = ?', [hash, id.user], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
                // If errors occur, log them and render the reset password page (previous GEt route) with the token and resetting failed as title
                if (error) {
                    console.log(`errors: ${JSON.stringify(error)}`);
                    res.render(`resetpw${req.params.token}`, { 
                    title: 'Resetting failed',
                    errors: errors
                    });
                // If no errors occur, get to login page
                } else {
                    res.redirect('/login');
                }
            });
        });
    }
});



// Destroy session via logout button
router.get('/logout', function (req, res, next) {
    // Remove req.user property and clears login session
    req.logout()
    // Destroy session and clear cookies. Get to the home page
    req.session.destroy(() => {
        res.clearCookie('connect.sid')
        res.redirect('/')
    })
});



// GET register page
router.get('/register', function (req, res, next) {
    // If the request is authenticated, get to dashboard page, otherwise render the register page
    if(req.isAuthenticated()) {
        res.redirect('/dashboard')
    }
    res.render('register', { title: 'Registration', register: true });
});



// Handle POST of register page
router.post('/register', function(req, res, next) {
    // Check the registration input with express-validator
    req.checkBody('username', 'Username field cannot be empty.').notEmpty();
    req.checkBody('username', 'Username must be between 4-15 characters long.').len(4, 15);
    req.checkBody('email', 'The email you entered is invalid, please try again.').isEmail();
    req.checkBody('email', 'Email address must be between 4-100 characters long, please try again.').len(4, 100);
    req.checkBody('password', 'Password must be between 8-100 characters long.').len(8, 100);
    req.checkBody("password", "Password must include one lowercase character, one uppercase character, a number, and a special character.").matches(/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.* )(?=.*[^a-zA-Z0-9]).{8,}$/, "i");
    req.checkBody('passwordMatch', 'Password must be between 8-100 characters long.').len(8, 100);
    req.checkBody('passwordMatch', 'Passwords do not match, please try again.').equals(req.body.password);

    // Define the constant errors as the validation errors
    const errors = req.validationErrors();

    // If errors occured, log them and render the register page with registering failed as title and the errors
    if(errors) {
        console.log(`errors: ${JSON.stringify(errors)}`);
        res.render('register', { 
            title: 'Registration failed',
            errors: errors
        });
    } else {
        // If no errors occured, define the user data (from the request body) as constants
        const username = req.body.username;
        const email = req.body.email;
        const password = req.body.password;

        // Establish connection to database
        var db = require('../db.js');

        // Hash the password and insert a new user with the data from the request into the database
        bcrypt.hash(password, saltRounds, function(err, hash) {
            db.query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email, hash], function(error, results, fields) {    // use ? so that you can't hack the server with unwanted inputs
                // If an error occures, log it and render the register page with registration failed as title and the username already exists as error
                if (error) {
                    console.log(`errors: ${JSON.stringify(error)}`);
                    var error = [{
                        msg: 'Username already exists.'
                    }]
                    console.log(`errors: ${JSON.stringify(error)}`);
                    res.render('register', { 
                        title: 'Registration failed',
                        errors: error
                    });
                } else {
                    // If no error occures, get the last created user_id (automatically created by MySQL)
                    db.query('SELECT LAST_INSERT_ID() as user_id', function (error, results, fields) {
                        // If error occurs, throw it
                        if (error) throw error;

                        // Define constant user_id as the id from the result
                        const user_id = results[0].user_id;
                        // Log the id
                        console.log(user_id);

                        // login (passport) uses serialization-function
                        /*req.login(user_id, function(err) {
                            res.redirect('/');
                        });*/

                        // Log mail password from env
                        console.log(process.env.MAIL_PASSWORD)
                        // Send mail to the registered user to confirm email
                        mailer(user_id, req.body.email, "confirmation")
                        // Get to the login page
                        res.redirect('/login');
                    });
                }
            });
        });
    } 
});



// Save the user_id as a session information
passport.serializeUser(function(user_id, done) {
    done(null, user_id);
});



// Read all session information
passport.deserializeUser(function(user_id, done) {
    done(null, user_id);
});



// Check whether the user is authenticated, if not, redirect him to the login page
function authenticationMiddleware() {
    return (req, res, next) => {
        console.log(`req.session.passport.user: ${JSON.stringify(req.session.passport)}`);
        if (req.isAuthenticated()) return next();
        res.redirect('/login');
    }
}


// Export the object router
module.exports = router;
