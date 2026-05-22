from domains.base import DomainAdapter


class SocietyAdapter(DomainAdapter):
    def map_to_engine(self, society):
        phi = society.get("migration_rate", 1.0)
        C = society.get("policy_restriction", 1.0)
        return max(phi, 0.01), max(C, 0.01)

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.7:
            return "societal collapse risk — flow severely constrained"
        if psi > 1.3:
            return "unstable growth — insufficient constraint structure"
        return "stable society"
