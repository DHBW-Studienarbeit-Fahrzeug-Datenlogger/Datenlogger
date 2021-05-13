/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Handles the calculation of the recommended car for the user when the button is clicked.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring

*/


var averageTripLength = 0;
var numberOfTrips = 0;
var longestTrip = 0;
var vConsumption = 0;

// Function to calculate the recommended car
var calculateCar = async function(){
    // Declare neccessary variables
    var type;
    var energyConsumptionFactor;
    var bestCar;
    console.log("averageTripLength: "+ averageTripLength)
    console.log((document.getElementById('input01')).value)
    // Switch case what type of car shall be calculated
    switch ((document.getElementById('input01')).value) {
        case "1":
            type = "micro"
            break;
        case "2":
            type = "mini"
            break;
        case "3":
            type = "medium"
            break;
        case "4":
            type = "van"
            break;
        case "5":
            type = "luxury"
            break;
        default:
            break;
    }
    // Switch case with which factor the calculation shall be done --> driving style (normal, eco, athletic)
    switch ((document.getElementById('input02')).value) {
        case "1":
            energyConsumptionFactor = 0.9
            break;
        case "2":
            energyConsumptionFactor = 1.0
            break;
        case "3":
            energyConsumptionFactor = 1.1
            break;
        default:
            break;
    }

    console.log(type);
    // Get the cars of the chosen type
    let response = await fetch("/getCars/" + type, {
        credentials: 'same-origin'
    });

    let cars = await response.json();

    // Declare variables
    var range = [];
    var count = 0;
    var deltaToAverage = averageTripLength;

    // Compare the range of each car with the average trip length from the routes to determine the recommended car
    // The car is the one that has a range bigger than the average trip length but also the range with the smallest difference
    for(let i = 0; i < cars.length; i++) {
        range[i] = (cars[i].capacity / (cars[i].consumption * energyConsumptionFactor)) * 100;
        if(((range[i] - averageTripLength) < deltaToAverage) && (range[i] > averageTripLength)) {
            deltaToAverage = range[i] - averageTripLength;
            bestCar = i;
        } else {
            count++;
        }
        console.log("Range: " + range[i])
    }
    // If no car matches the average trip length, choose the car with the greatest range
    if(count == cars.length) {
        bestCar = 0;
        for(let i = 0; i < cars.length; i++) {
            if(range[i] > range[bestCar]) {
                bestCar = i;
            }
        }
    }

    // Empty the division that displays the recommendation
    $("#car").empty()
    $("#range").empty()
    $("#eConsumption").empty()
    $("#averageTripLength").empty()
    $("#longestTrip").empty()
    $("#chargeStops").empty()
    $("#vConsumption").empty()
    $("#table").css("display", "")
    // Display the recommended car with its parameters
    if(averageTripLength != 0) {
        var innerHTML = `${cars[bestCar].name}`
        $("#car").append(innerHTML)
        innerHTML = `${Math.round(range[bestCar])}km`
        $("#range").append(innerHTML)
        innerHTML = `${cars[bestCar].consumption.toFixed(2)}kWh/100km`
        $("#eConsumption").append(innerHTML)
        innerHTML = `${Math.round(averageTripLength)}km`
        $("#averageTripLength").append(innerHTML)
        innerHTML = `${Math.round(longestTrip)}km`
        $("#longestTrip").append(innerHTML)
        innerHTML = `${Math.floor(longestTrip / range[bestCar])}`
        $("#chargeStops").append(innerHTML)
        innerHTML = `${vConsumption.toFixed(2)}kWh/100km`
        $("#vConsumption").append(innerHTML)
    // If there is no route, give a message
    } else {
        var innerHTML = `noch keine Fahrt`
        $("#car").append(innerHTML)
        $("#range").append(innerHTML)
        $("#eConsumption").append(innerHTML)
        $("#averageTripLength").append(innerHTML)
        $("#longestTrip").append(innerHTML)
        $("#chargeStops").append(innerHTML)
        $("#vConsumption").append(innerHTML)
    }
    $(function(){
        $('[data-toggle="tooltip"]').tooltip();
    })
}
