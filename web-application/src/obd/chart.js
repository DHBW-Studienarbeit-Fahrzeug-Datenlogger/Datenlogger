var getData = async function(filename, name) {
    // sends a request with credentials included
    let response = await fetch("/getOBD/" + filename, {
        credentials: 'same-origin'
    });
    let allData = await response.json();



    // Send a request to get the additional data
    var filenameAdd = filename.slice(0, -5) + "_height_profile.json"
    console.log("Filename for height profile: " + filenameAdd)

    let response = await fetch("/getAddData/" + filenameAdd, {
        credentials: 'same-origin'
    });
    let addData = await response.json();


    var time = allData.TIME;
    var speed = allData.SPEED;
    var rpm = allData.RPM;

    // USE THE RIGHT VARIABLE NAMES
    var timeAdd = allData.TIME;
    var height = addData.gps_alt;
    /*
    var engine_load = [];
    var maf = [];
    var temperature = [];
    var pedal = [];
    var afr = [];
    var fuel_level = [];*/
    var data = [time, speed, rpm/*, engine_load, maf, temperature, pedal, afr, fuel_level*/];
    var dataAdditional = [time_add, height];

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
            //domain: [0.25, 1],
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
    // IF NOT WORKING, CREATE SUBPLOTS
    Plotly.newPlot(name, data, layout, config);
    Plotly.newPlot(name + " height profile", [heightTrace], layoutAdditional, config)
}