/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Handles the representation of tge routes in the different maps.

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

Date: 03.03.2021

Version 1.1

Description:
    - Control the coloration of the routes in map three
    - Dependent from no parameter (--> normal color) or the vehicle speed

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 21.03.2021

Version 1.2

Description:
    - Add the ID to the pop ups of the first and third map
    - Add the energy data to these pop ups for simulated drives
*/


// First map (all routes)
var map0 = L.map( 'map0', {
    center: [20.0, 5.0],
    minZoom: 2,
    zoom: 2
});

// Function to represent all routes that shall be displayed in the first map
var printAllMarkers = async function() {
    map0.remove()
    // Create map instance
    map0 = L.map( 'map0', {
        center: [20.0, 5.0],
        minZoom: 2,
        zoom: 2
    });

    // Point to print the routes
    var customIcon = L.icon({
        iconUrl: '../img/dot.png',

        iconSize:     [4, 4], // size of the icon
        shadowSize:   [0, 0], // size of the shadow
        iconAnchor:   [2, 2], // point of the icon which will correspond to marker's location
        shadowAnchor: [4, 62],  // the same for the shadow
        popupAnchor:  [2, 2] // point from which the popup should open relative to the iconAnchor
    });

    // Array to hold the GPS data
    var allMarkers = [];
    // Title and stuff for the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map0);

    // Get the parameters to choose the routes from that shall be displayed
    var selector = document.getElementById('selector').value;
    var vin = document.getElementById('VIN').value;
    var sim_real = document.getElementById('sim_real_selector').value;
    vin = (vin === "") ? "none" : vin; 
    console.log(vin)

    // Get the GPS data for these routes
    let response = await fetch("/getAllGPS/" + sim_real + "/" + selector + "/" + vin, {
        credentials: 'same-origin'
    });
    let markers = await response.json();

    var allMarkers = []

    // averageLength needed for calCar.js
    averageTripLength = markers[markers.length-1].averageTripLength;
    longestTrip = markers[markers.length-1].longestTrip;
    vConsumption = markers[markers.length-1].vConsumption;
    numberOfTrips = 0;

    // Print each route
    for(var i = 0; i < (markers.length-1); i++) {
        // Get the id for the drive cycle or the simulated drive
        if (sim_real == "data") {
            let response3 = await fetch("/getID/" + sim_real + "/" + markers[i].filename, {
                credentials: 'same-origin'
            });
            var id = await response3.json();
        }
        else if (sim_real == "simulation") {
            let response3 = await fetch("/getID/" + sim_real + "/" + markers[i].filename_energy, {
                credentials: 'same-origin'
            });
            var id = await response3.json();
        }

        // Variable with no text in it yet
        var pop_text = "";

        // Get the energy data if the route is simulated and append the energy data to the pop_text
        if (sim_real == "simulation") {
            let response4 = await fetch("/getEnergyData/" + markers[i].filename_energy, {
                credentials: 'same-origin'
            });
            let energyData = await response4.json();
            temp_energy = energyData.energy_heat.pop();
            drive_energy = energyData.energy_drive.pop();
            pop_text = pop_text + "<p>Temperatur energy: " + temp_energy + "</p><p>Driving energy: " + drive_energy + "</p><p>Total energy: " + (temp_energy + drive_energy) + "</p>";
        }
        
	    // Print each GPS point in the map
        for (let g = 0; g < markers[i].GPS_Long.length; g++) {
            if(!(markers[i].GPS_Long[g] === null || markers[i].GPS_Lat[g] === null)) {
                //console.log("test")
                allMarkers.push({ 
                    "lat": markers[i].GPS_Lat[g],
                    "lng": markers[i].GPS_Long[g]
                });
                L.marker([markers[i].GPS_Lat[g], markers[i].GPS_Long[g]], { icon: customIcon })
                    // Bind pop up to the route
                    .bindPopup('<p>Route-ID:' + id[0] + '</p>' + pop_text)
                    .addTo( map0 );
            }
        }
        // Increment the number of printed routes
        numberOfTrips++;
    }
    // Match the map
    if(allMarkers.length != 0) {
        var bounds = L.latLngBounds(allMarkers);
        map0.fitBounds(bounds);
    }
}
// When Webapplication started, create empty maps
printAllMarkers();


//Waiting time map

