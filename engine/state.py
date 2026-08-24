import numpy as np
try:
    import h5py
except ImportError:
    h5py = None

from engine.config import DEFAULT_NX, DEFAULT_NY, DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_GAMMA, HISTORY_WINDOW

class State:
    def __init__(self, nx=DEFAULT_NX, ny=DEFAULT_NY):
        self.nx = nx
        self.ny = ny
        # Primary dynamic fields
        self.phi = np.ones((nx, ny), dtype=float)
        self.C = np.ones((nx, ny), dtype=float)
        self.S = np.ones((nx, ny), dtype=float)   # Surface responsiveness (2D Field)
        self.Ms = np.ones((nx, ny), dtype=float)  # Structural memory (2D Field)
        self.psi_s = (self.phi / self.C) * self.S * self.Ms
        self.dpsi_dt = np.zeros((nx, ny), dtype=float)  # Rate of change of Operating Ratio

        self.J = 1.0   # Flux Capacity Threshold
        self.chi = 137.036 # Aspect Ratio Lever (Mujjabi Attractor)

        # Chirality (Racemic Initialization with stochastic noise)
        self.C_L = 0.5 * np.ones((nx, ny), dtype=float) + np.random.normal(0, 0.01, (nx, ny))
        self.C_D = 0.5 * np.ones((nx, ny), dtype=float) + np.random.normal(0, 0.01, (nx, ny))

        # Energy Storage (Phosphate Quantization)
        self.stored_energy = np.zeros((nx, ny), dtype=float)

        # Spatial Tensor Parameters (Adaptive Flux Limitation)
        self.alpha = np.full((nx, ny), DEFAULT_ALPHA, dtype=float)
        self.beta = np.full((nx, ny), DEFAULT_BETA, dtype=float)
        self.gamma = np.full((nx, ny), DEFAULT_GAMMA, dtype=float)

        self.t = 0.0
        self.history = []
        # Diagnostics: life_number, throughput_J, OOL tri-regime (ool_C_input, ool_sigma_e, ool_sigma_p, ool_S_stability)
        self.meta = {}


    def save_h5(self, filepath):
        if h5py is None:
            raise ImportError("h5py is required to save HDF5 checkpoints.")
        with h5py.File(filepath, 'w') as f:
            # Metadata attributes
            f.attrs['nx'] = self.nx
            f.attrs['ny'] = self.ny
            f.attrs['t'] = self.t
            f.attrs['J'] = self.J
            f.attrs['chi'] = self.chi
            
            # Tensor datasets
            f.create_dataset('phi', data=self.phi, compression='gzip')
            f.create_dataset('C', data=self.C, compression='gzip')
            f.create_dataset('S', data=self.S, compression='gzip')
            f.create_dataset('Ms', data=self.Ms, compression='gzip')
            f.create_dataset('C_L', data=self.C_L, compression='gzip')
            f.create_dataset('C_D', data=self.C_D, compression='gzip')
            f.create_dataset('alpha', data=self.alpha, compression='gzip')
            f.create_dataset('beta', data=self.beta, compression='gzip')
            f.create_dataset('gamma', data=self.gamma, compression='gzip')

    @classmethod
    def load_h5(cls, filepath):
        if h5py is None:
            raise ImportError("h5py is required to load HDF5 checkpoints.")
        with h5py.File(filepath, 'r') as f:
            nx = f.attrs['nx']
            ny = f.attrs['ny']
            state = cls(nx=nx, ny=ny)
            
            state.t = f.attrs['t']
            state.J = f.attrs['J']
            state.chi = f.attrs['chi']
            
            state.phi[:] = f['phi'][:]
            state.C[:] = f['C'][:]
            state.S[:] = f['S'][:]
            state.Ms[:] = f['Ms'][:]
            state.C_L[:] = f['C_L'][:]
            state.C_D[:] = f['C_D'][:]
            state.alpha[:] = f['alpha'][:]
            state.beta[:] = f['beta'][:]
            state.gamma[:] = f['gamma'][:]
            
            state.update_psi()
            return state

    def snapshot(self):
        """Returns a full, high-fidelity copy of the state tensors."""
        self.update_psi()
        return {
            "t": self.t,
            "phi": self.phi.copy(),
            "C": self.C.copy(),
            "S": self.S.copy(),
            "Ms": self.Ms.copy(),
            "J": self.J,
            "chi": self.chi,
            "C_L": self.C_L.copy(),
            "C_D": self.C_D.copy(),
            "stored_energy": self.stored_energy.copy(),
            "psi_s": self.psi_s.copy(),
            "alpha": self.alpha.copy(),
            "beta": self.beta.copy(),
            "gamma": self.gamma.copy()
        }

    def record(self):
        """Stores the full tensor snapshot in history, keeping only the last HISTORY_WINDOW entries."""
        self.history.append(self.snapshot())
        if len(self.history) > HISTORY_WINDOW:
            self.history.pop(0)

    def record_metrics(self):
        """Stores only macroscopic scalar metrics (used for ultra-long runs)."""
        self.history.append({
            "t": self.t,
            "mean_phi": float(np.mean(self.phi)),
            "mean_C": float(np.mean(self.C)),
            "mean_psi_s": self.mean_psi(),
            "max_psi_s": self.max_psi(),
            "min_psi_s": self.min_psi(),
            "mean_alpha": float(np.mean(self.alpha)),
            "mean_beta": float(np.mean(self.beta))
        })
        if len(self.history) > HISTORY_WINDOW:
            self.history.pop(0)

    def update_psi(self):
        """Synchronize Ψ_s with the current Φ/C/S/Ms fields."""
        safe_C = np.where(self.C > 1e-9, self.C, 1e-9)
        self.psi_s = (self.phi / safe_C) * self.S * self.Ms
        return self.psi_s

    def mean_psi(self):
        self.update_psi()
        return float(np.mean(self.psi_s))

    def max_psi(self):
        self.update_psi()
        return float(np.max(self.psi_s))

    def min_psi(self):
        self.update_psi()
        return float(np.min(self.psi_s))

    def regime(self):
        m = self.mean_psi()
        if m > 1.2:
            return "overload"
        if m < 0.8:
            return "constrained"
        return "stable"

    def embed_knot(self, knot_data):
        """
        Embeds a T(2,n) topological knot mass spectrum into the spatial field.
        This localizes the topological charge into the C field as constraints.
        """
        n = knot_data["n"]
        masses = knot_data["masses"]
        
        # Create n focal points of constraint (lobes)
        cx, cy = self.nx // 2, self.ny // 2
        radius = min(self.nx, self.ny) // 4
        
        for k in range(n):
            angle = 2 * np.pi * k / n
            x = int(cx + radius * np.cos(angle))
            y = int(cy + radius * np.sin(angle))
            
            if 0 <= x < self.nx and 0 <= y < self.ny:
                # Add the mass to the constraint field to anchor the knot
                self.C[x, y] += masses[k]

        # Re-evaluate equilibrium
        self.update_psi()

    def spawn_cell(self, x, y, radius, resistance, adaptation):
        """
        Spawns a biological cell.
        A cell is a localized high-constraint boundary (membrane) with a specific
        internal adaptive coefficient (alpha) and relaxation (beta).
        """
        y_indices, x_indices = np.ogrid[:self.ny, :self.nx]
        dist_from_center = np.sqrt((x_indices - x)**2 + (y_indices - y)**2)

        # Membrane (Constraint Boundary)
        membrane = (dist_from_center >= radius - 1) & (dist_from_center <= radius + 1)
        self.C[membrane] += resistance

        # Cytoplasm (Internal Adaptive Region)
        cytoplasm = dist_from_center < radius
        self.alpha[cytoplasm] = adaptation

        # Re-evaluate
        self.update_psi()

    def generate_porous_matrix(self, porosity=0.4, wall_resistance=50.0):
        """
        Generates a porous mineral matrix (Paper 4).
        Creates localized spatial constraints that prevent rapid diffusion,
        forming the first stable reaction domains for prebiotic chemistry.
        """
        # Generate stochastic spatial noise
        noise = np.random.rand(self.nx, self.ny)

        # Apply threshold to define solid mineral walls vs open pores
        walls = noise > porosity
        self.C[walls] += wall_resistance

        # Mineral walls have rigid constraints (low adaptation)
        self.alpha[walls] *= 0.1
        self.beta[walls] *= 0.1

        # Re-evaluate equilibrium
        self.update_psi()


    def apply_intervention(self, target_field, value):
        """Pearl's Do-Calculus: Intervene on a physical field directly."""
        if target_field == "phi":
            self.phi[:] = value
        elif target_field == "C":
            self.C[:] = value
        elif target_field == "phi_spike":
            self.phi[self.nx//2-2:self.nx//2+2, self.ny//2-2:self.ny//2+2] += value
        self.update_psi()

    def apply_phase_separation(self):
        """
        Liquid-Liquid Phase Separation (LLPS).
        Dynamic droplet formation driven by free energy minimization combined with
        flux optimization. Replaces static membranes before lipids evolve.
        """
        # Droplets form where Flux (J) over Lambda is locally optimized
        grad_phi_y, grad_phi_x = np.gradient(self.phi)
        safe_C = np.where(self.C > 1e-9, self.C, 1e-9)
        flux_mag = np.sqrt((grad_phi_x / safe_C)**2 + (grad_phi_y / safe_C)**2)

        flux_ratio = flux_mag / safe_C
        mean_ratio = float(np.mean(flux_ratio))

        # High flux ratio promotes condensation into droplets (increased local C due to crowding)
        droplet_mask = flux_ratio > mean_ratio * 1.2
        self.C[droplet_mask] *= 1.05

        # Surrounding continuous phase depletes
        dilute_mask = flux_ratio < mean_ratio * 0.8
        self.C[dilute_mask] = np.maximum(self.C[dilute_mask] * 0.95, 1e-9)
        self.update_psi()

    def calculate_disease_horizon(self, threshold=1.5):
        """
        Legacy compatibility helper for a toy threshold-crossing time estimate.

        This extrapolates the current simulated Psi_s slope to a caller-provided
        numerical threshold. It is not a disease forecast, prognosis, or
        clinically calibrated time-to-event model.
        """
        self.update_psi()
        self.dpsi_dt = np.where(self.psi_s > 0, self.psi_s * 0.01, 0) # Conservative fallback derivative if history not available
        
        if len(self.history) >= 2:
            prev_psi = self.history[-2]["psi_s"] if "psi_s" in self.history[-2] else self.psi_s
            previous_t = self.history[-2].get("t", self.history[-2].get("time", self.t - 0.01))
            dt = self.t - previous_t
            if dt > 0:
                self.dpsi_dt = (self.psi_s - prev_psi) / dt
                
        # Calculate horizon where dpsi_dt > 0 and Psi_s < threshold
        with np.errstate(divide='ignore', invalid='ignore'):
            t_col = np.where((self.dpsi_dt > 1e-5) & (self.psi_s < threshold), 
                             (threshold - self.psi_s) / self.dpsi_dt, 
                             np.inf)
            
        self.meta["t_collapse_min"] = float(np.min(t_col))
        finite = t_col[np.isfinite(t_col)]
        self.meta["t_collapse_mean"] = float(np.mean(finite)) if finite.size else float("inf")
        self.meta["toy_horizon_status"] = "uncalibrated simulated threshold-crossing estimate"
        return t_col
