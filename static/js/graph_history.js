'use strict';

const get_budget_info = async (start, end, budgets, url) => {
    // defining body according to api standard
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

        1. the difference_value
            - this is the amount gained/lost from the start to the end
     */

    let difference_value = get_difference_value(data);
    let percent_difference = get_percent_difference_value(data);

    let statslist = document.getElementById('statslist');

    statslist.innerHTML = "<tr><th>Field</th><th>Value</th></tr>";
    statslist.innerHTML += "<tr>" +
        "<td>Total Difference</td>" +
        "<td>" + String(difference_value.toFixed(2)) + "</td>" +
        "</tr>";
    statslist.innerHTML += String("<tr><td>Percent Difference</td><td>" +
                String(percent_difference.toFixed(2)) +
             "%</td></tr>");
}

function get_difference_value(data) {
    /*
        dollar value difference between the start and end dates in dataset

        "param data: is the graph_history API response json object
     */
    let start_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        start_balance += data.budgets[i].data[0]
    }
    let end_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        end_balance += data.budgets[i].data[data.days.length - 1]
    }
    return end_balance - start_balance;
}

function get_percent_difference_value(data) {
    /*
        dollar value difference between the start and end dates in dataset

        "param data: is the graph_history API response json object
     */
    let start_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        start_balance += data.budgets[i].data[0]
    }
    let end_balance = 0;
    for (let i = 0; i < data.budgets.length; i++) {
        end_balance += data.budgets[i].data[data.days.length - 1]
    }
    return start_balance / end_balance;
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

