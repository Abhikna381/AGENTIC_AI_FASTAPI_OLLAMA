from rq import SimpleWorker
from rq.timeouts import BaseDeathPenalty
from dotenv import load_dotenv
from RAG_QUEUE.client.rq_client import queue, redis_conn

load_dotenv()


# ✅ Disable timeout system completely (Windows fix)
class NoOpTimeout(BaseDeathPenalty):
    def setup_death_penalty(self):
        pass

    def cancel_death_penalty(self):
        pass


if __name__ == "__main__":
    worker = SimpleWorker([queue], connection=redis_conn)

    # 🔥 override timeout handler
    worker.death_penalty_class = NoOpTimeout

    print("✅ SimpleWorker running...")
    worker.work(
        with_scheduler=False,
        burst=False,
        logging_level="INFO"
    )