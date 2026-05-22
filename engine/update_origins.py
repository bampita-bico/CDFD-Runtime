import re
import os

os.chdir('/home/bampita/Projects/CDFD/engine')

with open('origins_of_life.py', 'r') as f:
    content = f.read()

# Replace the update_tri_regime_channels return dictionary and assignments
# We will inject C_electron, C_proton, and C_stability into the meta dict.
old_meta_assign = r"""    m[META_OOL_PREFIX + "C_input"] = c_input
    m[META_OOL_PREFIX + "C_input"] = c_input
    m[META_OOL_PREFIX + "sigma_e"] = sigma_e_mean
    m[META_OOL_PREFIX + "sigma_p"] = sigma_p
    m[META_OOL_PREFIX + "S_stability"] = S_stability
    m[META_OOL_PREFIX + "transport_factor"] = transport_factor

    return {
        "C_input": c_input,
        "C_input": c_input,
        "sigma_e": sigma_e_mean,
        "sigma_p": sigma_p,
        "S_stability": S_stability,
    }"""

new_meta_assign = r"""    # Map to weakest-link capacity notation (C_i)
    c_electron = sigma_e_mean
    c_proton = sigma_p
    c_stability = 1.0 / S_stability

    # Weakest-link throughput bound
    j_max = min(c_input, c_electron, c_proton, c_stability)

    m[META_OOL_PREFIX + "C_input"] = c_input
    m[META_OOL_PREFIX + "C_input"] = c_input
    m[META_OOL_PREFIX + "C_electron"] = c_electron
    m[META_OOL_PREFIX + "C_proton"] = c_proton
    m[META_OOL_PREFIX + "C_stability"] = c_stability
    m[META_OOL_PREFIX + "sigma_e"] = sigma_e_mean
    m[META_OOL_PREFIX + "sigma_p"] = sigma_p
    m[META_OOL_PREFIX + "S_stability"] = S_stability
    m[META_OOL_PREFIX + "transport_factor"] = transport_factor
    m[META_OOL_PREFIX + "J_max"] = j_max

    return {
        "C_input": c_input,
        "C_input": c_input,
        "C_electron": c_electron,
        "C_proton": c_proton,
        "C_stability": c_stability,
        "J_max": j_max,
        "sigma_e": sigma_e_mean,
        "sigma_p": sigma_p,
        "S_stability": S_stability,
    }"""

content = content.replace(old_meta_assign, new_meta_assign)

old_compute = r"""    lam = (ci * se * sp * TAU_RELAX) / (S * E_MAINTENANCE + 1e-15)
    state.meta["life_number"] = lam"""

new_compute = r"""    # Equivalently: lam = (ci * c_electron * c_proton * TAU_RELAX) / (S * E_MAINTENANCE + 1e-15)
    lam = (ci * se * sp * TAU_RELAX) / (S * E_MAINTENANCE + 1e-15)
    state.meta["life_number"] = lam"""

content = content.replace(old_compute, new_compute)

with open('origins_of_life.py', 'w') as f:
    f.write(content)
