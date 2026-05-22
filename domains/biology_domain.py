from domains.base import DomainAdapter

class BiologyAdapter(DomainAdapter):
    """
    Biological Domain Adapter applying the Tri-Regime Model of Biological Energy Handling.
    Maps high-level biological metrics to specific capacity bottlenecks.
    """
    def map_to_engine(self, data):
        # 1. Energy Input (Chlorophyll-like, Nutrient/Light capture)
        light_or_food = data.get("energy_availability", 0.8) # 0-1
        absorption_eff = data.get("absorption_efficiency", 0.9)
        c_input = max(light_or_food * absorption_eff, 0.01)

        # 2. Electron Transport (Magnetite-like, Redox chain)
        mitochondrial_health = data.get("mitochondrial_health", 0.8)
        c_electron = max(mitochondrial_health, 0.01)

        # 3. Proton Transport (Water-like, Ion gradients)
        membrane_integrity = data.get("membrane_integrity", 0.9)
        c_proton = max(membrane_integrity, 0.01)

        # 4. Energy Stabilization (Melanin-like, Antioxidants)
        antioxidant_capacity = data.get("antioxidant_capacity", 0.5)
        c_stability = max(antioxidant_capacity, 0.01)

        # Engine phi (Flow) is driven by input
        phi = c_input
        
        # Engine C (Constraint) is the inverse of combined transport and stability
        # A bottleneck in transport or low stability increases systemic constraint
        combined_transport = (c_electron * c_proton)
        effective_S = 1.0 / c_stability
        C = max((effective_S / combined_transport) * 0.1, 0.01)

        # Store explicit Tri-Regime capacities for interpretation
        self.last_capacities = {
            "C_input": c_input,
            "C_electron": c_electron,
            "C_proton": c_proton,
            "C_stability": c_stability
        }

        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        
        # If the engine supports life_number in meta, use it
        lam = state.meta.get("life_number", None)
        
        if lam is not None:
            if lam < 1.0:
                return "System decay — throughput cannot sustain maintenance (Λ < 1)"
            elif lam < 1.5:
                return "Borderline survival — proto-biological or highly stressed state (Λ ≈ 1)"
            else:
                return f"Sustained biological life (Λ = {lam:.2f})"
        
        # Fallback to Psi
        if psi < 0.3:  return "Cell/organism death — system below viability threshold"
        if psi < 0.6:  return "Stressed biological system — resource or transport bottleneck"
        if psi <= 1.2: return "Healthy biological equilibrium"
        return "Uncontrolled growth — tumorigenic or invasive risk"
