/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Creates a router object and the route for the request of users.
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




// Requirememnts
var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('respond with a resource');
});

module.exports = router;
