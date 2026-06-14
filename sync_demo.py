import time
from timeit import default_timer as timer



def run_task(name,seconds):
    print(f"Task {name} starts at: {timer():.2f} seconds")
    time.sleep(seconds) # Blocking sleep, simulating a long-running task
    print(f"Task {name} completes at: {timer():.2f} seconds")



start = timer()
run_task("A", 2)
run_task("B", 1)
run_task("C", 3)
print(f'Total time taken: {timer() - start:.2f} seconds')