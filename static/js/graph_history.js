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

        // fetching data from
        const response = fetch(url, settings);

        if (!response.ok) {
            // checking if response is OK
            console.log("ERROR: bad response");
            console.log(response.status);
            console.log(response.body);
            return undefined

        }

        return await response.json();

    } catch (e) {
        // catching errors
        console.log(e);
        return undefined;
    }

};

const renderGraph = (url) => {
    let start = document.getElementById("id_start").value;
    let end = document.getElementById("id_end").value;
    let budgets = getSelectValues(document.getElementById("id_budgets"));
    let data = get_budget_info(start, end, budgets, url)

};

function getSelectValues(select) {
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

