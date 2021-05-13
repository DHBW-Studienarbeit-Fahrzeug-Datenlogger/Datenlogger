/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Contains the different functions for updating the frontend of the 
    webapplication.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 28.12.2020

Version 1.1

Description:
    - Function to control the creation of the diagramm for the height profile.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 17.04.2020

Version 1.2

Description:
    - Switch between the interfaces (by clicking in the sidebar) and show only one
    - Control the creation of the simulated route by calling the backend route and providing the parameters
      as well as creating the map views for the simulated route
*/


// Function to display the map view in the dashboard instead of the parameter interfaces
var displayData = function () {
    $("#headerVinEingabe").css("display", "")
    $("#sidebar").css("display", "")
    $("#firstPart").css("display", "")
    $("#secondPart").css("display", "")
    $("#dataPart").css("display", "")
    $("#VinEingabe").css("display", "none")
    $("#sidebar_navigation_data").css("display", "")
    $("#sidebar_simulation_real").css("display", "none")

    // Get the given VIN
    // Set the parameter in the header menu
    var vin = document.getElementById('firstVin').value;
    $("#VIN").val(vin);

    // Get the chosen selector parameter from the dropdown list
    // Set the parameter in the header menu
    var selector = document.getElementById('selector_select').value;
    var options = Array.from(document.querySelector("#selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == selector) {
            document.querySelector("#selector").selectedIndex = j;
        }
    }

    // Get the chosen selector parameter for recorded or simulated routes from the dropdown list
    // Set the parameter in the header menu
    selector = document.getElementById('sim_real_select').value;
    options = Array.from(document.querySelector("#sim_real_selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == selector) {
            document.querySelector("#sim_real_selector").selectedIndex = j;
        }
    }

    // Update the map view by activating the update button in the header menuS
    document.getElementById('VINButton').click()
}


// Function to show the simulation interface by clicking on the sidebar reference
var displaySim = function () {
    console.log("displaySim start");
    $("#VinEingabe").css("display", "none");
    $("#SimulationDivision").css("display", "");
    getOptions_sim();
    console.log("displaySim end");
}


// Function to show the standard interface for selecting a route by clicking on the sidebar reference
var displayRoutes = function () {
    $("#SimulationDivision").css("display", "none");
    $("#VinEingabe").css("display", "");
}


// Function to insert the options into the select lists for the simulation
var getOptions_sim = async function () {
    // Route to get the ids for the routes from the database
    let response = await fetch("/getIDs", {
        credentials: 'same-origin'
    });
    let id_list = await response.json();

    // Route to get the cars from the database
    let response2 = await fetch("/getAllCars", {
        credentials: 'same-origin'
    });
    let car_list = await response2.json();

    // Insert the options for the ids
    for (var i = 0; i < id_list.length; i++) {
        var innerHTML = `<option value="` + id_list[i] + `">` + id_list[i] + `</option>`
        $("#id_select").append(innerHTML)
    }

    // Insert the options for the cars
    for (var i = 0; i < car_list.length; i++) {
        var innerHTML = `<option value="` + car_list[i] + `">` + car_list[i] + `</option>`
        $("#car_select").append(innerHTML)
    }
}

// Function to create the simulation
var createSimulation = async function () {
    // Get selected car_id and route_id
    var car_name = document.getElementById('car_select').value;
    var route_id = document.getElementById('id_select').value;

    // Call python function
    let response = await fetch("/createSimulation/"+car_name+"/"+route_id, {
        credentials: 'same-origin'
    });
    let result = await response.json();
    console.log(result)

    // Show right site
    $("#headerVinEingabe").css("display", "")
    $("#sidebar").css("display", "")
    $("#firstPart").css("display", "")
    $("#secondPart").css("display", "")
    $("#dataPart").css("display", "")
    $("#SimulationDivision").css("display", "none")
    $("#sidebar_navigation_data").css("display", "")
    $("#sidebar_simulation_real").css("display", "none")

    // Put values into header selections
    var options = Array.from(document.querySelector("#sim_real_selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == 'simulation') {
            document.querySelector("#sim_real_selector").selectedIndex = j;
        }
    }

    options = Array.from(document.querySelector("#selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == 'id') {
            document.querySelector("#selector").selectedIndex = j;
        }
    }

    $("#VIN").val(result[0]);

    // Show dashboard maps
    document.getElementById('VINButton').click()
}

