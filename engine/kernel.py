"""Orchestrator — coordinates all modules, enforces error isolation, maintains temporal coherence."""
import json
import logging
import time

import numpy as np
from engine.config import DEFAULT_DT, LOG_FAILURES
from engine.physics import step as apply_physics, update_psi
from ontology.engine import CDFLOntologyEngine

logger = logging.getLogger(__name__)


class Kernel:
    def __init__(self, dt=DEFAULT_DT,
                 use_chemistry=False, use_biology=False,
                 use_evolution=False, use_cosmos=False,
                 use_intelligence=False, use_medicine=False, use_ecology=False,
                 use_self_regulation=False, use_temporal_memory=False,
                 use_civilization=False, use_economics=False,
                 use_trade_hubs=False, use_infrastructure=False,
                 use_networks=False, use_social=False,
                 use_language_spread=False, use_religion=False,
                 use_climate=False, use_conflict=False,
                 use_governance=False, use_technology=False,
                 use_epidemiology=False, use_finance=False,
                 use_media=False, use_population_genetics=False,
                 use_climate_civilization=False, use_war_economy=False,
                 use_agriculture=False, use_biodiversity=False,
                 use_collective_memory=False, use_colonialism=False,
                 use_consciousness=False, use_coral_reef=False,
                 use_deforestation=False, use_democracy=False,
                 use_demography_dynamics=False, use_development_traps=False,
                 use_food_web=False, use_forest_dynamics=False,
                 use_galaxy_dynamics=False, use_geology=False,
                 use_geopolitical_diplomacy=False, use_hydrology=False,
                 use_ideology=False, use_immune_system=False,
                 use_labor_markets=False, use_microbiome=False,
                 use_monetary_policy=False, use_neural_formation=False,
                 use_nuclear_dynamics=False, use_ocean_fisheries=False,
                 use_oceanography=False, use_organizational_dynamics=False,
                 use_particle_physics=False, use_permafrost=False,
                 use_plasma_dynamics=False, use_pollution=False,
                 use_power_grid=False, use_real_estate=False,
                 use_resource_depletion=False, use_sanctions=False,
                 use_science_paradigms=False, use_soil=False,
                 use_stellar_evolution=False, use_supply_chains=False,
                 use_symbiosis=False, use_thermodynamics_engine=False,
                 use_transportation_networks=False, use_urban_metabolism=False,
                 use_water_infrastructure=False, use_wetlands=False,
                 use_seismology=False, use_epigenetics=False,
                 use_atmospheric=False, use_crystallography=False,
                 use_psychoacoustics=False, use_volcanology=False, use_universal_ontology=False,
                 use_coherence=False, use_vpt_detector=False,
                 regulation_params=None, memory_window=50):
        self.dt = dt
        self.telemetry = {}
        self.use_chemistry = use_chemistry
        self.use_biology = use_biology
        self.use_evolution = use_evolution
        self.use_cosmos = use_cosmos
        self.use_intelligence = use_intelligence
        self.use_medicine = use_medicine
        self.use_ecology = use_ecology
        self.use_self_regulation = use_self_regulation
        self.use_temporal_memory = use_temporal_memory
        self.use_civilization = use_civilization
        self.use_economics = use_economics
        self.use_trade_hubs = use_trade_hubs
        self.use_infrastructure = use_infrastructure
        self.use_networks = use_networks
        self.use_social = use_social
        self.use_language_spread = use_language_spread
        self.use_religion = use_religion
        self.use_climate = use_climate
        self.use_conflict = use_conflict
        self.use_governance = use_governance
        self.use_technology = use_technology
        self.use_epidemiology = use_epidemiology
        self.use_finance = use_finance
        self.use_media = use_media
        self.use_population_genetics = use_population_genetics
        self.use_climate_civilization = use_climate_civilization
        self.use_war_economy = use_war_economy
        self.use_agriculture = use_agriculture
        self.use_biodiversity = use_biodiversity
        self.use_collective_memory = use_collective_memory
        self.use_colonialism = use_colonialism
        self.use_consciousness = use_consciousness
        self.use_coral_reef = use_coral_reef
        self.use_deforestation = use_deforestation
        self.use_democracy = use_democracy
        self.use_demography_dynamics = use_demography_dynamics
        self.use_development_traps = use_development_traps
        self.use_food_web = use_food_web
        self.use_forest_dynamics = use_forest_dynamics
        self.use_galaxy_dynamics = use_galaxy_dynamics
        self.use_geology = use_geology
        self.use_geopolitical_diplomacy = use_geopolitical_diplomacy
        self.use_hydrology = use_hydrology
        self.use_ideology = use_ideology
        self.use_immune_system = use_immune_system
        self.use_labor_markets = use_labor_markets
        self.use_microbiome = use_microbiome
        self.use_monetary_policy = use_monetary_policy
        self.use_neural_formation = use_neural_formation
        self.use_nuclear_dynamics = use_nuclear_dynamics
        self.use_ocean_fisheries = use_ocean_fisheries
        self.use_oceanography = use_oceanography
        self.use_organizational_dynamics = use_organizational_dynamics
        self.use_particle_physics = use_particle_physics
        self.use_permafrost = use_permafrost
        self.use_plasma_dynamics = use_plasma_dynamics
        self.use_pollution = use_pollution
        self.use_power_grid = use_power_grid
        self.use_real_estate = use_real_estate
        self.use_resource_depletion = use_resource_depletion
        self.use_sanctions = use_sanctions
        self.use_science_paradigms = use_science_paradigms
        self.use_soil = use_soil
        self.use_stellar_evolution = use_stellar_evolution
        self.use_supply_chains = use_supply_chains
        self.use_symbiosis = use_symbiosis
        self.use_thermodynamics_engine = use_thermodynamics_engine
        self.use_transportation_networks = use_transportation_networks
        self.use_urban_metabolism = use_urban_metabolism
        self.use_water_infrastructure = use_water_infrastructure
        self.use_wetlands = use_wetlands
        self.use_seismology = use_seismology
        self.use_epigenetics = use_epigenetics
        self.use_atmospheric = use_atmospheric
        self.use_crystallography = use_crystallography
        self.use_psychoacoustics = use_psychoacoustics
        self.use_volcanology = use_volcanology
        self.use_universal_ontology = use_universal_ontology
        self.ontology_engine = CDFLOntologyEngine() if use_universal_ontology else None

        self._coherence = None
        if use_coherence:
            from engine.coherence import CoherenceField
            nx, ny = 32, 32  # default; resized on first run_cycle if state differs
            self._coherence = CoherenceField(nx, ny)

        self._vpt_detector = None
        if use_vpt_detector:
            from engine.quantum_vacuum import VacuumPhaseDetector
            self._vpt_detector = VacuumPhaseDetector()

        self._regulator = None
        if use_self_regulation:
            from engine.self_regulation import SelfRegulator, RegulationParams
            p = regulation_params or RegulationParams(
                alpha=DEFAULT_DT * 10, beta=DEFAULT_DT * 5, gamma=DEFAULT_DT * 10
            )
            self._regulator = SelfRegulator(p)

        self._memory = None
        if use_temporal_memory:
            from engine.temporal_memory import TemporalMemory
            self._memory = TemporalMemory(window=memory_window)


    def save_checkpoint(self, state, filepath):
        """Saves the current state and kernel telemetry to an HDF5 file."""
        state.save_h5(filepath)
        logger.info(json.dumps({"event": "checkpoint_saved", "filepath": filepath, "t": state.t}))

    def load_checkpoint(self, filepath):
        """Loads a state from an HDF5 file."""
        from engine.state import State
        state = State.load_h5(filepath)
        logger.info(json.dumps({"event": "checkpoint_loaded", "filepath": filepath, "t": state.t}))
        self.log_telemetry(state)
        state.meta["checkpoint_loaded"] = filepath
        return state

    def log_telemetry(self, state):
        """Emits structured JSON logging for world-class telemetry."""
        if not hasattr(self, "telemetry"):
            self.telemetry = {}
        log_record = {
            "event": "step_complete",
            "t": state.t,
            "mean_psi": state.mean_psi(),
            "telemetry_ms": self.telemetry
        }
        logger.info(json.dumps(log_record))

    def run_cycle(self, state):
        active_constraints = []
        status = "ok"

        try:
            t0 = time.perf_counter()
            apply_physics(state, dt=self.dt)
            self.telemetry['physics'] = (time.perf_counter() - t0) * 1000
        except Exception as e:
            status = "physics_error"
            if LOG_FAILURES:
                logger.warning("physics update failed: %s", e)

        if self.use_chemistry:
            try:
                from engine.chemistry import apply_chemistry
                apply_chemistry(state, dt=self.dt)
                active_constraints.append("chemistry")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("chemistry failed: %s", e)

        if self.use_biology:
            try:
                from engine.biology import apply_biology
                apply_biology(state, dt=self.dt)
                active_constraints.append("biology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("biology failed: %s", e)

        if self.use_medicine:
            try:
                from engine.medicine import apply_medicine
                apply_medicine(state, dt=self.dt)
                active_constraints.append("medicine")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("medicine failed: %s", e)

        if self.use_ecology:
            try:
                from engine.ecology import apply_ecology
                apply_ecology(state, dt=self.dt)
                active_constraints.append("ecology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("ecology failed: %s", e)

        if self.use_evolution:
            try:
                from engine.evolution import apply_evolution
                apply_evolution(state, dt=self.dt)
                active_constraints.append("evolution")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("evolution failed: %s", e)

        if self.use_intelligence:
            try:
                from engine.intelligence import apply_intelligence
                apply_intelligence(state, dt=self.dt)
                active_constraints.append("intelligence")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("intelligence failed: %s", e)

        if self.use_cosmos:
            try:
                from engine.cosmos import apply_cosmos
                apply_cosmos(state, dt=self.dt)
                active_constraints.append("cosmos")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("cosmos failed: %s", e)

        if self.use_civilization:
            try:
                from engine.civilization import apply_civilization
                apply_civilization(state, dt=self.dt)
                active_constraints.append("civilization")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("civilization failed: %s", e)

        if self.use_economics:
            try:
                from engine.economics import apply_economics
                apply_economics(state, dt=self.dt)
                active_constraints.append("economics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("economics failed: %s", e)

        if self.use_trade_hubs:
            try:
                from engine.trade_hubs import apply_trade_hubs
                apply_trade_hubs(state, dt=self.dt)
                active_constraints.append("trade_hubs")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("trade_hubs failed: %s", e)

        if self.use_infrastructure:
            try:
                from engine.infrastructure import apply_infrastructure
                apply_infrastructure(state, dt=self.dt)
                active_constraints.append("infrastructure")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("infrastructure failed: %s", e)

        if self.use_networks:
            try:
                from engine.networks import apply_networks
                apply_networks(state, dt=self.dt)
                active_constraints.append("networks")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("networks failed: %s", e)

        if self.use_social:
            try:
                from engine.social import apply_social
                apply_social(state, dt=self.dt)
                active_constraints.append("social")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("social failed: %s", e)

        if self.use_language_spread:
            try:
                from engine.language_spread import apply_language_spread
                apply_language_spread(state, dt=self.dt)
                active_constraints.append("language_spread")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("language_spread failed: %s", e)

        if self.use_religion:
            try:
                from engine.religion import apply_religion
                apply_religion(state, dt=self.dt)
                active_constraints.append("religion")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("religion failed: %s", e)

        if self.use_climate:
            try:
                from engine.climate import apply_climate
                apply_climate(state, dt=self.dt)
                active_constraints.append("climate")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("climate failed: %s", e)

        if self.use_conflict:
            try:
                from engine.conflict import apply_conflict
                apply_conflict(state, dt=self.dt)
                active_constraints.append("conflict")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("conflict failed: %s", e)

        if self.use_governance:
            try:
                from engine.governance import apply_governance
                apply_governance(state, dt=self.dt)
                active_constraints.append("governance")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("governance failed: %s", e)

        if self.use_technology:
            try:
                from engine.technology import apply_technology
                apply_technology(state, dt=self.dt)
                active_constraints.append("technology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("technology failed: %s", e)

        if self.use_epidemiology:
            try:
                from engine.epidemiology import apply_epidemiology
                apply_epidemiology(state, dt=self.dt)
                active_constraints.append("epidemiology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("epidemiology failed: %s", e)

        if self.use_finance:
            try:
                from engine.finance import apply_finance
                apply_finance(state, dt=self.dt)
                active_constraints.append("finance")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("finance failed: %s", e)

        if self.use_media:
            try:
                from engine.media import apply_media
                apply_media(state, dt=self.dt)
                active_constraints.append("media")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("media failed: %s", e)

        if self.use_population_genetics:
            try:
                from engine.population_genetics import apply_population_genetics
                apply_population_genetics(state, dt=self.dt)
                active_constraints.append("population_genetics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("population_genetics failed: %s", e)

        if self.use_climate_civilization:
            try:
                from engine.climate_civilization import apply_climate_civilization
                apply_climate_civilization(state, dt=self.dt)
                active_constraints.append("climate_civilization")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("climate_civilization failed: %s", e)

        if self.use_war_economy:
            try:
                from engine.war_economy import apply_war_economy
                apply_war_economy(state, dt=self.dt)
                active_constraints.append("war_economy")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("war_economy failed: %s", e)

        if self.use_agriculture:
            try:
                from engine.agriculture import apply_agriculture
                apply_agriculture(state, dt=self.dt)
                active_constraints.append("agriculture")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("agriculture failed: %s", e)

        if self.use_biodiversity:
            try:
                from engine.biodiversity import apply_biodiversity
                apply_biodiversity(state, dt=self.dt)
                active_constraints.append("biodiversity")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("biodiversity failed: %s", e)

        if self.use_collective_memory:
            try:
                from engine.collective_memory import apply_collective_memory
                apply_collective_memory(state, dt=self.dt)
                active_constraints.append("collective_memory")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("collective_memory failed: %s", e)

        if self.use_colonialism:
            try:
                from engine.colonialism import apply_colonialism
                apply_colonialism(state, dt=self.dt)
                active_constraints.append("colonialism")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("colonialism failed: %s", e)

        if self.use_consciousness:
            try:
                from engine.consciousness import apply_consciousness
                apply_consciousness(state, dt=self.dt)
                active_constraints.append("consciousness")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("consciousness failed: %s", e)

        if self.use_coral_reef:
            try:
                from engine.coral_reef import apply_coral_reef
                apply_coral_reef(state, dt=self.dt)
                active_constraints.append("coral_reef")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("coral_reef failed: %s", e)

        if self.use_deforestation:
            try:
                from engine.deforestation import apply_deforestation
                apply_deforestation(state, dt=self.dt)
                active_constraints.append("deforestation")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("deforestation failed: %s", e)

        if self.use_democracy:
            try:
                from engine.democracy import apply_democracy
                apply_democracy(state, dt=self.dt)
                active_constraints.append("democracy")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("democracy failed: %s", e)

        if self.use_demography_dynamics:
            try:
                from engine.demography_dynamics import apply_demography_dynamics
                apply_demography_dynamics(state, dt=self.dt)
                active_constraints.append("demography_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("demography_dynamics failed: %s", e)

        if self.use_development_traps:
            try:
                from engine.development_traps import apply_development_traps
                apply_development_traps(state, dt=self.dt)
                active_constraints.append("development_traps")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("development_traps failed: %s", e)

        if self.use_food_web:
            try:
                from engine.food_web import apply_food_web
                apply_food_web(state, dt=self.dt)
                active_constraints.append("food_web")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("food_web failed: %s", e)

        if self.use_forest_dynamics:
            try:
                from engine.forest_dynamics import apply_forest_dynamics
                apply_forest_dynamics(state, dt=self.dt)
                active_constraints.append("forest_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("forest_dynamics failed: %s", e)

        if self.use_galaxy_dynamics:
            try:
                from engine.galaxy_dynamics import apply_galaxy_dynamics
                apply_galaxy_dynamics(state, dt=self.dt)
                active_constraints.append("galaxy_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("galaxy_dynamics failed: %s", e)

        if self.use_geology:
            try:
                from engine.geology import apply_geology
                apply_geology(state, dt=self.dt)
                active_constraints.append("geology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("geology failed: %s", e)

        if self.use_geopolitical_diplomacy:
            try:
                from engine.geopolitical_diplomacy import apply_geopolitical_diplomacy
                apply_geopolitical_diplomacy(state, dt=self.dt)
                active_constraints.append("geopolitical_diplomacy")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("geopolitical_diplomacy failed: %s", e)

        if self.use_hydrology:
            try:
                from engine.hydrology import apply_hydrology
                apply_hydrology(state, dt=self.dt)
                active_constraints.append("hydrology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("hydrology failed: %s", e)

        if self.use_ideology:
            try:
                from engine.ideology import apply_ideology
                apply_ideology(state, dt=self.dt)
                active_constraints.append("ideology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("ideology failed: %s", e)

        if self.use_immune_system:
            try:
                from engine.immune_system import apply_immune_system
                apply_immune_system(state, dt=self.dt)
                active_constraints.append("immune_system")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("immune_system failed: %s", e)

        if self.use_labor_markets:
            try:
                from engine.labor_markets import apply_labor_markets
                apply_labor_markets(state, dt=self.dt)
                active_constraints.append("labor_markets")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("labor_markets failed: %s", e)

        if self.use_microbiome:
            try:
                from engine.microbiome import apply_microbiome
                apply_microbiome(state, dt=self.dt)
                active_constraints.append("microbiome")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("microbiome failed: %s", e)

        if self.use_monetary_policy:
            try:
                from engine.monetary_policy import apply_monetary_policy
                apply_monetary_policy(state, dt=self.dt)
                active_constraints.append("monetary_policy")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("monetary_policy failed: %s", e)

        if self.use_neural_formation:
            try:
                from engine.neural_formation import apply_neural_formation
                apply_neural_formation(state, dt=self.dt)
                active_constraints.append("neural_formation")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("neural_formation failed: %s", e)

        if self.use_nuclear_dynamics:
            try:
                from engine.nuclear_dynamics import apply_nuclear_dynamics
                apply_nuclear_dynamics(state, dt=self.dt)
                active_constraints.append("nuclear_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("nuclear_dynamics failed: %s", e)

        if self.use_ocean_fisheries:
            try:
                from engine.ocean_fisheries import apply_ocean_fisheries
                apply_ocean_fisheries(state, dt=self.dt)
                active_constraints.append("ocean_fisheries")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("ocean_fisheries failed: %s", e)

        if self.use_oceanography:
            try:
                from engine.oceanography import apply_oceanography
                apply_oceanography(state, dt=self.dt)
                active_constraints.append("oceanography")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("oceanography failed: %s", e)

        if self.use_organizational_dynamics:
            try:
                from engine.organizational_dynamics import apply_organizational_dynamics
                apply_organizational_dynamics(state, dt=self.dt)
                active_constraints.append("organizational_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("organizational_dynamics failed: %s", e)

        if self.use_particle_physics:
            try:
                from engine.particle_physics import apply_particle_physics
                apply_particle_physics(state, dt=self.dt)
                active_constraints.append("particle_physics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("particle_physics failed: %s", e)

        if self.use_permafrost:
            try:
                from engine.permafrost import apply_permafrost
                apply_permafrost(state, dt=self.dt)
                active_constraints.append("permafrost")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("permafrost failed: %s", e)

        if self.use_plasma_dynamics:
            try:
                from engine.plasma_dynamics import apply_plasma_dynamics
                apply_plasma_dynamics(state, dt=self.dt)
                active_constraints.append("plasma_dynamics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("plasma_dynamics failed: %s", e)

        if self.use_pollution:
            try:
                from engine.pollution import apply_pollution
                apply_pollution(state, dt=self.dt)
                active_constraints.append("pollution")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("pollution failed: %s", e)

        if self.use_power_grid:
            try:
                from engine.power_grid import apply_power_grid
                apply_power_grid(state, dt=self.dt)
                active_constraints.append("power_grid")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("power_grid failed: %s", e)

        if self.use_real_estate:
            try:
                from engine.real_estate import apply_real_estate
                apply_real_estate(state, dt=self.dt)
                active_constraints.append("real_estate")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("real_estate failed: %s", e)

        if self.use_resource_depletion:
            try:
                from engine.resource_depletion import apply_resource_depletion
                apply_resource_depletion(state, dt=self.dt)
                active_constraints.append("resource_depletion")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("resource_depletion failed: %s", e)

        if self.use_sanctions:
            try:
                from engine.sanctions import apply_sanctions
                apply_sanctions(state, dt=self.dt)
                active_constraints.append("sanctions")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("sanctions failed: %s", e)

        if self.use_science_paradigms:
            try:
                from engine.science_paradigms import apply_science_paradigms
                apply_science_paradigms(state, dt=self.dt)
                active_constraints.append("science_paradigms")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("science_paradigms failed: %s", e)

        if self.use_soil:
            try:
                from engine.soil import apply_soil
                apply_soil(state, dt=self.dt)
                active_constraints.append("soil")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("soil failed: %s", e)

        if self.use_stellar_evolution:
            try:
                from engine.stellar_evolution import apply_stellar_evolution
                apply_stellar_evolution(state, dt=self.dt)
                active_constraints.append("stellar_evolution")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("stellar_evolution failed: %s", e)

        if self.use_supply_chains:
            try:
                from engine.supply_chains import apply_supply_chains
                apply_supply_chains(state, dt=self.dt)
                active_constraints.append("supply_chains")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("supply_chains failed: %s", e)

        if self.use_symbiosis:
            try:
                from engine.symbiosis import apply_symbiosis
                apply_symbiosis(state, dt=self.dt)
                active_constraints.append("symbiosis")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("symbiosis failed: %s", e)

        if self.use_thermodynamics_engine:
            try:
                from engine.thermodynamics_engine import apply_thermodynamics_engine
                apply_thermodynamics_engine(state, dt=self.dt)
                active_constraints.append("thermodynamics_engine")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("thermodynamics_engine failed: %s", e)

        if self.use_transportation_networks:
            try:
                from engine.transportation_networks import apply_transportation_networks
                apply_transportation_networks(state, dt=self.dt)
                active_constraints.append("transportation_networks")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("transportation_networks failed: %s", e)

        if self.use_urban_metabolism:
            try:
                from engine.urban_metabolism import apply_urban_metabolism
                apply_urban_metabolism(state, dt=self.dt)
                active_constraints.append("urban_metabolism")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("urban_metabolism failed: %s", e)

        if self.use_water_infrastructure:
            try:
                from engine.water_infrastructure import apply_water_infrastructure
                apply_water_infrastructure(state, dt=self.dt)
                active_constraints.append("water_infrastructure")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("water_infrastructure failed: %s", e)

        if self.use_wetlands:
            try:
                from engine.wetlands import apply_wetlands
                apply_wetlands(state, dt=self.dt)
                active_constraints.append("wetlands")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("wetlands failed: %s", e)

        if self.use_seismology:
            try:
                from engine.seismology import apply_seismology
                apply_seismology(state, dt=self.dt)
                active_constraints.append("seismology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("seismology failed: %s", e)

        if self.use_epigenetics:
            try:
                from engine.epigenetics import apply_epigenetics
                apply_epigenetics(state, dt=self.dt)
                active_constraints.append("epigenetics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("epigenetics failed: %s", e)

        if self.use_atmospheric:
            try:
                from engine.atmospheric import apply_atmospheric
                apply_atmospheric(state, dt=self.dt)
                active_constraints.append("atmospheric")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("atmospheric failed: %s", e)

        if self.use_crystallography:
            try:
                from engine.crystallography import apply_crystallography
                apply_crystallography(state, dt=self.dt)
                active_constraints.append("crystallography")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("crystallography failed: %s", e)

        if self.use_psychoacoustics:
            try:
                from engine.psychoacoustics import apply_psychoacoustics
                apply_psychoacoustics(state, dt=self.dt)
                active_constraints.append("psychoacoustics")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("psychoacoustics failed: %s", e)

        if self.use_volcanology:
            try:
                from engine.volcanology import apply_volcanology
                apply_volcanology(state, dt=self.dt)
                active_constraints.append("volcanology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("volcanology failed: %s", e)


        # Dynamic Domain Loading via Universal Ontology
        active_domains = state.meta.get("active_domains", [])
        if self.ontology_engine:
            for domain_key in active_domains:
                # The ontology engine automatically loads the domain process
                # and evaluates its mathematical constraints.
                process = self.ontology_engine.instantiate_domain(domain_key)
                if process:
                    # In a full implementation, we would extract Phi/C from the grid
                    # For now, we simulate the topological check
                    active_constraints.append(domain_key)
                    
            try:
                anomalies = self.ontology_engine.step(self.dt, state)
                if anomalies:
                    state.meta["ontology_anomalies"] = anomalies
                active_constraints.append("universal_ontology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning(f"Universal ontology failed: {e}")

        try:
            update_psi(state)
        except Exception as e:
            if LOG_FAILURES:
                logger.warning("psi synchronization failed: %s", e)

        if self.use_temporal_memory and self._memory is not None:
            try:
                self._memory.record(state)
                self._memory.apply(state)
                update_psi(state)
                active_constraints.append("temporal_memory")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("temporal_memory failed: %s", e)

        if self.use_self_regulation and self._regulator is not None:
            try:
                self._regulator.regulate(state)
                active_constraints.append("self_regulation")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("self_regulation failed: %s", e)


        # Dynamic Domain Loading via Universal Ontology
        active_domains = state.meta.get("active_domains", [])
        if self.ontology_engine:
            for domain_key in active_domains:
                # The ontology engine automatically loads the domain process
                # and evaluates its mathematical constraints.
                process = self.ontology_engine.instantiate_domain(domain_key)
                if process:
                    # In a full implementation, we would extract Phi/C from the grid
                    # For now, we simulate the topological check
                    active_constraints.append(domain_key)
                    
            try:
                anomalies = self.ontology_engine.step(self.dt, state)
                if anomalies:
                    state.meta["ontology_anomalies"] = anomalies
                active_constraints.append("universal_ontology")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning(f"Universal ontology failed: {e}")

        if self._coherence is not None:
            try:
                # Resize coherence field if state dimensions differ
                nx, ny = state.phi.shape
                if self._coherence.Omega.shape != (nx, ny):
                    from engine.coherence import CoherenceField
                    self._coherence = CoherenceField(nx, ny)
                self._coherence.update(state, self.dt)
                if hasattr(state, "meta") and isinstance(state.meta, dict):
                    state.meta["coherence"] = self._coherence.mean_coherence()
                    state.meta["coherence_efficiency"] = self._coherence.coherence_efficiency(state)
                active_constraints.append("coherence")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("coherence update failed: %s", e)

        if self._vpt_detector is not None:
            try:
                vpt_triggered = self._vpt_detector.check(state)
                si = self._vpt_detector.stability_index(state)
                if hasattr(state, "meta") and isinstance(state.meta, dict):
                    state.meta["stability_index"] = si
                    state.meta["vpt_triggered"] = vpt_triggered
                if vpt_triggered:
                    active_constraints.append("vpt")
            except Exception as e:
                if LOG_FAILURES:
                    logger.warning("vpt detector failed: %s", e)

        try:
            update_psi(state)
        except Exception as e:
            if LOG_FAILURES:
                logger.warning("final psi synchronization failed: %s", e)

        # state.t is already incremented by apply_physics(state, dt)

        memory_summary = self._memory.summary() if self._memory else None
        regulation_status = (self._regulator.status(state)
                             if self._regulator else None)

        return {
            "state": state,
            "equilibrium_psi_s": state.mean_psi(),
            "status": status,
            "active_constraints": active_constraints,
            "memory": memory_summary,
            "regulation": regulation_status,
        }

    def run(self, state, steps):
        """Run `steps` cycles and return scalar time series for CLI and web visualization."""
        history = []
        for _ in range(steps):
            try:
                result = self.run_cycle(state)
                psi_s = result["equilibrium_psi_s"]
                history.append({
                    "t": float(state.t),
                    "psi": psi_s,
                    "psi_s": psi_s,
                    "phi": float(np.mean(state.phi)),
                    "C": float(np.mean(state.C)),
                    "S": float(np.mean(state.S)),
                    "Ms": float(np.mean(state.Ms)),
                    "regime": state.regime(),
                    "status": result["status"],
                })
            except Exception:
                continue
        return history
