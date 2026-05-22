import os
import importlib
import inspect
import logging
from typing import TYPE_CHECKING, Dict, Any, Optional
from ontology.runtime.graph_mechanics import OntologyGraph
from ontology.runtime.relationship_prop import RelationshipPropagator
from ontology.runtime.regime_tagging import RegimeTagger
from ontology.runtime.personalization import PersonalizationManager
from ontology.meta.process import Process
from ontology.meta.entity import Entity

if TYPE_CHECKING:
    from engine.state import State

logger = logging.getLogger(__name__)

class CDFLOntologyEngine:
    """
    The Universal Semantic Nervous System.
    Wraps the raw numeric CDFD State and provides native reasoning across all domains.
    """
    _registry: Dict[str, type] = {}

    def __init__(self):
        self.graph = OntologyGraph()
        self.p13n_manager = PersonalizationManager()
        self.propagator = RelationshipPropagator(self.graph, self.p13n_manager)
        self.tagger = RegimeTagger(self.graph)
        self.step_count = 0
        self.active_processes: Dict[str, Process] = {}
        
        if not self._registry:
            self.build_registry()

    @classmethod
    def build_registry(cls):
        """
        Dynamically imports all Process subclasses from the ontology packages.
        """
        base_dir = os.path.dirname(__file__)
        categories = ['abstract', 'applied', 'biology_medicine', 'commerce', 'cosmos', 
                      'earth', 'economic', 'engineered', 'music', 'origins_of_life', 'physics', 'socioeconomic']
        
        for category in categories:
            cat_path = os.path.join(base_dir, category)
            if not os.path.exists(cat_path):
                continue
                
            for file_name in os.listdir(cat_path):
                if file_name.endswith('.py') and file_name != '__init__.py':
                    module_name = file_name[:-3]
                    full_module_path = f"ontology.{category}.{module_name}"
                    
                    try:
                        module = importlib.import_module(full_module_path)
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, Process) and obj is not Process:
                                cls._registry[module_name] = obj
                    except Exception as e:
                        logger.debug(f"Failed to import {full_module_path}: {e}")
        
        logger.info(f"[Ontology] Registry built. Loaded {len(cls._registry)} domains.")

    @classmethod
    def register_discovered_type(cls, name: str, process_class: type):
        """
        Hook for the CDFD Runtime discovery layer to inject candidate schemas.
        """
        cls._registry[name] = process_class
        logger.info(f"[Ontology Engine] Registered AUTONOMOUS SCHEMA: {name}")

    def instantiate_domain(self, domain_key: str) -> Optional[Process]:
        if domain_key in self._registry:
            if domain_key not in self.active_processes:
                process_class = self._registry[domain_key]
                self.active_processes[domain_key] = process_class()
            return self.active_processes[domain_key]
        return None

    def evaluate_semantic_node(self, domain_key: str, node_id: str, phi: float, c: float, s: float = 1.0, ms: float = 1.0) -> str:
        """
        Used by the DSL to quickly evaluate a specific mathematical state against a domain ontology.
        """
        process = self.instantiate_domain(domain_key)
        
        if process and getattr(process, "is_discovered", False):
            # If it's an invented schema, it overrides standard semantic labels
            regime_prefix = f"*[DISCOVERED]* {process.name} -> "
        else:
            regime_prefix = f"[{domain_key.upper()}] Node '{node_id}' evaluating -> "
        
        if c <= 0: c = 1e-6
        psi_s = (phi / c) * s * ms
        
        if psi_s < 1.0:
            regime = "Decay/Necrosis/Collapse"
        elif abs(psi_s - 1.0) < 0.1:
            regime = "Stable/Critical Equilibrium"
        else:
            regime = "Over-flux/Growth/Hyperinflation"
            
        return regime_prefix + regime

    def sync_from_state(self, numeric_state: 'State'):
        pass

    def step(self, dt: float, numeric_state: 'State'):
        self.step_count += 1
        self.sync_from_state(numeric_state)
        anomalies = self.tagger.detect_anomalies()
        return anomalies
