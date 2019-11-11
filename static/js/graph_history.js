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
        console.log(data);
        // getting chart from page
        var ctx = document.getElementById('myChart').getContext('2d');

        let datasets = [];
        let background_colors = [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)'
        ];

        // generating datasets
        for(let i = 0; i < data.budgets.length; i++) {
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
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    });

};

function getSelectValues(select) {
    // gets list of select values, credit: stack overflow
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i=0, iLen=options.length; i<iLen; i++) {
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

