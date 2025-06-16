from heapq import heappush, heappop
from pywebio.output import put_html, put_text, put_warning, put_buttons, use_scope

from .suggestion_strategy import SuggestionStrategy

class CheapestStrategy(SuggestionStrategy):
    def suggest(self, manager, from_airport, to_airport, seat_type, result_scope, graph_scope):
        pq = [(0, [from_airport])]
        costs = {a: float('inf') for a in manager.airports}
        costs[from_airport] = 0
        final_path, final_cost = None, float('inf')

        while pq:
            cost, path = heappop(pq)
            cur = path[-1]
            if cost > costs[cur]:
                continue
            if cur == to_airport:
                if cost < final_cost:
                    final_cost, final_path = cost, path
                continue

            for f in manager.flights.get(cur, []):
                nc = cost + f[seat_type.lower()]
                if nc < costs[f['to']]:
                    costs[f['to']] = nc
                    heappush(pq, (nc, path + [f['to']]))

        with use_scope(result_scope):
            put_html(f"<b>Cheapest {seat_type} Route:</b><br><br>")
            if not final_path:
                put_warning(f"No {seat_type} route from {from_airport} to {to_airport}.")
            else:
                put_text(f"Path: {' → '.join(final_path)}")
                put_text(f"Total Cost: ${final_cost:.2f}")
                put_buttons(
                    ['Show Graph'],
                    onclick=lambda _: manager.visualize([final_path], scope_name=graph_scope)
                )
        put_html("", scope=graph_scope)
