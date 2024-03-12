import os
import time
import schedule
import threading

from dotenv import load_dotenv
from betsapi import BetsApiService

load_dotenv()


# create a thread for every class function
# save the response

# bets_api_service = BetsApiService()
# bets_api_service.save_bet365_inplay();

# Define a function that will be executed by each thread
# def thread_function(name):
#     print(f"Thread {name} starting...")
#     time.sleep(2)
#     print(f"Thread {name} ending...")
#
#
# if __name__ == "__main__":
#     # Create and start multiple threads
#     threads = []
#     for i in range(5):
#         thread = threading.Thread(target=thread_function, args=(i,))
#         threads.append(thread)
#         thread.start()
#
#     # Wait for all threads to complete
#     for thread in threads:
#         thread.join()
#
#     print("All threads have finished execution.")
