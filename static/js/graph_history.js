'use strict';


function set_initial_dates(url) {
    /*
    This sets the first dates to be
        start is 1 week from today
        end is today

       when the user first reaches the page
     */
    let end = new Date();
    end.setDate(end.getDate());

    let start = new Date();
    start.setDate(start.getDate() - 7);

    const options = {year: 'numeric', day: '2-digit', month: '2-digit'};

    document.getElementById('id_start').value = start.toLocaleDateString('UTC', options);
    document.getElementById('id_end').value = end.toLocaleDateString('UTC', options);

    // showing graph
    renderGraph(url);
}

const get_budget_info = async (start, end, budgets, url) => {
    // defining body according to web standard
    const csrftoken = getCookie('csrftoken');

    url = url + "?start=" + start + "&end=" + end + "&budgets=" + budgets;
    // defining settings
    const settings = {
        method: "GET",
        headers: {
            Accept: 'application/json',
            "Content-Type": 'application/json',
            "X-CSRFToken": csrftoken
        },
    };
    try {
        // fetching data from URL
        const response = await fetch(url, settings);

        return response.json();

    } catch (e) {
        // catching errors
        alert(e);
        console.log(e);
        return undefined;
    }

};

const renderGraph = (url) => {
    // getting data from form
    let start = document.getElementById("id_start").value;
    let end = document.getElementById("id_end").value;
    let budgets = getSelectValues(document.getElementById("id_budgets"));

    // plotting budgets after fetch
    get_budget_info(start, end, budgets, url).then((data) => {
        // handling errors
        if ('error' in data) {
            // displaying message to user
            alert(data.error);

            // exiting..
            return;
        }

        // getting chart from page
        var ctx = document.getElementById('myChart').getContext('2d');

        let datasets = [];
        let background_colors = [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(255, 102, 178, 0.2)',
            'rgba(102, 255, 102, 0.2)',
            'rgba(102, 102, 255, 0.2)',
        ];
        // setting stats on the page
        set_stats(data);

        // generating datasets
        for (let i = 0; i < data.budgets.length; i++) {
            datasets.push({
                label: data.budgets[i].name,
                data: data.budgets[i].data,
                backgroundColor: [background_colors[i % background_colors.length]],
                borderWidth: 1
            })
        }
        // setting up chart
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.days,
                datasets: datasets
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            },
        });
    });
    myChart.height = 512;


};

function set_stats(data) {
    /*
        Populates div "stats"

        the difference_value
            - this is the amount gained/lost from the start to the end
        growth factor
            - How many times bigger the budget became since the start

         This populates the table on the "graph_history" page

     */

    let difference_value = get_difference_value(data).toFixed(2);
    let percent_difference = get_percent_difference_value(data).toFixed(2);
    let start_balance = get_start_balance(data).toFixed(2)
    let end_balance = get_end_balance(data).toFixed(2)

    let statslist = document.getElementById('statslist');

    statslist.innerHTML = "<tr><th>Field</th><th>Value</th></tr>";
    statslist.innerHTML += "<tr>" +
        "<td>Total Difference</td>" +
        "<td>" + String(difference_value) + "</td>" +
        "</tr>";
    statslist.innerHTML += String("<tr><td>Start Balance</td><td>" +
        String(start_balance) +
        "</td></tr>");
    statslist.innerHTML += String("<tr><td>End Balance</td><td>" +
        String(end_balance) +
        "</td></tr>");
    statslist.innerHTML += String("<tr><td>Growth Factor</td><td>" +
        String(percent_difference) +
        "x</td></tr>");
}

function get_start_balance(data) {
    /*
        returns the balance at the start of the time period
        "param data: is the graph_history API response json object
     */
    let start_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        start_balance += data.budgets[i].data[0];
    }
    return start_balance;
}

function get_end_balance(data) {
    /*
        returns the balance at the end of the time period
        "param data: is the graph_history API response json object
     */
    let end_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        end_balance += data.budgets[i].data[data.days.length - 1];
    }
    return end_balance;
}

function get_difference_value(data) {
    /*
        dollar value difference between the start and end dates in dataset

        "param data: is the graph_history API response json object
     */
    return get_end_balance(data) - get_start_balance(data);
}

function get_percent_difference_value(data) {
    /*
        dollar value difference between the start and end dates in dataset

        "param data: is the graph_history API response json object
     */
    let start_balance = get_start_balance(data);

    // this fixes dividing by zero errors
    if (start_balance === 0) {
        start_balance = 1;
    }

    return get_end_balance(data) / start_balance;
}

function getSelectValues(select) {
    // gets list of select values, credit: stack overflow
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i = 0, iLen = options.length; i < iLen; i++) {
        opt = options[i];

        if (opt.selected) {
            result.push(opt.text);
        }
    }
    return result;
}

function getCookie(name) {
    // gets the csrf cookie, credit: django CSRF documentation
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

