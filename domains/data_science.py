from domains.base import DomainAdapter

class DataScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        data_volume_norm = data.get("data_volume_norm", 0.6)
        model_performance= data.get("model_performance", 0.7)
        data_quality     = data.get("data_quality", 0.7)
        missing_data     = data.get("missing_data_fraction", 0.1)
        phi = max(data_volume_norm * 0.3 + model_performance * 0.4 + data_quality * 0.3, 0.01)
        C   = max(missing_data * 0.5 + (1.0 - data_quality) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Data pipeline broken — missing or corrupt data, models failing"
        if psi < 0.6:  return "Limited insights — data quality constraining analysis"
        if psi <= 1.2: return "Data science functioning — reliable insights being generated"
        return "High-value analytics — clean data, accurate models, actionable insights"
