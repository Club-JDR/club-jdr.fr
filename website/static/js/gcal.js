document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('gcal');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        locale: 'fr',
        themeSystem: 'bootstrap',
        initialView: 'listMonth',
        headerToolbar: { left: 'prev,next', center: 'title', right: '' },
        googleCalendarApiKey: 'AIzaSyAS28nNQCIfyUTjSLa9e9wT45BhjSxPoXw',
        events: 'm864cqm7ptg77gc6hevr9l91r0@group.calendar.google.com',
    });
    calendar.render();
});
