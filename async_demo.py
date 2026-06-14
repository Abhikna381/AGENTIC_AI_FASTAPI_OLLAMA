import asyncio
from timeit import default_timer as timer


async def run_task(name,seconds):
    print(f"Task {name} starts at: {timer():.2f} seconds")
    await asyncio.sleep(seconds) # Non-blocking sleep
    print(f"Task {name} completes at: {timer():.2f} seconds")



async def main():
    start = timer()
    await asyncio.gather(
        run_task("A", 2),
        run_task("B", 1),
        run_task("C", 3)
    )
    print(f'Total time taken: {timer() - start:.2f} seconds')

if __name__ == "__main__":
    asyncio.run(main()) 