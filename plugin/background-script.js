httpRequest = new XMLHttpRequest();

function convertToString(json_payload) {
    ret = "Date:Amount\n"

    for (var entry in json_payload) {
        ret += json_payload[entry].date+':'+json_payload[entry].amount+'\n';
    }
    return ret;
}

function notify(message) {
  message = convertToString(JSON.parse(message).history.land_data);
  browser.notifications.create({
    "type": "basic",
    "iconUrl": "",
    "title": "LandRegistry History",
    "message": message
  });    // process the server response
}

function get_history(lan,lon) {


  httpRequest.open('GET', 'http://localhost:8080/land/51.387585/-0.32609', true);
  httpRequest.send(null);

}


httpRequest.onload = function () {
  console.log('DONE', xhr.status);
};

httpRequest.onreadystatechange = function(){

   if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        notify(httpRequest.responseText);
      } else {
        log.console('There was a problem with the request.');
      }
    }

};

/*
Assign `notify()` as a listener to messages from the content script.
*/
browser.runtime.onMessage.addListener(get_history);
