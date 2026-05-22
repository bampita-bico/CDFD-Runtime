from domains.base import DomainAdapter

class BioinformaticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        sequence_coverage= data.get("sequence_coverage_norm", 0.7)
        annotation_quality = data.get("annotation_quality", 0.6)
        noise_fraction   = data.get("sequencing_error_rate", 0.01)
        database_completeness = data.get("database_completeness", 0.7)
        phi = max(sequence_coverage * 0.4 + annotation_quality * 0.3 + database_completeness * 0.3, 0.01)
        C   = max(noise_fraction * 0.5 + (1.0 - annotation_quality) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Analysis unreliable — coverage or annotation insufficient"
        if psi < 0.6:  return "Incomplete genomic picture — gaps limiting discovery"
        if psi <= 1.2: return "Reliable bioinformatics pipeline — good coverage and annotation"
        return "High-quality genomic analysis — deep coverage, complete annotation"
