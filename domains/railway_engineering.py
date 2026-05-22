from domains.base import DomainAdapter
class RailwayEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        track_quality    = data.get("track_quality_norm", 0.7)
        train_speed_norm = data.get("train_speed_norm", 0.6)
        punctuality      = data.get("punctuality_index", 0.8)
        infrastructure_age = data.get("infrastructure_age_norm", 0.3)
        incident_rate    = data.get("incident_rate_norm", 0.05)
        phi = max(track_quality*0.3 + train_speed_norm*0.3 + punctuality*0.4, 0.01)
        C   = max(infrastructure_age*0.5 + incident_rate*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Railway system failing — track or safety incidents critical"
        if psi < 0.6:  return "Railway degraded — ageing infrastructure reducing reliability"
        if psi <= 1.2: return "Railway system functional — reliable and punctual service"
        return "World-class railway — high speed, punctual, excellent safety record"
