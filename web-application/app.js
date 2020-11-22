/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Handles the basic building of the web application. Creates the instance of
    express and configurates it.
    Exports the application object.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring

*/




// Requirements (modules)
var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var expressValidator = require('express-validator');

var session = require('express-session');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var MySQLStore = require('express-mysql-session')(session);
var bcrypt = require('bcrypt');

var index = require('./routes/index');
var users = require('./routes/users');


// Create app as instance of express --> The web application object
var app = express();

// Needed to use process.env
var testFunction = require('dotenv').config();         
console.log(testFunction);

// Get the function getIP from own module getIP:
// Logs the local IP and also returns ist
var getIP = require('./getIP.js');
// Log the local IP
console.log('IP: ' + getIP());

// Get the function mailer from the own module mailer
var mailer = require('./mailer.js');
// Call function mailer with no ID, the email from the env and the mode getIP
mailer(null, process.env.MAIL_TESTMAIL, "getIP");




// Setup view engine for the web application
app.set('views', path.join(__dirname, 'views'));
// Home.hbs is the standard HTML file
app.set('view engine', 'hbs');


// uncomment after placing your favicon in /public --> Logo of the webapplication
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));

// Colors the output by response status
// Green: successful code, red: server error code, yellow: client error code, cyan: redirection code, uncolored: information code
app.use(logger('dev'));

// For handling POST and GET requests: Only parses JSON. New body object with the parsed data is populated on request object (req.body)
app.use(bodyParser.json());

// For handling POST and GET requests: Only parses urlencoded bodies --> req.body, contains key-value pairs, value can only be string or array
app.use(bodyParser.urlencoded({ extended: false }));

// Use Express Validator
app.use(expressValidator());

// User is assigned a cookie 
app.use(cookieParser());

// So that maps are available for every middleware
app.use(express.static(path.join(__dirname, 'src')));




// Set up a session and save it in MySQL when the user is authenticated
var options = {
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database : process.env.DB_NAME
};
// Saves the session information in MySQL
var sessionStore = new MySQLStore(options);


// Creates a new session for user
app.use(session({
  secret: 'aiuwhdhwoawd',   
  store: sessionStore,
  resave: 'false',          // doesn't resave the session information after every refresh
  saveUninitialized: false  // saves session information only if user is initialized
}));

// Initialize passport --> authenticates requests
app.use(passport.initialize());
// Alters req object and change 'user' value, currently session id from client cookie, into deserialized user object
app.use(passport.session());

// Every route is now able to see whether the user is authenticated 
app.use(function(req, res, next) {
  res.locals.isAuthenticated = req.isAuthenticated();   
  next();
});

// Add the self defined midleware to the express middleware stack --> defines the nadlers for the routes
app.use('/', index);
app.use('/users', users);


// Set up the strategy for passport
// Therefor the input password has to be compared to the saved password
// Creates a sign in?
passport.use(new LocalStrategy(
    function (username, password, done) {
        // Log username on console
        console.log(username);
        // Connection to the database (mysql)  
        const db = require('./db.js');
        // Send a query to the database to get the data for the current username 
        // !!!confirmed is not in database ??? !!!
        db.query('SELECT id, email, password, confirmed FROM users WHERE username = ?', [username], function (err, results, fields) {
        // Callback function, executed after passport strategy
        if (err) done(err);
        // When the username is not in database: Show message saying that
        if(results.length === 0) {    
            done(null, false, { message: 'Incorrect username!', user_id: null, email: null });
        // If username is in database
        } else {
            // Get the password (hashed) from the database and convert to a string
            const hash = results[0].password.toString();
            // WTF is confirmed supposed to be???
            console.log(results[0].confirmed);
            // Compare the entered password with the one from the datdabase
            bcrypt.compare(password, hash, function (err, response) {
                // Callback from bcrypt
                if (response === true && results[0].confirmed != null) {
                    return done(null, {user_id: results[0].id});
                } else if (response === true) {
                    return done(null, false, {message: 'Confirm your email!', user_id: results[0].id, email: results[0].email});
                } else {
                    return done(null, false, {message: 'Incorrect password!', user_id: null, email: null});
                }
            }); // End of callback from bcrypt
        }
        });  // End of callback from db.query
    } // End of callback from new LocalStrategy
));



// Catch 404 and forward to error handler
app.use(function(req, res, next) {
    var err = new Error('Not Found');
    err.status = 404;
    next(err);
});


// Error handler
app.use(function(err, req, res, next) {
    // Set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // Render the error page
    res.status(err.status || 500);
    res.render('error');
});


// Handlebars default config --> Handlebars is for templating to generate HTML
const hbs = require('hbs');
const fs = require('fs');

// Define the directory containing the partials
const partialsDir = __dirname + '/views/partials';

// Get the filenames from the parials directory
const filenames = fs.readdirSync(partialsDir);

// Execute the following function for each file in the partials directory
filenames.forEach(function (filename) {
    // Find the strings with at the beginning at least one character that is not a dot and with .hbs at the end (I think)
    const matches = /^([^.]+).hbs$/.exec(filename);
    // Does not match, "exit" the function
    if (!matches) {
        return;
    }
    // filename does match --> get the filename
    const name = matches[1];
    // Read the content of the file as template
    const template = fs.readFileSync(partialsDir + '/' + filename, 'utf8');
    // Register the partials so it can be used; partials are templates that may be called directly by other templates
    hbs.registerPartial(name, template);
});

// Registers helper accessible by any template in the environment; Helpers add custom logic to templates
// Helper: json --> transfers the context to a JSON string
hbs.registerHelper('json', function(context) {
    return JSON.stringify(context, null, 2);
});


// Export the application object
module.exports = app;
