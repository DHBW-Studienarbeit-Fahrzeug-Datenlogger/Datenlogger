/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Module for the establishing of a connection to the MySQL database from
    the env file.
    Exports the connection object.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring

*/




// Requires mysql
var mysql = require('mysql')

// Create mysql connection to the database
var connection = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database : process.env.DB_NAME
  //in case of error: add socketPath of the db
})

// Establish the connection
connection.connect();



// test the connection
connection.query('SELECT 1 + 1 AS solution', function (error, results, fields) {
  if (error) throw error;
  console.log('The solution is: ', results[0].solution);
});

module.exports = connection;