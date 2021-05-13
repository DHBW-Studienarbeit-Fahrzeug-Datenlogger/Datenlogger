/*
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0

Description:
    Contains the function to create the diagramm for the vehicle data. The 
    diagramm is placed under the third map.

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
    - Another diagramm representing the height profile is appended
*/

var getData = async function (filename, name) {
    // sends a request with credentials included
    let response = await fetch("/getOBD/" + filename, {
        credentials: 'same-origin'
    });
    let allData = await response.json();



    // Send a request to get the additional data
    var filenameAdd = filename.slice(0, -5) + "_height_profile.json"
    console.log("Filename for height profile: " + filenameAdd)

    let response2 = await fetch("/getAddData/" + filenameAdd, {
        credentials: 'same-origin'
    });
    let addData = await response2.json();


    var time = allData.TIME;
    var speed = allData.SPEED;
    var rpm = allData.RPM;

    // USE THE RIGHT VARIABLE NAMES
    var timeAdd = allData.TIME;
    var height = addData.gps_alt;

    var data = [time, speed, rpm/*, engine_load, maf, temperature, pedal, afr, fuel_level*/];
    var dataAdditional = [timeAdd, height];

    // Sources: https://plot.ly/javascript/configuration-options
    //          https://community.plot.ly/t/remove-options-from-the-hover-toolbar/130/11 
    var speedTrace = {
        type: "scatter",
        mode: "lines",
        name: 'Speed',
        x: data[0],
        y: data[1],
        yaxis: 'y2',
        line: {color: '#7F7F7F'}
    }

    var rpmTrace = {
        type: "scatter",
        mode: "lines",
        name: 'RPM',
        x: data[0],
        y: data[2],
        line: {color: '#1f77b4'}
    }

    var heightTrace = {
        type: "scatter",
        mode: "lines",
        name: 'Height profile',
        x: dataAdditional[0],
        y: dataAdditional[1],
        line: { color: '#7F7F7F' }
    }
    
    var data = [speedTrace, rpmTrace];
        
    var layout = {
        title: name,
        xaxis: 
        {
            domain: [0.25, 1],
            showgrid: false
        },
        yaxis: 
        {
            title: 'RPM',
            titlefont: {color: '#1f77b4'},
            tickfont: {color: '#1f77b4'},
            showgrid: false
        },
        yaxis2: 
        {
            title: 'Speed',
            titlefont: {color: '#7F7F7F'},
            tickfont: {color: '#7F7F7F'},
            anchor: 'free',
            overlaying: 'y',
            side: 'left',
            position: 0.15,
            showgrid: false
        }
    };

    var layoutAdditional = {
        title: name + " height profile",
        xaxis:
        {
            showgrid: false
        },
        yaxis:
        {
            title: 'Height profile',
            titlefont: { color: '#1f77b4' },
            tickfont: { color: '#1f77b4' },
            showgrid: false
        }
    };
    config = {
        'modeBarButtonsToRemove': ['sendDataToCloud', 'hoverClosestCartesian', 'toggleSpikelines', 'resetScale2d', 'hoverCompareCartesian'],
        'displayModeBar': true,
        'displaylogo': false,
        'responsive': true
    }

    // Create the diagramms
    Plotly.newPlot(name, data, layout, config);
    Plotly.newPlot(name + " height profile", [heightTrace], layoutAdditional, config)
}