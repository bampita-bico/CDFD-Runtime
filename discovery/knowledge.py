class KnowledgeBase:
    def __init__(self):
        self._records = []

    def append(self, params, pattern, features):
        self._records.append({
            "params": params,
            "pattern": pattern,
            "features": features,
        })

    def query(self, pattern=None):
        if pattern is None:
            return list(self._records)
        return [r for r in self._records if r["pattern"] == pattern]

    def all_patterns(self):
        return list({r["pattern"] for r in self._records})

    def __len__(self):
        return len(self._records)

    def ingest_results(self, experiment_results, detector_fn, feature_fn):
        for res in experiment_results:
            if res["error"] or not res["history"]:
                continue
            pattern = detector_fn(res["history"])
            features = feature_fn(res["history"])
            self.append(res["params"], pattern, features)
