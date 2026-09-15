"""Compare captured queue semantics; output observations, never A7 acceptance."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

FIELDS = ('method', 'site', 'event', 'job_name', 'kwargs_hash', 'status')

def semantic(snapshot):
    return {
        'workers_count': len(snapshot['workers']),
        'queues': {
            name: {
                'jobs': sorted(collections.Counter(
                    json.dumps({field: job[field] for field in FIELDS}, sort_keys=True)
                    for job in value['jobs']).items()),
                'registries': {key: len(ids) for key, ids in value['registries'].items()},
            }
            for name, value in snapshot['queues'].items()
        },
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build1', type=Path)
    parser.add_argument('build2', type=Path)
    args = parser.parse_args()
    result = {'kind': 'A7_SEMANTIC_COMPARISON_NOT_ACCEPTANCE', 'builds': {},
              'ignored_fields': ['job_id', 'enqueued_at', 'rq_keys', 'worker_names'],
              'origin': 'UNKNOWN in snapshots; source/history explanation is separate',
              'limitations': ['Registry cardinalities compared; full registry payloads not captured',
                              'Three discrete samples do not prove continuous quiescence']}
    normalized = []
    for label, path in [('build1', args.build1), ('build2', args.build2)]:
        samples = [path / f'queue-{i}.json' for i in (1,2,3)]
        raw = [json.loads(p.read_text()) for p in samples]
        norms = [semantic(s) for s in raw]
        stable = all(n == norms[0] for n in norms)
        result['builds'][label] = {
            'sample_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in samples},
            'samples_semantically_equal': stable,
            'raw_samples_equal': all(s == raw[0] for s in raw),
            'normalized': norms[0],
        }
        normalized.append(norms[0])
    result['builds_semantically_equal'] = normalized[0] == normalized[1]
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