// Function to parse the time from a time stamp in milliseconds
function parseTime(milliseconds){
    //Get hours from milliseconds
    var hours = milliseconds / (3600000);
    var absoluteHours = Math.floor(hours);
    var h = absoluteHours > 9 ? absoluteHours : '0' + absoluteHours;

    //Get remainder from hours and convert to minutes
    var minutes = (hours - absoluteHours) * 60;
    var absoluteMinutes = Math.floor(minutes);
    var m = absoluteMinutes > 9 ? absoluteMinutes : '0' +  absoluteMinutes;

    //Get remainder from minutes and convert to seconds
    var seconds = (minutes - absoluteMinutes) * 60;
    var absoluteSeconds = Math.floor(seconds);
    var s = absoluteSeconds > 9 ? absoluteSeconds : '0' + absoluteSeconds;


    return h + 'h' + m;
}

// Second map with the waiting points
var map2 = L.map( 'map2', {
    center: [20.0, 5.0],
    minZoom: 2,
    zoom: 2
});

// Function to display the waiting points in the second map
var printWaitingTime = async function() {
    map2.remove()

    // Create map instance
    map2 = L.map( 'map2', {
        center: [20.0, 5.0],
        minZoom: 2,
        zoom: 2
    });

    // Define the Icon for the waiting time
    var LeafIcon = L.Icon.extend({
        options: {
            shadowUrl: 'leaf-shadow.png',
            iconSize:     [182/5, 219/5],
            shadowSize:   [0, 0],
            iconAnchor:   [182/10, 219/5],
            shadowAnchor: [0, 0],
            popupAnchor:  [0, -219/10]
        }
    });
     // Get the icon pictures
    var redIcon = new LeafIcon({iconUrl: '../img/red.png'}),
        orangeIcon = new LeafIcon({iconUrl: '../img/orange.png'}),
        yellowIcon = new LeafIcon({iconUrl: '../img/yellow.png'});
        greenIcon = new LeafIcon({iconUrl: '../img/green.png'});

    // Empty array for the waiting points
    var allMarkers = [];
    // Map title
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map2);

    // Get the parameters to choose the right routes
    var selector = document.getElementById('selector').value;
    var vin = document.getElementById('VIN').value;
    var sim_real = document.getElementById('sim_real_selector').value;
    vin = (vin === "") ? "none" : vin; 
    console.log(vin)

    // Get the waiting times for the routes
    let response = await fetch("/getWaitingTime/" + sim_real + "/" + selector + "/" + vin, {
        credentials: 'same-origin'
    });
    let markers = await response.json();

    var allMarkers = []

    // Get value of the radiobuttons with the charging variations
    var radioButtons = document.getElementsByName('charging_variations');
    var radioValue = 'none';
    for (var i = 0; i < radioButtons.length; i++) {
        if (radioButtons[i].checked == true) {
            radioValue = radioButtons[i].value;
        }
    }

    // Get value of slider with the power to fulfill minimally
    var sliderValue = document.getElementById("power_range").value;

    // Dictionary containing the types of charging stations as keys and their power output as values
    var charging_dict = {
        "type1":5.8,
        "type2":22,
        "ccscombo2":50,
        "chademo":36,
        "teslasupercharger":135
    }

    // Decide which markers to show (based on selection of radiobuttons and checkbox underneath the map)
    if (radioValue == "none") {
        // Print every waiting point with an bound pop up containing the waiting time
        for (var i = 0; i < markers.length; i++) {
            if (markers[i].waitingTime < 1800000) {
                customIcon = redIcon;
            } else if (markers[i].waitingTime < 2 * 1800000 && markers[i].waitingTime > 1800000) {
                customIcon = orangeIcon;
            } else if (markers[i].waitingTime < 8 * 1800000 && markers[i].waitingTime > 2 * 1800000) {
                customIcon = yellowIcon;
            } else {
                customIcon = greenIcon;
            }
            allMarkers.push({
                "lat": markers[i].gpsLat,
                "lng": markers[i].gpsLong
            });
            L.marker([markers[i].gpsLat, markers[i].gpsLong], { icon: customIcon, opacity: 0.7 })
                .bindPopup('<p>Waiting-Time: ' + parseTime(markers[i].waitingTime) + '</p>')
                .addTo(map2);

        }
        if (markers.length > 0) {
            // Create legend for route visualization
            var legend = L.control({ position: 'bottomright' });
            // Adding the labels
            legend.onAdd = function (map2) {
                // Create division for labels
                var div = L.DomUtil.create('div', 'route-coor-legend');
                // Arrays to organize the values
                labels = ['<strong>Color legend</strong>'];
                categories = ['< 30min', '30min - 1h', '1h - 4h', '> 4h'];
                colors = ['red', 'orange', 'yellow', 'green'];
                // Add the labels to the division
                for (var j = 0; j < categories.length; j++) {
                    labels.push('<span style="background-color:' + colors[j] + '; border-radius: 50%; width: 10px; height: 10px; display: inline-block"></span> ' + (categories[j] ? categories[j] : '+'));
                }
                // Linebreaks between the labels
                div.innerHTML = labels.join('<br>');
                return div
            };
            // Add legend to the map
            legend.addTo(map2);
        }
        
        // Match map
        if (allMarkers.length != 0) {
            var bounds = L.latLngBounds(allMarkers);
            map2.fitBounds(bounds);
        }
    }
    else{
        for (var i = 0; i < markers.length; i++) {
            // Show only locations matching the given criterias
            if (charging_dict[radioValue] * (markers[i].waitingTime / 3600000) >= sliderValue) {
                customIcon = greenIcon;
                allMarkers.push({
                    "lat": markers[i].gpsLat,
                    "lng": markers[i].gpsLong
                });

                L.marker([markers[i].gpsLat, markers[i].gpsLong], { icon: customIcon, opacity: 0.7 })
                    // Bind pop up with the waiting time and the charged power
                    .bindPopup('<p>Waiting-Time: ' + parseTime(markers[i].waitingTime) + '</p>' + '<p>Charge: ' + charging_dict[radioValue] * (markers[i].waitingTime / 3600000) + 'Wh</p>')
                    .addTo(map2);
            }

        }
        if (allMarkers.length != 0) {
            var bounds = L.latLngBounds(allMarkers);
            map2.fitBounds(bounds);
        }
    }

    
}
// Create empty map when webapplication is started
printWaitingTime();



