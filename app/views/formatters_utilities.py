
""" START - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""

# checks and formats roles
def roles_formatter(view, context, model, name):
    if model.roles:
        return ", ".join([role.name for role in model.roles])
    return ""

# checks and forms events
def events_formatter(view, context, model, name):
    if model.events:
        return ", ".join([f"Event {event.event_id} at {event.timestamp}" for event in model.events])
    return ""

# References:
# https://www.w3schools.com/python/ref_string_join.asp
# https://docs.python.org/3/

""" END - Documentation and research materials were used in the development of the code, 
including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. 
Note: Some parts were copied and closely adopted.
"""