// Function to update the third map and also display the diagramms underneath it
var update = async function () {
    // Get the selected parameters
    var selector = document.getElementById('selector').value;
    var vin = document.getElementById('VIN').value;
    var sim_real = document.getElementById('sim_real_selector').value;
    console.log(vin)
    vin = (vin === "") ? "none" : vin; 
    // Get the selected date
    var dateArray = (document.getElementById('datepicker').value).split(".")
    var date = (dateArray[1] + '-' + dateArray[0] + '-' + dateArray[2])
    // Format the date
    if(document.getElementById('datepicker').value === "") {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth() + 1; //January is 0!
        var yyyy = today.getFullYear();
        if(dd < 10) {
            dd = '0' + dd
        }
        if(mm < 10) {
            mm = '0' + mm
        }
        date = mm + '-' + dd + '-' + yyyy;
    }
    console.log(date);

    // Get the trip data filenames via the route
    let response = await fetch("/getTrips/" + date + "/" + sim_real + "/" + selector + "/" + vin, {
        credentials: 'same-origin'
    });
    let filenames = await response.json();

    console.log(filenames)
    // Number of filenames
    var nof = 0;
    // Array of the obd filenames and if the routes are simulated the energy filenames
    var fn = [];
    var fn_energy = [];
    // Empty the allTrips division
    $("#allTrips").empty()
    // For each filename:
    filenames.forEach(file => {
        console.log(file.filename)
        // Put the filenames into the arrays and increment the number of filenames
        fn.push(file.filename)
        if (sim_real == "simulation") {
            fn_energy.push(file.filename_energy)
        }
        nof++;
        // Create a new "container" to contain the diagramms of the matching route and append it to the emptied division
        var innerHTML = `<label class='tripButton btn btn-secondary active'>
                            <input type='checkbox' class='filename' filename='${file.filename}' checked autocomplete='off'>
                                Fahrt ${nof}<br>
                                <div class='buttonText'>
                                    Startzeit: ${file.starttime} Uhr<br>
                                    gef. KM: ${file.totalKM} km<br>
                                </div>
                        </label>`
        $("#allTrips").append(innerHTML)
    });

    // Display the routes in the third map
    printMarkers(fn, nof, fn_energy);

    // Remove the diagramms
    $("#charts").empty()
    if(nof === 0) {
        $("#dataPart").css("display", "none")
    } else {
        $("#dataPart").css("display", "")
    }
    // Append the containers for the diagramms (holding the charts created)
    for(var h = 1; h <= nof; h++) {
        console.log("Filename: " + fn[h-1])
        $("#charts").append("<div id='Fahrt " + h + "'></div>")
        $("#charts").append("<div id='Fahrt " + h + " height profile" + "'></div>")
        getData(fn[h-1], "Fahrt " + h);
    }

    // Create the diagramms
    $(function() {
        console.log($(".filename").length);
        // Create a diagramm for each route that matched the parameters
        for(var i = 0; i < $(".filename").length; i++) {
            $(".filename:eq(" + i + ")").change(function(){
                var filenames = [];
                var nof = 0;
                $("#charts").empty()
                // Basically the same as above
                for(var g = 0; g < $(".filename").length; g++) {
                    if($(".filename:eq(" + g + ")").prop('checked')) {
                        filenames.push($(".filename:eq(" + g + ")").attr('filename'));
                        nof++;
                        $("#charts").append("<div id='Fahrt " + (g + 1) + "'></div>")
                        $("#charts").append("<div id='Fahrt " + (g + 1) + " height profile" + "'></div>")
                        getData($(".filename:eq(" + g + ")").attr('filename'), "Fahrt " + (g + 1));
                    }
                }
                console.log(filenames);
                // Show the routes in the map
                printMarkers(filenames, nof, fn_energy);
            });
        }
    });
}

// Create empty maps when the webapplication is started
update()
