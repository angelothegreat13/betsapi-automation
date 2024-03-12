import math
import os
import json
import random
import mysql.connector

from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from http_helper import HttpHelper
from abc import ABC, abstractmethod
from helpers import get_data_from_file, get_id_name_info
from config import mysql_connection, r_sport_ids
from datetime import datetime

load_dotenv()


class BetsApiDataProvider(ABC):

    @abstractmethod
    def get_bet365_inplay(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_bet365_inplay_filter(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_bet365_inplay_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_bet365_upcoming_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_bet365_pre_match_odds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_bet365_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        pass


class BetsApiHttpData(BetsApiDataProvider):

    def __init__(self, http: HttpHelper):
        self._http = http
        self._configure_api()

    def _configure_api(self):
        self._http.set_base_url(f"{os.getenv('BETS_API_SCHEME')}://{os.getenv('X_RAPID_API_HOST')}")
        self._http.set_headers({
            "X-RapidAPI-Key": os.getenv('X_RAPID_API_KEY'),
            "X-RapidAPI-Host": os.getenv('X_RAPID_API_HOST')
        })

    def get_bet365_inplay(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        return self._http.get('/v1/bet365/inplay', params).json()

    def get_bet365_inplay_filter(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        return self._http.get('/v1/bet365/inplay_filter', params).json()

    def get_bet365_inplay_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.get('/v1/bet365/event', params).json()

    def get_bet365_upcoming_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.get('/v1/bet365/upcoming', params).json()

    def get_bet365_pre_match_odds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.get('/v3/bet365/prematch', params).json()

    def get_bet365_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return self._http.get('/v1/bet365/result', params).json()


class BetsApiSampleHttpData(BetsApiDataProvider):

    def get_bet365_inplay(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        return get_data_from_file('betsapi_sample_responses/bet365_inplay.json')

    def get_bet365_inplay_filter(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        return get_data_from_file('betsapi_sample_responses/bet365_inplay_filter.json')

    def get_bet365_inplay_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        events = [
            'bet365_event.basketball',
            'bet365_event.cricket',
            'bet365_event.cricket.lineup',
            'bet365_event.soccer',
            'bet365_event.soccer.stats',
            'bet365_event.tennis',
            'bet365_event.tennis.stats'
        ]

        random_event = random.choice(events)

        return get_data_from_file(f"betsapi_sample_responses/bet365_inplay_events/{random_event}.json")

    def get_bet365_upcoming_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return get_data_from_file('betsapi_sample_responses/bet365_upcoming.json')

    def get_bet365_pre_match_odds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return get_data_from_file('betsapi_sample_responses/bet365_prematch_odds.json')

    def get_bet365_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return get_data_from_file('betsapi_sample_responses/bet365_result.json')


conn, cursor = mysql_connection()
now = datetime.now()


class BetsApiService:

    def __init__(self, bets_api: object = None):
        if bets_api is None:
            bets_api = self._get_bets_api_instance()
        self.bets_api = bets_api

    def _get_bets_api_instance(self):
        if os.getenv('BETS_API_TEST_MODE').lower() == 'true':
            return BetsApiSampleHttpData()
        elif os.getenv('BETS_API_TEST_MODE').lower() == 'false':
            return BetsApiHttpData(HttpHelper())
        else:
            raise ValueError('Please set your BETS_API_TEST_MODE in .env')

    @staticmethod
    def save_bet365_inplay(inplays: Dict[str, Any]):
        response_data = json.dumps(inplays)
        query = "INSERT INTO bet365_inplays (response_data,created_at,updated_at) VALUES (%s, %s, %s)"
        cursor.execute(query, (response_data, now, now))
        conn.commit()

    @staticmethod
    def save_multiple_bet365_pre_match_odds(pre_match_odds: List[tuple]):
        if not pre_match_odds:
            print("Nothing to save.The provided pre_match_odds list is empty")
            return

        try:                                                                                                                                                                                                
            query = """                                                                                                                                                                                     
                INSERT INTO bet365_pre_match_odds                                                                                                                                                           
                (FI, event_id, event_sport_id, event_league_id, event_league_name, response_data, response_data, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
            cursor.executemany(query, pre_match_odds)
            conn.commit()
            print(f"Multiple pre-match odds successfully inserted into bet365_pre_match_odds table")
        except mysql.connector.Error as error:
            conn.rollback()                                                                                                                                                                                 
            print("Failed to insert record into bet365_pre_match_odds table: ", error.msg)

    @staticmethod
    def save_multiple_bet365_inplay_filter(inplays: List[tuple]):
        if not inplays:
            print("Nothing to save.The provided inplays list is empty")
            return

        try:
            query = """
                INSERT INTO bet365_inplay_filters 
                (api_id, sport_id, time, time_status, league_id, league_name, home_id, home_name, away_id, away_name, ss, our_event_id, r_id, ev_id, api_updated_at, response_data, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
            cursor.executemany(query, inplays)
            conn.commit()
            print(f"Multiple filtered in-plays successfully inserted into bet365_inplay_filters table")
        except mysql.connector.Error as error:
            conn.rollback()
            print("Failed to insert record into bet365_inplay_filters table: ", error.msg)

    @staticmethod
    def save_multiple_bet365_upcoming_events(upcoming_events: List[tuple]):
        if not upcoming_events:
            print("Nothing to save.The provided upcoming_events list is empty")
            return

        try:
            query = """                                                                                                                                                                                    
                INSERT INTO bet365_upcoming_events                                                                                                                                                          
                (api_id, sport_id, time, time_status, league_id, league_name, home_id, home_name, away_id, away_name, ss, our_event_id, r_id, api_updated_at, response_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
            cursor.executemany(query, upcoming_events)
            conn.commit()
            print(f"Multiple Upcoming Events successfully inserted into bet365_upcoming_events table")
        except mysql.connector.Error as error:
            conn.rollback()
            print("Failed to insert record into bet365_upcoming_events table: ", error.msg)

    @staticmethod
    def save_bet365_pre_match_odds(fi: str, event_id: str, sport_id: str, league_id: Optional[str], league_name: Optional[str], pre_match_odds: str):
        try:
            query = """
                INSERT INTO bet365_pre_match_odds
                (FI, event_id, event_sport_id, event_league_id, event_league_name, response_data, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) """
            cursor.execute(query, (fi, event_id, sport_id, league_id, league_name, pre_match_odds, now, now))
            conn.commit()
            print(f"Pre-match Odds: {fi} successfully inserted into bet365_pre_match_odds table")
        except mysql.connector.Error as error:
            conn.rollback()
            print("Failed to insert record into bet365_pre_match_odds table: ", error.msg)

    @staticmethod
    def save_bet365_inplay_events(inplay_id: str, sport_id: str, league_id: Optional[str], league_name: Optional[str], events: str):
        try:        
            query = """        
                INSERT INTO bet365_inplay_events         
                (inplay_id, inplay_sport_id, inplay_league_id, inplay_league_name, response_data, created_at,updated_at)         
                VALUES (%s, %s, %s, %s, %s, %s, %s) """        
            cursor.execute(query, (inplay_id, sport_id, league_id, league_name, events, now, now))        
            conn.commit()
            print(f"Inplay Event: {inplay_id} successfully inserted into bet365_inplay_events table")
        except mysql.connector.Error as error:
            conn.rollback()        
            print("Failed to insert record into bet365_inplay_events table: ", error.msg)

    @staticmethod
    def save_bet365_upcoming_events(inplay_id: str, sport_id: str, league_id: Optional[str], league_name: Optional[str], events: str):
        try:
            query = """                                                                                                                 
                INSERT INTO bet365_inplay_events                                                                                        
                (inplay_id, inplay_sport_id, inplay_league_id, inplay_league_name, response_data, created_at,updated_at)                
                VALUES (%s, %s, %s, %s, %s, %s, %s) """
            cursor.execute(query, (inplay_id, sport_id, league_id, league_name, events, now, now))
            conn.commit()
            print(f"Upcoming Event: {inplay_id} successfully inserted into bet365_inplay_events table")
        except mysql.connector.Error as error:
            conn.rollback()
            print("Failed to insert record into bet365_upcoming_events table: ", error.msg)

    @staticmethod
    def sync_upcoming_events_pre_match_odds(upcoming_events: Dict[str, Any]):
        if 'success' not in upcoming_events or upcoming_events['success'] != 1 or not upcoming_events['results']:
            print("Error: Failed to retrieve valid upcoming events data. Please check API response for 'success' status and 'results' availability.")
            return

        insert_events_data = []

        for event in upcoming_events['results']:
            event_id = event['id']
            sport_id = event.get('sport_id', None)
            league_id = event['league']['id'] if event['league'] is not None else None
            league_name = event['league']['name'] if event['league'] is not None else None

            # fetch pre_match_odds filtered by event_id
            pre_match_odds = bets_api.get_bet365_pre_match_odds({
                "FI": event_id,
            })
            
            # save pre_match_odds if success else just continue
            if 'success' not in pre_match_odds or pre_match_odds['success'] != 1:
                continue

            for pre_match in pre_match_odds['results']:
                BetsApiService.save_bet365_pre_match_odds(pre_match['FI'], pre_match['event_id'], sport_id, league_id, league_name, json.dumps(pre_match))

            # populate a data(List[tuple]) to be inserted in bet365_upcoming_events table
            data_to_insert = (
                event_id,
                sport_id,
                event['time'],
                event['time_status'],
                league_id,
                league_name,
                *get_id_name_info(event['home']),
                *get_id_name_info(event['away']),
                event['ss'],
                event.get('our_event_id', None),
                event.get('r_id', None),
                event.get('updated_at', None),
                json.dumps(event),
                now,
                now
            )
            insert_events_data.append(data_to_insert)

        # save bet365 upcoming events
        BetsApiService.save_multiple_bet365_upcoming_events(insert_events_data)

    @staticmethod
    def sync_filtered_inplays_events(inplays: Dict[str, Any]):
        if 'success' not in inplays or inplays['success'] != 1 or not inplays['results']:
            print("Error: Failed to retrieve valid in-plays data. Please check API response for 'success' status and 'results' availability.")
            return

        insert_inplays_data = []

        for inplay in inplays['results']:
            inplay_id = inplay['id']
            sport_id = inplay['sport_id']
            league_id = inplay['league']['id'] if inplay['league'] is not None else None
            league_name = inplay['league']['name'] if inplay['league'] is not None else None

            # fetch inplay_events by inplay_id
            inplay_events = bets_api.get_bet365_inplay_event({
                "FI": inplay_id,
            })

            # save inplay_events if success else just continue
            if 'success' not in inplay_events or inplay_events['success'] != 1:
                continue
                
            BetsApiService.save_bet365_inplay_events(inplay_id, sport_id, league_id, league_name, json.dumps(inplay_events))

            # populate a data(List[tuple]) to be inserted in bet365_filter table
            data_to_insert = (
                inplay_id,
                sport_id,
                inplay['time'],
                inplay['time_status'],
                league_id,
                league_name,
                *get_id_name_info(inplay['home']),
                *get_id_name_info(inplay['away']),
                inplay['ss'],
                inplay['our_event_id'],
                inplay['r_id'],
                inplay['ev_id'],
                inplay['updated_at'],
                json.dumps(inplay),
                now,
                now
            )
            insert_inplays_data.append(data_to_insert)

        # save bet365 inplay filters
        BetsApiService.save_multiple_bet365_inplay_filter(insert_inplays_data)


bets_api_service = BetsApiService()
bets_api = bets_api_service.bets_api

for r_sport_id in r_sport_ids:
    # get the inplays, filter inplays by r_sport_id and page
    inplays = bets_api.get_bet365_inplay_filter({
        "sport_id": r_sport_id,
        "page": 1
    })

    bets_api_service.sync_filtered_inplays_events(inplays)
    inplays_end_page = math.ceil(inplays['pager']['total'] / inplays['pager']['per_page'])

    if inplays_end_page > 1:
        for inplays_page in range(2, inplays_end_page + 1):
            inplays = bets_api.get_bet365_inplay_filter({
                "sport_id": r_sport_id,
                "page": inplays_page
            })

            bets_api_service.sync_filtered_inplays_events(inplays)

    # get upcoming events, filter it sport_id and page
    upcoming_events = bets_api.get_bet365_upcoming_events({
        "sport_id": r_sport_id,
        "page": 1
    })
    
    bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)
    upcoming_events_end_page = math.ceil(upcoming_events['pager']['total'] / upcoming_events['pager']['per_page'])

    if upcoming_events_end_page > 1:
        for events_page in range(2, upcoming_events_end_page + 1):
            inplays = bets_api.get_bet365_inplay_filter({                        
                "sport_id": r_sport_id,                                          
                "page": events_page
            })
                                                                                 
            bets_api_service.sync_upcoming_events_pre_match_odds(upcoming_events)

    