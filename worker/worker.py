import redis
import time
import os
import signal
import sys

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
_redis_password = os.environ.get("REDIS_PASSWORD")
_redis_kwargs = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "decode_responses": False,
}
if _redis_password:
    _redis_kwargs["password"] = _redis_password

r = redis.Redis(**_redis_kwargs)
_running = True


def _stop(*_args):
    global _running
    _running = False


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


def main():
    while _running:
        job = r.brpop("job", timeout=5)
        if job:
            _, job_id = job
            process_job(job_id.decode())
    sys.exit(0)


if __name__ == "__main__":
    main()
