from engine.state import State
from engine.kernel import Kernel
from engine.physics import run, step
from engine.self_regulation import SelfRegulator, RegulationParams
from engine.cross_scale import CrossScaleCoupler, build_scale_stack
from engine.temporal_memory import TemporalMemory
from engine.bifurcation import map_phase, regime_summary
from engine.field_geometry import FieldGraph, make_chain, make_ring, make_star
from engine.emergence import emergence_report
from engine.causal_graph import build_causal_graph
from engine.attractor import attractor_report, detect_attractor
from engine.information_flow import information_report, mutual_information
from engine.quantum_vacuum import QuantumVacuum
from engine.seismology import apply_seismology
from engine.epigenetics import apply_epigenetics
from engine.atmospheric import apply_atmospheric
from engine.crystallography import apply_crystallography
from engine.psychoacoustics import apply_psychoacoustics
from engine.volcanology import apply_volcanology
