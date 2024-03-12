import os
import math
import requests
import concurrent.futures
from multiprocessing.pool import ThreadPool

from betsapi import BetsApiService
from config import r_sport_ids


# bets_api_service = BetsApiService()
# bets_api = bets_api_service.get_bets_api_instance()
#
# for r_sport_id in r_sport_ids:
#     # get the inplays, filter inplays by r_sport_id and page
#     inplays = bets_api.get_bet365_inplay_filter({
#         "sport_id": r_sport_id,
#         "page": 1
#     })
#
#     bets_api_service.sync_filtered_inplays_events(inplays)
#     inplays_end_page = math.ceil(inplays['pager']['total'] / inplays['pager']['per_page'])
#
#     if inplays_end_page > 1:
#         for inplays_page in range(2, inplays_end_page + 1):
#             inplays = bets_api.get_bet365_inplay_filter({
#                 "sport_id": r_sport_id,
#                 "page": inplays_page
#             })
#
#             bets_api_service.sync_filtered_inplays_events(inplays)
#
#     # get upcoming events, filter it sport_id and page
#     upcoming_events = bets_api.get_bet365_upcoming_events({
#         "sport_id": r_sport_id,
#         "page": 1
#     })
#
#     bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)
#     upcoming_events_end_page = math.ceil(upcoming_events['pager']['total'] / upcoming_events['pager']['per_page'])
#
#     if upcoming_events_end_page > 1:
#         for events_page in range(2, upcoming_events_end_page + 1):
#             inplays = bets_api.get_bet365_inplay_filter({
#                 "sport_id": r_sport_id,
#                 "page": events_page
#             })
#
#             bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)


# TODO: optimize this code
# Need to fix python quit unexpectedly
def process_inplays_events(page_data):
    r_sport_id, inplays_page = page_data
    bets_api_service = BetsApiService()
    bets_api = bets_api_service.get_bets_api_instance()

    inplays = bets_api.get_bet365_inplay_filter({
        "sport_id": r_sport_id,
        "page": inplays_page
    })
    bets_api_service.sync_filtered_inplays_events(inplays)


def process_upcoming_events(page_data):
    r_sport_id, events_page = page_data
    bets_api_service = BetsApiService()
    bets_api = bets_api_service.get_bets_api_instance()

    upcoming_events = bets_api.get_bet365_upcoming_events({
        "sport_id": r_sport_id,
        "page": events_page
    })
    bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)


if __name__ == "__main__":
    # Determine the number of worker threads based on the CPU cores
    num_workers = min(8, os.cpu_count() or 1)  # Limit to 8 workers

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit tasks to the thread pool for inplay events
        inplays_pages = [(r_sport_id, 1) for r_sport_id in r_sport_ids]
        executor.map(process_inplays_events, inplays_pages)

        # Submit tasks to the thread pool for upcoming events
        upcoming_events_pages = [(r_sport_id, 1) for r_sport_id in r_sport_ids]
        executor.map(process_upcoming_events, upcoming_events_pages)

