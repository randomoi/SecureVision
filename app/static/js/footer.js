/*
START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/

// wait for DOM to load
document.addEventListener("DOMContentLoaded", function() {
    // updates date and time
    function updateDateAndTime() {
        // gets current date and time
        let currentDateAndTime = new Date();

        // formats  date and time as a string
        let dateAndTimeString = currentDateAndTime.toLocaleDateString() + " " + currentDateAndTime.toLocaleTimeString();

        // updates content 
        document.getElementById("dateAndTime").textContent = dateAndTimeString;

        // gets current year
        const currentYear = currentDateAndTime.getFullYear();

        // updates content 
        document.getElementById("currentYear").textContent = currentYear;
    }

    // first update of date and time
    updateDateAndTime();

    // setup an interval to update date and time every second 
    setInterval(updateDateAndTime, 1000);
});

// References:
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date
// https://www.w3schools.com/js/js_dates.asp
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/getFullYear
// https://www.w3docs.com/snippets/javascript/how-get-the-current-year-in-javascript.html

/*
END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links.
*/