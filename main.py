from pywebio import start_server
from organizer.airtravel_organizer import AirTravelOrganizer

if __name__ == '__main__':
    app = AirTravelOrganizer()
    start_server(app.welcome, port=8080, debug=True)
# minor update to refresh commit message
