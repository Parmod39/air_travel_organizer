from pywebio.output import put_html, put_text, put_warning, put_buttons, use_scope
from .suggestion_strategy import SuggestionStrategy

class CostStrategy(SuggestionStrategy):
    def suggest(self, manager, from_airport, to_airport, max_cost, result_scope, graph_scope):
        all_paths = []

        def dfs(cur, details, econ_sum, bus_sum, visited):
            if cur == to_airport:
                path = [details[0]['from']] + [leg['to'] for leg in details]
                all_paths.append({
                    'details': details.copy(),
                    'econ': econ_sum,
                    'bus': bus_sum,
                    'path': path
                })
                return
            for f in manager.flights.get(cur, []):
                nxt, ec, bc = f['to'], f['economy'], f['business']
                if nxt not in visited and (econ_sum + ec <= max_cost or bus_sum + bc <= max_cost):
                    visited.add(nxt)
                    details.append({'from': cur, 'to': nxt, 'econ': ec, 'bus': bc})
                    dfs(nxt, details, econ_sum + ec, bus_sum + bc, visited)
                    details.pop()
                    visited.remove(nxt)

        dfs(from_airport, [], 0, 0, {from_airport})

        with use_scope(result_scope):
            put_html(f"<b>Routes Under ${max_cost:.2f}:</b><br><br>")
            if not all_paths:
                put_warning(f"No routes from {from_airport} to {to_airport} under ${max_cost:.2f}.")
            else:
                for idx2, p in enumerate(sorted(all_paths, key=lambda x: x['econ']), 1):
                    put_html(f"<u>Route {idx2}</u> – Economy: ${p['econ']:.2f}, Business: ${p['bus']:.2f}")
                    for leg in p['details']:
                        put_text(f"  • {leg['from']} → {leg['to']}  (Economy: ${leg['econ']:.2f}, Business: ${leg['bus']:.2f})")
                put_buttons(
                    ['Show Graph'],
                    onclick=lambda _: manager.visualize([p['path'] for p in all_paths], scope_name=graph_scope)
                )
        put_html("", scope=graph_scope)
