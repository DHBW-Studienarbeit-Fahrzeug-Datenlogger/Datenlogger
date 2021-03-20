var displayData = function() {
    $("#headerVinEingabe").css("display", "")
    $("#sidebar").css("display", "")
    $("#firstPart").css("display", "")
    $("#secondPart").css("display", "")
    $("#dataPart").css("display", "")
    $("#VinEingabe").css("display", "none")
    $("#sidebar_navigation_data").css("display", "")
    $("#sidebar_simulation_real").css("display", "none")

    var vin = document.getElementById('firstVin').value;
    $("#VIN").val(vin);

    var selector = document.getElementById('selector_select').value;
    var options = Array.from(document.querySelector("#selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == selector) {
            document.querySelector("#selector").selectedIndex = j;
        }
    }

    selector = document.getElementById('sim_real_select').value;
    options = Array.from(document.querySelector("#sim_real_selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == selector) {
            document.querySelector("#sim_real_selector").selectedIndex = j;
        }
    }
    
    document.getElementById('VINButton').click()
}


// Function to show the simulation interface by clicking on the sidebar reference
var displaySim = function () {
    $("#VinEingabe").css("display", "none");
    $("#SimulationDivision").css("display", "");
}


// Function to show the standard interface for selecting a route by clicking on the sidebar reference
var displayRoutes = function () {
    $("#SimulationDivision").css("display", "none");
    $("#VinEingabe").css("display", "");
}


// Function to insert the options into the select lists for the simulation
var getOptions_sim = function () {
    // Route to get the ids for the routes from the database
    let response = await fetch("/getIDs", {
        credentials: 'same-origin'
    });
    let id_list = await response.json();

    // Route to get the cars from the database
    let response2 = await fetch("/getCars", {
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
var createSimulation = function () {
    // Call python function
    const { PythonShell } = require('python-shell');

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

    // Get id of created route
    var id = 0;
    // Put values into header selections
    var options = Array.from(document.querySelector("#sim_real_selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == 'simulations') {
            document.querySelector("#sim_real_selector").selectedIndex = j;
        }
    }

    options = Array.from(document.querySelector("#selector").options);
    for (var j = 0; j < options.length; j++) {
        if (options[j].value == 'id') {
            document.querySelector("#selector").selectedIndex = j;
        }
    }

    $("#VIN").val(text_received);

    // Show dashboard maps
    document.getElementById('VINButton').click()
}

var update = async function () {
    var selector = document.getElementById('selector').value;
    var vin = document.getElementById('VIN').value;
    var sim_real = document.getElementById('sim_real_selector').value;
    console.log(vin)
    vin = (vin === "") ? "none" : vin; 
    var dateArray = (document.getElementById('datepicker').value).split(".")
    var date = (dateArray[1] + '-' + dateArray[0]+ '-' + dateArray[2])
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
    let response = await fetch("/getTrips/" + date + "/" + sim_real + "/" + selector + "/" + vin, {
        credentials: 'same-origin'
    });
    let filenames = await response.json();
    console.log(filenames)
    var nof = 0;
    var fn = [];
    $("#allTrips").empty()
    filenames.forEach(file => {
        console.log(file.filename)
        fn.push(file.filename)
        nof++;
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
    printMarkers(fn, nof);
    $("#charts").empty()
    if(nof === 0) {
        $("#dataPart").css("display", "none")
    } else {
        $("#dataPart").css("display", "")
    }
    for(var h = 1; h <= nof; h++) {
        console.log("Filename: " + fn[h-1])
        $("#charts").append("<div id='Fahrt " + h + "'></div>")
        $("#charts").append("<div id='Fahrt " + h + " height profile" + "'></div>")
        getData(fn[h-1], "Fahrt " + h);
    }
    $(function() {
        console.log($(".filename").length);
        //console.log($(".test:eq(0)").attr('test'));
        for(var i = 0; i < $(".filename").length; i++) {
            $(".filename:eq(" + i + ")").change(function(){
                var filenames = [];
                var nof = 0;
                $("#charts").empty()
                //console.log($(this).prop('checked'));
                //console.log($(".test").length);
                for(var g = 0; g < $(".filename").length; g++) {
                    //console.log($(".test:eq(" + g + ")").prop('checked'));
                    if($(".filename:eq(" + g + ")").prop('checked')) {
                        //console.log($(".test:eq(" + g + ")").attr('test'));
                        filenames.push($(".filename:eq(" + g + ")").attr('filename'));
                        nof++;
                        $("#charts").append("<div id='Fahrt " + (g + 1) + "'></div>")
                        $("#charts").append("<div id='Fahrt " + (g + 1) + " height profile" + "'></div>")
                        getData($(".filename:eq(" + g + ")").attr('filename'), "Fahrt " + (g + 1));
                    }
                }
                console.log(filenames);
                printMarkers(filenames, nof);
            });
        }
    });
}

update()