// Function to determine the color of the route points in map1
var determine_color = function (data, position, radioValue) {
    var point_color = 'blue';
    // Select the color visualization depending on the radio button value
    if (radioValue == 'speed')
    {
        if (data.SPEED[position] >= 0 && data.SPEED[position] <= 30) {
            point_color = 'green';
        }
        else if (data.SPEED[position] > 30 && data.SPEED[position] <= 50) {
            point_color = 'blue';
        }
        else if (data.SPEED[position] > 50 && data.SPEED[position] <= 100) {
            point_color = 'rgb(255, 0, 255)';
        }
        else if (data.SPEED[position] > 100) {
            point_color = 'red';
        }
    }

    return point_color;
}

// Trip information map
var map = L.map( 'map1', {
    center: [20.0, 5.0],
    minZoom: 2,
    zoom: 2
});

// Function to display the routes in the third map
var printMarkers = async function(filename, nof, filename_energy) {
    map.remove();

    // Create map instance
    map = L.map( 'map1', {
        center: [20.0, 5.0],
        minZoom: 2,
        zoom: 2
    });

    // Map title
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    
    // Get value of the checked radio button
    var radioButtons = document.getElementsByName('route_visualization');
    var radioValue = 'none';
    for (var i = 0; i < radioButtons.length; i++) {
        if (radioButtons[i].checked == true) {
            radioValue = radioButtons[i].value;
        }
    }

    // If there are routes to print:
    if(nof === 0) {} else {
        var allMarkers = [];
        for(var g = 0; g < nof; g++) {
            /*let response = await fetch("maps/markers.json");
            let markers = await response.json();*/
            console.log(g)
            let response = await fetch("/getGPS/" + filename[g], {
                credentials: 'same-origin'
            });
            let markers = await response.json();
	    var gpsData = markers;
            //console.log("Test " + markers.GPS_Lat[0]);

            // Get all obd data for the drive cycle
            let response2 = await fetch("/getOBD/" + filename[g], {
                credentials: 'same-origin'
            });
            let allData = await response2.json();

            // Get the id for the drive cycle or the simulated drive
            if (filename_energy.length >= g + 1) {
                console.log("Get ID for cycle: " + filename[g])
                let response3 = await fetch("/getID/" + "simulation/" + filename_energy[g], {
                    credentials: 'same-origin'
                });
                var id = await response3.json();
            }
            else {
                console.log("Get ID for cycle: " + filename[g])
                let response3 = await fetch("/getID/" + "data/" + filename[g], {
                    credentials: 'same-origin'
                });
                var id = await response3.json();
            }
            console.log("ID:")
            console.log(id)

            // Empty pop up text
            pop_text = "";

            // Get the energy data if the route is simulated and append the energy data to the pop up
            if (filename_energy.length >= g + 1) {
                let response4 = await fetch("/getEnergyData/" + filename_energy[g], {
                    credentials: 'same-origin'
                });
                let energyData = await response4.json();
                temp_energy = energyData.energy_heat.pop();
                drive_energy = energyData.energy_drive.pop();
                pop_text = pop_text + "<p>Temperatur energy: " + temp_energy + "</p><p>Driving energy: " + drive_energy + "</p><p>Total energy: " + (temp_energy + drive_energy) + "</p>";
            }

            // Remove empty GPS points
            markers = await removeNull(markers);
            allMarkers.push(markers)
            

	        // Counter to handle empty GPS values for colored visualization
            var counter_gps = 0;
            // Print the GPS points to the map
            for ( var i=0; i < markers.length; i++ ) 
            {
                // Add GPS point to the map for the pop up
                var tmp = 0;
                if(i === 0 || i === (markers.length - 1)) {
                    tmp = 1;
                }
                L.marker( [markers[i].lat, markers[i].lng], {opacity: tmp})
                    .bindPopup('<p>Route-ID:' + id[0] + '</p>' + pop_text)
                    .addTo( map );

                // Next GPS point
                if ((i + 1) < markers.length) {
                    var latlngs = Array();
                    latlngs.push({
                        "lat": markers[i].lat,
                        "lng": markers[i].lng
                    });
                    latlngs.push({
                        "lat": markers[i + 1].lat,
                        "lng": markers[i + 1].lng
                    });
                    // When GPS point is empty, jump over the matching OBD data for this point
		    while(gpsData.GPS_Lat[counter_gps] === null || gpsData.GPS_Long[counter_gps] === null){
			counter_gps = counter_gps + 1;
                    }
                    // Determine the color for the route point and add the route to the map
                    var point_color = await determine_color(allData, counter_gps, radioValue);
                    var polyline = L.polyline(latlngs, { color: point_color }).addTo(map);
                    // Increment the position in the OBD data array
		    counter_gps = counter_gps + 1;
                }
                // If colorization is chosen, add a legend to the map
                else if(radioValue != 'none' && g == 0){
                    // Create legend for route visualization
                    var legend = L.control({ position: 'bottomright' });
                    // Adding the labels
                    legend.onAdd = function (map) {
                        // Create division for labels
                        var div = L.DomUtil.create('div', 'route-coor-legend');
                        // Arrays to organize the values
                        labels = ['<strong>Route visualization</strong>'];
                        categories = [];
                        colors = []
                        if (radioValue == 'speed') {
                            categories.push(...['0-30 km/h', '30-50 km/h', '50-100 km/h', '>100 km/h']);
                            colors.push(...['#00ff00', '#0000ff', '#ff00ff', '#ff0000']);
                        }
                        // Add the labels to the division
                        for (var j = 0; j < categories.length; j++) {
                            div.innerHTML += labels.push('<span style="background-color:' + colors[j] + '; border-radius: 50%; width: 10px; height: 10px; display: inline-block"></span> ' + (categories[j] ? categories[j] : '+'));
                        }
                        // Linebreaks between the labels
                        div.innerHTML = labels.join('<br>');
                        return div
                    };
                    // Add legend to the map
                    legend.addTo(map);
                }
            }
        }
        // Match map
        var bounds = L.latLngBounds(allMarkers);
        map.fitBounds(bounds);
    }
}

// Function to remove the empty GPS points from an array
var removeNull = function (markers) {
    // Array for the GPS points
    let markerList = new Array();
    // Go through each GPS point
    for ( var i=0; i < markers.GPS_Lat.length; ++i ) 
    {
        // Check if the GPS coordinates are empty, if that's the case, jump over the point
        if(markers.GPS_Long[i] === null || markers.GPS_Lat[i] === null) {
            continue;
        }
        // Valid GPS points are put into the array
        markerList.push({ 
            "lat": markers.GPS_Lat[i],
            "lng": markers.GPS_Long[i]
        });
    }
    return markerList;
}
