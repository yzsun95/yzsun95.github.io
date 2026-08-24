import json
import multiprocessing
import os
import sys
import traceback
from datetime import datetime, timezone


DEFAULT_AUTHOR = {
    "name": "Yizhong Sun",
    "citedby": 0,
    "publications": {},
}


def load_author(scholar_id):
    from scholarly import scholarly

    author = scholarly.search_author_id(scholar_id)
    if not author:
        raise RuntimeError(f"No Google Scholar profile found for {scholar_id}")

    scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
    author["publications"] = {
        publication["author_pub_id"]: publication
        for publication in author.get("publications", [])
        if publication.get("author_pub_id")
    }
    return author


def fallback_author(error):
    author = DEFAULT_AUTHOR.copy()
    author["error"] = str(error)
    author["source"] = "fallback"
    return author


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False)


def fetch_worker(scholar_id, queue):
    try:
        queue.put(("ok", load_author(scholar_id)))
    except Exception:
        queue.put(("error", traceback.format_exc()))


def load_author_with_timeout(scholar_id, timeout_seconds):
    if timeout_seconds <= 0:
        return load_author(scholar_id)

    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=fetch_worker, args=(scholar_id, queue))
    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join(5)
        raise TimeoutError(
            f"Google Scholar fetch exceeded {timeout_seconds} seconds"
        )

    if queue.empty():
        raise RuntimeError(f"Google Scholar fetch exited with code {process.exitcode}")

    status, payload = queue.get()
    if status == "ok":
        return payload
    raise RuntimeError(payload)


def main():
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID", "HS_-OPIAAAAJ")
    timeout_seconds = int(os.environ.get("GOOGLE_SCHOLAR_TIMEOUT_SECONDS", "90"))
    os.makedirs("results", exist_ok=True)

    try:
        author = load_author_with_timeout(scholar_id, timeout_seconds)
        shield_message = str(author.get("citedby", 0))
    except Exception as error:
        print(f"Google Scholar fetch failed: {error}", file=sys.stderr)
        author = fallback_author(error)
        shield_message = "unavailable"

    author["updated"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(author, indent=2, ensure_ascii=False))
    write_json("results/gs_data.json", author)
    write_json(
        "results/gs_data_shieldsio.json",
        {
            "schemaVersion": 1,
            "label": "citations",
            "message": shield_message,
        },
    )


if __name__ == "__main__":
    main()
