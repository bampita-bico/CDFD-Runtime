from domains.base import DomainAdapter

class SoftwareEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        code_quality     = data.get("code_quality_norm", 0.7)
        test_coverage    = data.get("test_coverage", 0.6)
        technical_debt   = data.get("technical_debt_norm", 0.3)
        bug_density      = data.get("bug_density_norm", 0.15)
        phi = max(code_quality * 0.5 + test_coverage * 0.5, 0.01)
        C   = max(technical_debt * 0.5 + bug_density * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Software collapse — technical debt and bugs unmanageable"
        if psi < 0.6:  return "Poor software health — development velocity stalled"
        if psi <= 1.2: return "Healthy codebase — maintainable and tested"
        return "Excellent engineering — clean, well-tested, low debt"
