from calendar import HTMLCalendar
from .models import Entry
from django.utils.html import format_html

class XCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(XCalendar, self).__init__()
        self.cssclass_month = "calendar"

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="calendar__day calendar__day--empty">&nbsp;</td>'
        
        entries = Entry.objects.filter(
            owner=self.user, 
            event_date__year=self.year, 
            event_date__month=self.month, 
            event_date__day=day
        )
        
        css_class = "calendar__day"
        events_html = ""
        
        # Format date string for data attribute (YYYY-MM-DD)
        date_str = f"{self.year}-{self.month:02d}-{day:02d}"
        
        if entries.exists():
            css_class += " calendar__day--active"
            events_html = '<div class="calendar__events">'
            for entry in entries:
                # Mood color mapping could be done here or via CSS classes
                mood_class = f"event--{entry.mood.lower()}" if entry.mood else "event--default"
                events_html += f'<div class="event-pill {mood_class}" title="{entry.title}" draggable="true" data-entry-id="{entry.id}">{entry.title}</div>'
            events_html += '</div>'
            
        return f'<td class="{css_class}" data-date="{date_str}"><div class="day-wrapper"><span class="calendar__date">{day}</span>{events_html}</div></td>'

    def formatmonth(self, withyear=True):
        """
        Return a formatted month as a table.
        """
        self.year, self.month = int(self.year), int(self.month)
        return super(XCalendar, self).formatmonth(self.year, self.month)