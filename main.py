import math
import multiprocessing

from betsapi import BetsApiService
from config import r_sport_ids

bets_api_service = BetsApiService()
bets_api = bets_api_service.get_bets_api_instance()


def process_sport_id(r_sport_id):
    """Retrieves and processes data for a given sport_id."""

    inplays = bets_api.get_bet365_inplay_filter({"sport_id": r_sport_id, "page": 1})
    bets_api_service.sync_filtered_inplays_events(inplays)

    inplays_end_page = math.ceil(inplays['pager']['total'] / inplays['pager']['per_page'])
    for inplays_page in range(2, inplays_end_page + 1):
        inplays = bets_api.get_bet365_inplay_filter({"sport_id": r_sport_id, "page": inplays_page})
        bets_api_service.sync_filtered_inplays_events(inplays)

    upcoming_events = bets_api.get_bet365_upcoming_events({"sport_id": r_sport_id, "page": 1})
    bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)

    upcoming_events_end_page = math.ceil(upcoming_events['pager']['total'] / upcoming_events['pager']['per_page'])
    for events_page in range(2, upcoming_events_end_page + 1):
        inplays = bets_api.get_bet365_inplay_filter({"sport_id": r_sport_id, "page": events_page})
        bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)


def background_task():
    """Executes data retrieval and processing in the background."""

    with multiprocessing.Pool() as pool:
        pool.map(process_sport_id, r_sport_ids)

    print("Data processing for all sport IDs completed (running in background).")


if __name__ == "__main__":
    while True:
        background_task()
        user_input = input("Press 'Y' to restart the background process, anything else to exit: ").upper()
        if user_input != "Y":
            break





