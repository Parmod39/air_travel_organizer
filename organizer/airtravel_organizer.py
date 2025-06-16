import os
import graphviz
from itertools import count
from random import choice

from pywebio import start_server
from pywebio.input import input_group, input, select, FLOAT, TEXT, NUMBER
from pywebio.output import put_text, put_html, put_buttons, put_image, put_warning, use_scope, clear

from strategies.cheapest_strategy import CheapestStrategy
from strategies.cost_strategy import CostStrategy
from strategies.stops_strategy import StopsStrategy

class AirTravelOrganizer:
    def __init__(self):
        self.airports = set()
        self.flights = {}
        self.airport_counter = count(1)
        self.flight_counter = count(1)
        self.suggestion_counters = {'cheapest': 0, 'cost': 0, 'stops': 0}
        self.strategies = {
            'Find Cheapest Route': CheapestStrategy(),
            'Find Routes by Max Cost': CostStrategy(),
            'Find Routes by Max Stops': StopsStrategy()
        }
        self.palette = ['#FF5733', '#33FF57', '#3357FF', '#FF33A1']

    # --- Unique Generators ---
    def _gen_airport(self):
        i = next(self.airport_counter)
        return f"A{i:03}", f"Airport_{i}"

    def _gen_flight(self):
        a_list = list(self.airports)
        if len(a_list) < 2:
            return None
        src, dst = choice(a_list), choice(a_list)
        while dst == src:
            dst = choice(a_list)
        i = next(self.flight_counter)
        dep_hour, arr_hour = 8 + (i % 12), 9 + (i % 12)
        return src, dst, f"{dep_hour:02}:00", f"{arr_hour:02}:00", 100 + i*10, 200 + i*15

    # --- UI Pages ---
    def welcome(self):
    # Header section with centered styling
        put_html("""
        <style>
            /* Ensure any button container is centered */
            .btn-center-container {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 20px;
            }
        </style>
        <div style="text-align:center; padding:20px;">
            <h1 style="color:#2F4F4F; font-size:48px;">🌍 Air Travel Organizer System ✈</h1>
            <p style="font-size:22px; color:#4682B4; font-weight:bold;">
                Plan your journey with ease.
            </p>
            <p style="font-size:18px; color:#5F9EA0; max-width:700px; margin:0 auto;">
                Welcome to your all-in-one flight management hub. Whether you’re adding airports, scheduling flights,
                or hunting for the cheapest travel route, our system brings complex route planning and visualization
                into a single, intuitive interface. Get started below!
            </p>
        </div>""")

        # Wrap buttons in a flex container for centering
        put_html('<div class="btn-center-container">')
        put_buttons(
            ['✈ Manage Airports', '🛫 Manage Flights', '📅 Flight Suggestions', '🗺 Full Flight Map'],
            onclick=[self.manage_airports, self.manage_flights, self.flight_suggestions_ui, self.show_map]
        )
        put_html('</div>')




    def manage_airports(self):
        opt = select("Choose Airport Operation", ['Add Airport', 'Delete Airport'], scope='asp')
        clear('asp')
        if opt == 'Add Airport':
            code, name = self._gen_airport()
            d = input_group("Add Airport", [
                input("Airport Code", name='code', value=code, type=TEXT),
                input("Airport Name", name='name', value=name, type=TEXT)
            ])
            c = d['code'].upper()
            if c not in self.airports:
                self.airports.add(c)
                put_text(f"✅ Airport {d['name']} ({c}) added.")
            else:
                put_text(f"⚠ Airport {c} exists.")
        else:
            if not self.airports:
                put_warning("No airports to delete.")
                return
            to_del = select("Select Airport", sorted(self.airports), scope='asp')
            clear('asp')
            self.airports.remove(to_del)
            self.flights.pop(to_del, None)
            for src in list(self.flights):
                self.flights[src] = [f for f in self.flights[src] if f['to'] != to_del]
                if not self.flights[src]:
                    del self.flights[src]
            put_text(f"❌ Airport {to_del} deleted.")

    def manage_flights(self):
        opt = select("Choose Flight Operation", ['Add Flight', 'Delete Flight'], scope='fsp')
        clear('fsp')
        if opt == 'Add Flight':
            if len(self.airports) < 2:
                put_warning("Add at least two airports first.")
                return
            defaults = self._gen_flight()
            if not defaults:
                put_warning("Not enough airports.")
                return
            src, dst, dep, arr, eco, bus = defaults
            d = input_group("Add New Flight", [
                select("From", name='from', options=sorted(self.airports), value=src),
                select("To", name='to', options=sorted(self.airports), value=dst),
                input("Departure", name='dep', value=dep, type=TEXT),
                input("Arrival", name='arr', value=arr, type=TEXT),
                input("Economy Fare", name='eco', value=str(eco), type=FLOAT),
                input("Business Fare", name='bus', value=str(bus), type=FLOAT),
            ])
            self.flights.setdefault(d['from'], []).append({
                'to': d['to'],
                'departure': d['dep'],
                'arrival': d['arr'],
                'economy': float(d['eco']),
                'business': float(d['bus'])
            })
            put_text(f"✈ Flight added: {d['from']} → {d['to']} (Dep:{d['dep']}, Arr:{d['arr']})")
        else:
            if not self.flights:
                put_warning("⚠ No flights to delete.")
                return
            opts = []
            for src, fls in self.flights.items():
                for i, f in enumerate(fls):
                    opts.append({
                        'label': f"{src} → {f['to']} (Dep:{f['departure']}, Arr:{f['arrival']})",
                        'value': (src, i)
                    })
            src, i = select("Select Flight", options=opts)
            f = self.flights[src].pop(i)
            if not self.flights[src]:
                del self.flights[src]
            put_text(f"🗑 Deleted flight {src} → {f['to']}")

    def flight_suggestions_ui(self):
        if len(self.airports) < 2:
            put_warning("Need ≥2 airports.")
            return
        opt = select("Choose Suggestion", list(self.strategies), scope='ssp')
        clear('ssp')
        a_list = sorted(self.airports)
        if 'Cheapest' in opt:
            d = input_group("Cheapest Flight", [
                select("From", name='from', options=a_list),
                select("To", name='to', options=a_list),
                select("Seat Type", name='seat_type', options=['Economy', 'Business'])
            ])
            self._run_strategy(opt, d['from'], d['to'], d['seat_type'])
        elif 'Max Cost' in opt:
            d = input_group("Flights by Max Cost", [
                select("From", name='from', options=a_list),
                select("To", name='to', options=a_list),
                input("Max Cost ($)", name='max_cost', type=FLOAT)
            ])
            self._run_strategy(opt, d['from'], d['to'], d['max_cost'])
        else:
            d = input_group("Flights by Max Stops", [
                select("From", name='from', options=a_list),
                select("To", name='to', options=a_list),
                input("Max Stops", name='max_stops', type=NUMBER)
            ])
            self._run_strategy(opt, d['from'], d['to'], d['max_stops'])

    def _run_strategy(self, opt, from_airport, to_airport, param):
        key = 'cheapest' if 'Cheapest' in opt else ('cost' if 'Cost' in opt else 'stops')
        self.suggestion_counters[key] += 1
        idx = self.suggestion_counters[key]
        rs, gs = f"{key}_results_{idx}", f"{key}_graph_{idx}"
        strat = self.strategies[opt]
        kwargs = {}
        if 'Cheapest' in opt:
            kwargs['seat_type'] = param
        elif 'Cost' in opt:
            kwargs['max_cost'] = param
        else:
            kwargs['max_stops'] = param
        strat.suggest(self, from_airport=from_airport, to_airport=to_airport,
                      result_scope=rs, graph_scope=gs, **kwargs)

    def show_map(self):
        put_html('<h2 style="text-align:center;">Full Flight Map</h2>', scope='graph_map')
        self.visualize(None, scope_name='graph_map')

    def visualize(self, highlighted_paths=None, scope_name='graph'):
        with use_scope(scope_name, clear=True):
            if not self.airports:
                put_warning("⚠ No airports to visualize.")
                return

            # ensure graphviz on PATH if installed in custom dir
            gpath = 'C:/Program Files/Graphviz/bin'
            if os.path.exists(gpath) and gpath not in os.environ['PATH']:
                os.environ['PATH'] += os.pathsep + gpath

            dot = graphviz.Digraph('FlightMap', strict=False)
            dot.attr('node', shape='invhouse', style='filled', color='lightblue', fontname='Helvetica')
            dot.attr('edge', fontname='Helvetica', fontsize='10', splines='curved',
                     overlap='false', labelfloat='false', fontrotate='true',
                     labeldistance='1.2', labelangle='0')

            node_colors, edge_color_lists = {}, {}
            if highlighted_paths:
                for i, path in enumerate(highlighted_paths):
                    c = self.palette[i % len(self.palette)]
                    for n in path:
                        node_colors[n] = c
                    for u, v in zip(path, path[1:]):
                        edge_color_lists.setdefault((u, v), []).append(c)

            edge_colors = {}
            for edge, cols in edge_color_lists.items():
                rgbs = [tuple(int(col.lstrip('#')[j:j+2],16) for j in (0,2,4)) for col in cols]
                avg = tuple(sum(ch[i] for ch in rgbs)//len(rgbs) for i in range(3))
                mixed = '#{:02X}{:02X}{:02X}'.format(*avg)
                if mixed.upper() == '#000000':
                    mixed = '#888888'
                edge_colors[edge] = mixed

            for code in sorted(self.airports):
                dot.node(code, code, color=node_colors.get(code, 'lightblue'))
            for src, lst in self.flights.items():
                for idx, f in enumerate(lst):
                    lbl = f"E: ${f['economy']:.2f}\\nB: ${f['business']:.2f}"
                    key = f"{src}_{f['to']}_{idx}"
                    col = edge_colors.get((src, f['to']), '#555555')
                    pw = '2.5' if (src, f['to']) in edge_colors else '1.0'
                    dot.edge(src, f['to'], key=key, label=lbl, color=col, penwidth=pw)

            put_html('<hr>')
            try:
                img = dot.pipe(format='png')
                put_image(img)
            except Exception as e:
                put_warning(f"Visualization error: {e}")
            put_html('<hr>')
