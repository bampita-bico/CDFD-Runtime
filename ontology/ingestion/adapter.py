import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime

class DataIngestionAdapter:
    """
    Extract-Transform-Load (ETL) layer.
    Translates messy external JSON/CSV/SQL data into CDFD DSL parameters,
    preserving exact provenance and lineage.
    """
    def __init__(self):
        self.schema_mappings = {}

    def register_mapping(self, source_type: str, mapping_rules: Dict[str, str]):
        """
        Example: register_mapping('sensor_json', {'temp_k': 'phi', 'friction': 'C'})
        """
        self.schema_mappings[source_type] = mapping_rules

    def ingest_json(self, payload: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Parses JSON array and extracts Phi and C variables.
        """
        data = json.loads(payload)
        if not isinstance(data, list):
            data = [data]
            
        results = []
        timestamp = datetime.utcnow().isoformat()
        
        for idx, record in enumerate(data):
            # In a real system, we'd use registered schema mappings.
            # Here we dynamically look for flux/constraint keywords
            phi_val = record.get("flow", record.get("flux", record.get("phi", 1.0)))
            c_val = record.get("resistance", record.get("friction", record.get("constraint", record.get("c", 1.0))))
            name = record.get("id", record.get("name", f"{source_id}_{idx}"))
            
            # Map into the CDFD format that DSL or Engine expects
            results.append({
                "name": name,
                "phi": float(phi_val),
                "C": float(c_val),
                "provenance": {
                    "source": source_id,
                    "timestamp": timestamp,
                    "raw_record": record
                }
            })
        return results

    def ingest_csv(self, csv_string: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Parses a CSV string and extracts Phi and C.
        """
        import io
        reader = csv.DictReader(io.StringIO(csv_string))
        results = []
        timestamp = datetime.utcnow().isoformat()
        
        for idx, row in enumerate(reader):
            phi_val = row.get("flow", row.get("flux", row.get("phi", 1.0)))
            c_val = row.get("resistance", row.get("friction", row.get("constraint", row.get("c", 1.0))))
            name = row.get("id", row.get("name", f"{source_id}_{idx}"))
            
            results.append({
                "name": name,
                "phi": float(phi_val),
                "C": float(c_val),
                "provenance": {
                    "source": source_id,
                    "timestamp": timestamp,
                    "raw_record": row
                }
            })
        return results
