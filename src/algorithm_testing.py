import json
from Algorithmia.errors import ApiError, AlgorithmException
from time import sleep


def call_algo(algo, payload, timeout=None):
    try:
        if timeout:
            result = algo.set_options(timeout=timeout).pipe(payload).result
        else:
            result = algo.pipe(payload).result
        return result
    except Exception as e:
        return e


def algorithm_publish(algo, payload):
    try:
        algo.publish(
            settings={"algorithm_callability": "private"},
            version_info={
                "release_notes": "created programmatically",
                "sample_input": json.dumps(payload),
                "version_type": "minor"
            }
        )
        print(f"algorithm {algo.username}/{algo.algoname} published")
        return algo
    except ApiError as e:
        if "Version already published" in str(e):
            print(f"algorithm {algo.username}/{algo.algoname} already published")
            return algo
        else:
            raise e

def algorithm_test(algo, payload):
    try:
        algo_info = algo.info()
        latest_hash = algo_info.version_info.git_hash
        algo.url = f"/v1/algo/{algo.username}/{algo.algoname}/{latest_hash}"
        result = call_algo(algo, payload)
        if isinstance(result, Exception):
            raise result
        print(f"testing for algorithm {algo.username}/{algo.algoname}/{latest_hash} complete")
        return algo
    except AlgorithmException as e:
        if "version hash" in str(e):
            sleep(1)
            algorithm_test(algo, payload)
            return algo
        else:
            raise e