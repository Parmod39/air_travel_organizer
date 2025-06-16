from pywebio.output import put_html, put_text, put_warning, put_buttons, use_scope
from .suggestion_strategy import SuggestionStrategy

class StopsStrategy(SuggestionStrategy):
    def suggest(self, manager, from_airport, to_airport, max_stops, result_scope, graph_scope):
        queue, routes = [[from_airport]], []

        while queue:
            path = queue.pop(0)
            if len(path) - 1 > max_stops:
                continue
            if path[-1] == to_airport:
                routes.append(path)
            if len(path) - 1 < max_stops:
                for f in manager.flights.get(path[-1], []):
                    if f['to'] not in path:
                        queue.append(path + [f['to']])

        with use_scope(result_scope):
            put_html(f"<b>Routes with up to {max_stops} Stops:</b><br><br>")
            if not routes:
                put_warning(f"No routes from {from_airport} to {to_airport} with up to {max_stops} stops.")
            else:
                for idx2, route in enumerate(sorted(routes, key=len), 1):
                    put_text(f"Route {idx2}: {' → '.join(route)}")
                put_buttons(
                    ['Show Graph'],
                    onclick=lambda _: manager.visualize(routes, scope_name=graph_scope)
                )
        put_html("", scope=graph_scope)
