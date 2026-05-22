from domains.base import DomainAdapter

class MedicineAdapter(DomainAdapter):
    """
    Medical Domain Adapter applying the Tri-Regime Model of Biological Energy Handling.
    Evaluates patient health as a constraint-limited flow system.
    """
    def map_to_engine(self, patient):
        # 1. Energy Input (Chlorophyll-like: intake and supply)
        # Driven by glucose and oxygen availability (Hb)
        hb = patient.get("Hb", 12)
        glucose = patient.get("glucose", 5.5)
        c_input = max(hb * 0.5 + glucose * 0.1, 0.01)

        # 2. Electron Transport (Magnetite-like: metabolic/mitochondrial efficiency)
        # Lowered by insulin resistance
        insulin_r = patient.get("insulin_resistance", 1.0)
        c_electron = max(5.0 / (insulin_r + 0.1), 0.01)

        # 3. Proton Transport (Water-like: perfusion and filtration)
        # Driven by eGFR and blood pressure
        egfr = patient.get("eGFR", 60)
        bp = patient.get("bp", 120)
        c_proton = max((egfr / 100.0) * (120.0 / bp), 0.01)

        # 4. Energy Stabilization (Melanin-like: antioxidant/buffering capacity)
        # Lowered by toxic accumulation (e.g. high phosphate)
        phosphate = patient.get("phosphate", 1.0)
        c_stability = max(5.0 / (phosphate + 0.1), 0.01)

        # Engine phi (Flow) is driven by input
        phi = c_input
        
        # Engine C (Constraint) is the inverse of combined transport and stability
        combined_transport = (c_electron * c_proton)
        effective_S = 1.0 / c_stability
        C = max((effective_S / combined_transport) * 10.0, 0.01)

        self.last_capacities = {
            "C_input": c_input,
            "C_electron": c_electron,
            "C_proton": c_proton,
            "C_stability": c_stability
        }

        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        lam = state.meta.get("life_number", None)
        
        if lam is not None:
            if lam < 1.0:
                return "Critical organ/system failure — throughput cannot sustain basal maintenance (Λ < 1)"
            elif lam < 1.5:
                return "Highly stressed metabolic state — borderline viability (Λ ≈ 1)"
            else:
                return f"Stable physiological function (Λ = {lam:.2f})"
                
        # Fallback to Psi
        if psi < 0.8:
            return "degenerative disease — Ψ below stability threshold"
        if psi > 1.2:
            return "overload state — system under excessive stress"
        return "stable"

    def evolve(self, state, dt=0.01):
        psi = state.mean_psi()
        if psi < 0.5:
            state.phi *= (1.0 - 0.001 * dt)
