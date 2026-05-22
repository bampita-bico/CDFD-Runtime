from domains.base import DomainAdapter
class OralHistoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        recording_rate   = data.get("recording_rate_norm", 0.4)
        speaker_availability = data.get("elder_speaker_availability", 0.5)
        community_support    = data.get("community_support", 0.5)
        generational_loss    = data.get("generational_transmission_loss", 0.3)
        technology_access    = data.get("technology_access", 0.6)
        phi = max(recording_rate*0.3 + speaker_availability*0.3 + community_support*0.2 + technology_access*0.2, 0.01)
        C   = max(generational_loss*0.6 + (1.0-speaker_availability)*0.4, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Oral histories being lost — no speakers or recording capacity"
        if psi < 0.6:  return "Oral tradition threatened — transmission chain weakening"
        if psi <= 1.2: return "Oral history preserved — recording and transmission active"
        return "Vibrant oral tradition — well-documented and living in community"
