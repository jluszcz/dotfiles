_<% tp.date.now("dddd") %>_

<%* if (moment(tp.date.yesterday()).day() == 0) { -%>
- [Friday](<% tp.date.now("YYYY-MM-DD", -3) %>)
<%* } else { -%>
- [Yesterday](<% tp.date.now("YYYY-MM-DD", -1) %>)
<%* } -%>
- Today
    - **Carry over any #todo items**

----
### TODOs
