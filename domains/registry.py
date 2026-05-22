class DomainRegistry:
    def __init__(self):
        self.domains = {}

    def register(self, name, adapter):
        self.domains[name] = adapter

    def get(self, name):
        if name not in self.domains:
            return None
        return self.domains[name]

    def list_domains(self):
        return list(self.domains.keys())

    @classmethod
    def default(cls):
        registry = cls()

        # ── Original five ─────────────────────────────────────────────────────
        from domains.medicine       import MedicineAdapter
        from domains.physics_domain import PhysicsAdapter
        from domains.society        import SocietyAdapter
        from domains.economics      import EconomicsAdapter
        from domains.cosmos         import CosmosAdapter
        registry.register("medicine",   MedicineAdapter())
        registry.register("physics",    PhysicsAdapter())
        registry.register("society",    SocietyAdapter())
        registry.register("economics",  EconomicsAdapter())
        registry.register("cosmos",     CosmosAdapter())
        from domains.sports_markets import SportsMarketsAdapter
        registry.register("sports_markets", SportsMarketsAdapter())

        # ── Medicine & Health ─────────────────────────────────────────────────
        from domains.nephrology          import NephrologyAdapter
        from domains.cardiology          import CardiologyAdapter
        from domains.oncology            import OncologyAdapter
        from domains.neurology           import NeurologyAdapter
        from domains.endocrinology       import EndocrinologyAdapter
        from domains.pulmonology         import PulmonologyAdapter
        from domains.infectious_disease  import InfectiousDiseaseAdapter
        from domains.haematology         import HaematologyAdapter
        from domains.gastroenterology    import GastroenterologyAdapter
        from domains.hepatology          import HepatologyAdapter
        from domains.rheumatology        import RheumatologyAdapter
        from domains.dermatology         import DermatologyAdapter
        from domains.ophthalmology       import OphthalmologyAdapter
        from domains.psychiatry          import PsychiatryAdapter
        from domains.paediatrics         import PaediatricsAdapter
        from domains.obstetrics          import ObstetricsAdapter
        from domains.geriatrics          import GeriatricsAdapter
        from domains.surgery             import SurgeryAdapter
        from domains.emergency_medicine  import EmergencyMedicineAdapter
        from domains.epidemiology        import EpidemiologyAdapter
        from domains.pharmacology        import PharmacologyAdapter
        from domains.nutrition           import NutritionAdapter
        from domains.sports_medicine     import SportsMedicineAdapter
        from domains.immunology          import ImmunologyAdapter
        from domains.radiology           import RadiologyAdapter
        from domains.pathology           import PathologyAdapter
        from domains.anaesthesia         import AnaesthesiaAdapter
        from domains.urology             import UrologyAdapter
        from domains.orthopaedics        import OrthopaedicsAdapter
        from domains.neurosurgery        import NeurosurgeryAdapter
        from domains.dentistry           import DentistryAdapter
        from domains.otolaryngology      import OtolaryngologyAdapter
        from domains.rehabilitation      import RehabilitationAdapter
        from domains.palliative_care     import PalliativeCareAdapter
        from domains.neonatology         import NeonatologyAdapter
        from domains.toxicology          import ToxicologyAdapter
        from domains.sleep_medicine      import SleepMedicineAdapter
        from domains.forensic_medicine   import ForensicMedicineAdapter
        from domains.nuclear_medicine    import NuclearMedicineAdapter
        registry.register("nephrology",         NephrologyAdapter())
        registry.register("cardiology",         CardiologyAdapter())
        registry.register("oncology",           OncologyAdapter())
        registry.register("neurology",          NeurologyAdapter())
        registry.register("endocrinology",      EndocrinologyAdapter())
        registry.register("pulmonology",        PulmonologyAdapter())
        registry.register("infectious_disease", InfectiousDiseaseAdapter())
        registry.register("haematology",        HaematologyAdapter())
        registry.register("gastroenterology",   GastroenterologyAdapter())
        registry.register("hepatology",         HepatologyAdapter())
        registry.register("rheumatology",       RheumatologyAdapter())
        registry.register("dermatology",        DermatologyAdapter())
        registry.register("ophthalmology",      OphthalmologyAdapter())
        registry.register("psychiatry",         PsychiatryAdapter())
        registry.register("paediatrics",        PaediatricsAdapter())
        registry.register("obstetrics",         ObstetricsAdapter())
        registry.register("geriatrics",         GeriatricsAdapter())
        registry.register("surgery",            SurgeryAdapter())
        registry.register("emergency_medicine", EmergencyMedicineAdapter())
        registry.register("epidemiology",       EpidemiologyAdapter())
        registry.register("pharmacology",       PharmacologyAdapter())
        registry.register("nutrition",          NutritionAdapter())
        registry.register("sports_medicine",    SportsMedicineAdapter())
        registry.register("immunology",         ImmunologyAdapter())
        registry.register("radiology",          RadiologyAdapter())
        registry.register("pathology",          PathologyAdapter())
        registry.register("anaesthesia",        AnaesthesiaAdapter())
        registry.register("urology",            UrologyAdapter())
        registry.register("orthopaedics",       OrthopaedicsAdapter())
        registry.register("neurosurgery",       NeurosurgeryAdapter())
        registry.register("dentistry",          DentistryAdapter())
        registry.register("otolaryngology",     OtolaryngologyAdapter())
        registry.register("rehabilitation",     RehabilitationAdapter())
        registry.register("palliative_care",    PalliativeCareAdapter())
        registry.register("neonatology",        NeonatologyAdapter())
        registry.register("toxicology",         ToxicologyAdapter())
        registry.register("sleep_medicine",     SleepMedicineAdapter())
        registry.register("forensic_medicine",  ForensicMedicineAdapter())
        registry.register("nuclear_medicine",   NuclearMedicineAdapter())

        # ── Natural Sciences ──────────────────────────────────────────────────
        from domains.chemistry_domain    import ChemistryAdapter
        from domains.biology_domain      import BiologyAdapter
        from domains.evolution_domain    import EvolutionAdapter
        from domains.genetics            import GeneticsAdapter
        from domains.neuroscience        import NeuroscienceAdapter
        from domains.ecology             import EcologyAdapter
        from domains.climate             import ClimateAdapter
        from domains.geology             import GeologyAdapter
        from domains.astrophysics        import AstrophysicsAdapter
        from domains.optics              import OpticsAdapter
        from domains.acoustics           import AcousticsAdapter
        from domains.thermodynamics      import ThermodynamicsAdapter
        from domains.fluid_dynamics      import FluidDynamicsAdapter
        from domains.condensed_matter    import CondensedMatterAdapter
        from domains.nuclear_physics     import NuclearPhysicsAdapter
        from domains.plasma_physics      import PlasmaPhysicsAdapter
        from domains.materials_science   import MaterialsScienceAdapter
        from domains.quantum_mechanics   import QuantumMechanicsAdapter
        from domains.electromagnetism    import ElectromagnetismAdapter
        from domains.oceanography        import OceanographyAdapter
        from domains.atmospheric_science import AtmosphericScienceAdapter
        from domains.hydrology           import HydrologyAdapter
        from domains.seismology          import SeismologyAdapter
        from domains.volcanology         import VolcanologyAdapter
        from domains.planetary_science   import PlanetaryScienceAdapter
        from domains.biophysics          import BiophysicsAdapter
        from domains.physical_chemistry  import PhysicalChemistryAdapter
        from domains.computational_physics import ComputationalPhysicsAdapter
        registry.register("chemistry",             ChemistryAdapter())
        registry.register("biology",               BiologyAdapter())
        registry.register("evolution",             EvolutionAdapter())
        registry.register("genetics",              GeneticsAdapter())
        registry.register("neuroscience",          NeuroscienceAdapter())
        registry.register("ecology",               EcologyAdapter())
        registry.register("climate",               ClimateAdapter())
        registry.register("geology",               GeologyAdapter())
        registry.register("astrophysics",          AstrophysicsAdapter())
        registry.register("optics",                OpticsAdapter())
        registry.register("acoustics",             AcousticsAdapter())
        registry.register("thermodynamics",        ThermodynamicsAdapter())
        registry.register("fluid_dynamics",        FluidDynamicsAdapter())
        registry.register("condensed_matter",      CondensedMatterAdapter())
        registry.register("nuclear_physics",       NuclearPhysicsAdapter())
        registry.register("plasma_physics",        PlasmaPhysicsAdapter())
        registry.register("materials_science",     MaterialsScienceAdapter())
        registry.register("quantum_mechanics",     QuantumMechanicsAdapter())
        registry.register("electromagnetism",      ElectromagnetismAdapter())
        registry.register("oceanography",          OceanographyAdapter())
        from domains.origins_of_life import OriginsOfLifeAdapter
        registry.register("origins_of_life",     OriginsOfLifeAdapter())
        registry.register("atmospheric_science",   AtmosphericScienceAdapter())
        registry.register("hydrology",             HydrologyAdapter())
        registry.register("seismology",            SeismologyAdapter())
        registry.register("volcanology",           VolcanologyAdapter())
        registry.register("planetary_science",     PlanetaryScienceAdapter())
        registry.register("biophysics",            BiophysicsAdapter())
        registry.register("physical_chemistry",    PhysicalChemistryAdapter())
        registry.register("computational_physics", ComputationalPhysicsAdapter())

        # ── Social Sciences ───────────────────────────────────────────────────
        from domains.politics              import PoliticsAdapter
        from domains.law_domain            import LawAdapter
        from domains.education             import EducationAdapter
        from domains.psychology            import PsychologyAdapter
        from domains.linguistics           import LinguisticsAdapter
        from domains.sociology             import SociologyAdapter
        from domains.demography            import DemographyAdapter
        from domains.criminology           import CriminologyAdapter
        from domains.urban_planning        import UrbanPlanningAdapter
        from domains.public_policy         import PublicPolicyAdapter
        from domains.philosophy            import PhilosophyAdapter
        from domains.ethics                import EthicsAdapter
        from domains.media_studies         import MediaStudiesAdapter
        from domains.religious_studies     import ReligiousStudiesAdapter
        from domains.behavioral_economics  import BehavioralEconomicsAdapter
        from domains.development_economics import DevelopmentEconomicsAdapter
        registry.register("politics",              PoliticsAdapter())
        registry.register("law",                   LawAdapter())
        registry.register("education",             EducationAdapter())
        registry.register("psychology",            PsychologyAdapter())
        registry.register("linguistics",           LinguisticsAdapter())
        registry.register("sociology",             SociologyAdapter())
        registry.register("demography",            DemographyAdapter())
        registry.register("criminology",           CriminologyAdapter())
        registry.register("urban_planning",        UrbanPlanningAdapter())
        registry.register("public_policy",         PublicPolicyAdapter())
        registry.register("philosophy",            PhilosophyAdapter())
        registry.register("ethics",                EthicsAdapter())
        registry.register("media_studies",         MediaStudiesAdapter())
        registry.register("religious_studies",     ReligiousStudiesAdapter())
        registry.register("behavioral_economics",  BehavioralEconomicsAdapter())
        registry.register("development_economics", DevelopmentEconomicsAdapter())

        # ── Technology & Engineering ──────────────────────────────────────────
        from domains.energy_systems          import EnergySystemsAdapter
        from domains.networks                import NetworksAdapter
        from domains.artificial_intelligence import ArtificialIntelligenceAdapter
        from domains.cybersecurity           import CybersecurityAdapter
        from domains.robotics                import RoboticsAdapter
        from domains.semiconductors          import SemiconductorsAdapter
        from domains.telecommunications     import TelecommunicationsAdapter
        from domains.space_technology        import SpaceTechnologyAdapter
        from domains.quantum_computing       import QuantumComputingAdapter
        from domains.biotechnology           import BiotechnologyAdapter
        from domains.nanotechnology          import NanotechnologyAdapter
        from domains.nuclear_engineering     import NuclearEngineeringAdapter
        from domains.chemical_engineering    import ChemicalEngineeringAdapter
        from domains.civil_engineering       import CivilEngineeringAdapter
        from domains.electrical_engineering  import ElectricalEngineeringAdapter
        from domains.mechanical_engineering  import MechanicalEngineeringAdapter
        from domains.aerospace_engineering   import AerospaceEngineeringAdapter
        from domains.biomedical_engineering  import BiomedicalEngineeringAdapter
        from domains.environmental_engineering import EnvironmentalEngineeringAdapter
        from domains.software_engineering    import SoftwareEngineeringAdapter
        from domains.data_science            import DataScienceAdapter
        from domains.cloud_computing         import CloudComputingAdapter
        from domains.iot                     import IoTAdapter
        from domains.autonomous_vehicles     import AutonomousVehiclesAdapter
        from domains.bioinformatics          import BioinformaticsAdapter
        from domains.marine_engineering      import MarineEngineeringAdapter
        from domains.railway_engineering     import RailwayEngineeringAdapter
        from domains.construction            import ConstructionAdapter
        import importlib
        _tdp = importlib.import_module("domains.3d_printing")
        ThreeDPrintingAdapter = _tdp.ThreeDPrintingAdapter
        registry.register("energy_systems",           EnergySystemsAdapter())
        registry.register("networks",                 NetworksAdapter())
        registry.register("artificial_intelligence",  ArtificialIntelligenceAdapter())
        registry.register("cybersecurity",            CybersecurityAdapter())
        registry.register("robotics",                 RoboticsAdapter())
        registry.register("semiconductors",           SemiconductorsAdapter())
        registry.register("telecommunications",       TelecommunicationsAdapter())
        registry.register("space_technology",         SpaceTechnologyAdapter())
        registry.register("quantum_computing",        QuantumComputingAdapter())
        registry.register("biotechnology",            BiotechnologyAdapter())
        registry.register("nanotechnology",           NanotechnologyAdapter())
        registry.register("nuclear_engineering",      NuclearEngineeringAdapter())
        registry.register("chemical_engineering",     ChemicalEngineeringAdapter())
        registry.register("civil_engineering",        CivilEngineeringAdapter())
        registry.register("electrical_engineering",   ElectricalEngineeringAdapter())
        registry.register("mechanical_engineering",   MechanicalEngineeringAdapter())
        registry.register("aerospace_engineering",    AerospaceEngineeringAdapter())
        registry.register("biomedical_engineering",   BiomedicalEngineeringAdapter())
        registry.register("environmental_engineering",EnvironmentalEngineeringAdapter())
        registry.register("software_engineering",     SoftwareEngineeringAdapter())
        registry.register("data_science",             DataScienceAdapter())
        registry.register("cloud_computing",          CloudComputingAdapter())
        registry.register("iot",                      IoTAdapter())
        registry.register("autonomous_vehicles",      AutonomousVehiclesAdapter())
        registry.register("bioinformatics",           BioinformaticsAdapter())
        registry.register("marine_engineering",       MarineEngineeringAdapter())
        registry.register("railway_engineering",      RailwayEngineeringAdapter())
        registry.register("construction",             ConstructionAdapter())
        registry.register("3d_printing",              ThreeDPrintingAdapter())

        # ── Geopolitics & Conflict ────────────────────────────────────────────
        from domains.empire            import EmpireAdapter
        from domains.urban_growth      import UrbanGrowthAdapter
        from domains.civil_war         import CivilWarAdapter
        from domains.interstate_war    import InterstateWarAdapter
        from domains.trade_routes      import TradeRoutesAdapter
        from domains.migration         import MigrationAdapter
        from domains.geopolitics       import GeopoliticsAdapter
        from domains.diplomacy         import DiplomacyAdapter
        from domains.sanctions         import SanctionsAdapter
        from domains.terrorism         import TerrorismAdapter
        from domains.peacekeeping      import PeacekeepingAdapter
        from domains.espionage         import EspionageAdapter
        from domains.propaganda        import PropagandaAdapter
        from domains.nuclear_deterrence import NuclearDeterrenceAdapter
        from domains.hybrid_warfare    import HybridWarfareAdapter
        from domains.information_warfare import InformationWarfareAdapter
        from domains.economic_warfare  import EconomicWarfareAdapter
        from domains.revolution        import RevolutionAdapter
        from domains.international_law import InternationalLawAdapter
        from domains.refugee_crisis    import RefugeeCrisisAdapter
        registry.register("empire",              EmpireAdapter())
        registry.register("urban_growth",        UrbanGrowthAdapter())
        registry.register("civil_war",           CivilWarAdapter())
        registry.register("interstate_war",      InterstateWarAdapter())
        registry.register("trade_routes",        TradeRoutesAdapter())
        registry.register("migration",           MigrationAdapter())
        registry.register("geopolitics",         GeopoliticsAdapter())
        registry.register("diplomacy",           DiplomacyAdapter())
        registry.register("sanctions",           SanctionsAdapter())
        registry.register("terrorism",           TerrorismAdapter())
        registry.register("peacekeeping",        PeacekeepingAdapter())
        registry.register("espionage",           EspionageAdapter())
        registry.register("propaganda",          PropagandaAdapter())
        registry.register("nuclear_deterrence",  NuclearDeterrenceAdapter())
        registry.register("hybrid_warfare",      HybridWarfareAdapter())
        registry.register("information_warfare", InformationWarfareAdapter())
        registry.register("economic_warfare",    EconomicWarfareAdapter())
        registry.register("revolution",          RevolutionAdapter())
        registry.register("international_law",   InternationalLawAdapter())
        registry.register("refugee_crisis",      RefugeeCrisisAdapter())

        # ── Earth & Environment ───────────────────────────────────────────────
        from domains.marine_biology     import MarineBiologyAdapter
        from domains.coral_reefs        import CoralReefsAdapter
        from domains.fresh_water_ecology import FreshwaterEcologyAdapter
        from domains.forest_ecology     import ForestEcologyAdapter
        from domains.desert_ecology     import DesertEcologyAdapter
        from domains.arctic_ecology     import ArcticEcologyAdapter
        from domains.biodiversity       import BiodiversityAdapter
        from domains.conservation       import ConservationAdapter
        from domains.invasive_species   import InvasiveSpeciesAdapter
        from domains.wildfire           import WildfireAdapter
        from domains.drought            import DroughtAdapter
        from domains.flooding           import FloodingAdapter
        from domains.pollution          import PollutionAdapter
        from domains.deforestation      import DeforestationAdapter
        from domains.water_scarcity     import WaterScarcityAdapter
        from domains.soil_degradation   import SoilDegradationAdapter
        registry.register("marine_biology",     MarineBiologyAdapter())
        registry.register("coral_reefs",        CoralReefsAdapter())
        registry.register("freshwater_ecology", FreshwaterEcologyAdapter())
        registry.register("forest_ecology",     ForestEcologyAdapter())
        registry.register("desert_ecology",     DesertEcologyAdapter())
        registry.register("arctic_ecology",     ArcticEcologyAdapter())
        registry.register("biodiversity",       BiodiversityAdapter())
        registry.register("conservation",       ConservationAdapter())
        registry.register("invasive_species",   InvasiveSpeciesAdapter())
        registry.register("wildfire",           WildfireAdapter())
        registry.register("drought",            DroughtAdapter())
        registry.register("flooding",           FloodingAdapter())
        registry.register("pollution",          PollutionAdapter())
        registry.register("deforestation",      DeforestationAdapter())
        registry.register("water_scarcity",     WaterScarcityAdapter())
        registry.register("soil_degradation",   SoilDegradationAdapter())

        # ── History & Civilisation ────────────────────────────────────────────
        from domains.archaeology         import ArchaeologyAdapter
        from domains.anthropology        import AnthropologyAdapter
        from domains.prehistory          import PrehistoryAdapter
        from domains.ancient_civilisations import AncientCivilisationsAdapter
        from domains.medieval_history    import MedievalHistoryAdapter
        from domains.early_modern        import EarlyModernAdapter
        from domains.industrial_age      import IndustrialAgeAdapter
        from domains.modern_history      import ModernHistoryAdapter
        from domains.postcolonial        import PostcolonialAdapter
        from domains.cultural_heritage   import CulturalHeritageAdapter
        from domains.oral_history        import OralHistoryAdapter
        from domains.historiography      import HistoriographyAdapter
        from domains.cartography         import CartographyAdapter
        from domains.numismatics         import NumismaticsAdapter
        registry.register("archaeology",           ArchaeologyAdapter())
        registry.register("anthropology",          AnthropologyAdapter())
        registry.register("prehistory",            PrehistoryAdapter())
        registry.register("ancient_civilisations", AncientCivilisationsAdapter())
        registry.register("medieval_history",      MedievalHistoryAdapter())
        registry.register("early_modern",          EarlyModernAdapter())
        registry.register("industrial_age",        IndustrialAgeAdapter())
        registry.register("modern_history",        ModernHistoryAdapter())
        registry.register("postcolonial",          PostcolonialAdapter())
        registry.register("cultural_heritage",     CulturalHeritageAdapter())
        registry.register("oral_history",          OralHistoryAdapter())
        registry.register("historiography",        HistoriographyAdapter())
        registry.register("cartography",           CartographyAdapter())
        registry.register("numismatics",           NumismaticsAdapter())

        # ── Arts & Culture ────────────────────────────────────────────────────
        from domains.music             import MusicAdapter
        from domains.visual_arts       import VisualArtsAdapter
        from domains.literature        import LiteratureAdapter
        from domains.architecture_arts import ArchitectureArtsAdapter
        from domains.folklore          import FolkloreAdapter
        from domains.mythology         import MythologyAdapter
        from domains.performing_arts   import PerformingArtsAdapter
        from domains.digital_arts      import DigitalArtsAdapter
        registry.register("music",             MusicAdapter())
        registry.register("visual_arts",       VisualArtsAdapter())
        registry.register("literature",        LiteratureAdapter())
        registry.register("architecture_arts", ArchitectureArtsAdapter())
        registry.register("folklore",          FolkloreAdapter())
        registry.register("mythology",         MythologyAdapter())
        registry.register("performing_arts",   PerformingArtsAdapter())
        registry.register("digital_arts",      DigitalArtsAdapter())

        # ── Philosophy & Cognition ────────────────────────────────────────────
        from domains.logic              import LogicAdapter
        from domains.epistemology       import EpistemologyAdapter
        from domains.ethics_theory      import EthicsTheoryAdapter
        from domains.consciousness      import ConsciousnessAdapter
        from domains.decision_theory    import DecisionTheoryAdapter
        from domains.game_theory        import GameTheoryAdapter
        from domains.information_theory import InformationTheoryAdapter
        from domains.cognitive_science  import CognitiveScienceAdapter
        from domains.philosophy_of_mind import PhilosophyOfMindAdapter
        from domains.complexity_theory  import ComplexityTheoryAdapter
        registry.register("logic",              LogicAdapter())
        registry.register("epistemology",       EpistemologyAdapter())
        registry.register("ethics_theory",      EthicsTheoryAdapter())
        registry.register("consciousness",      ConsciousnessAdapter())
        registry.register("decision_theory",    DecisionTheoryAdapter())
        registry.register("game_theory",        GameTheoryAdapter())
        registry.register("information_theory", InformationTheoryAdapter())
        registry.register("cognitive_science",  CognitiveScienceAdapter())
        registry.register("philosophy_of_mind", PhilosophyOfMindAdapter())
        registry.register("complexity_theory",  ComplexityTheoryAdapter())

        # ── Agriculture & Food ────────────────────────────────────────────────
        from domains.crop_science   import CropScienceAdapter
        from domains.livestock      import LivestockAdapter
        from domains.aquaculture    import AquacultureAdapter
        from domains.food_security  import FoodSecurityAdapter
        from domains.soil_health    import SoilHealthAdapter
        from domains.irrigation     import IrrigationAdapter
        from domains.agroforestry   import AgroforestryAdapter
        from domains.urban_farming  import UrbanFarmingAdapter
        from domains.famine_risk    import FamineRiskAdapter
        registry.register("crop_science",  CropScienceAdapter())
        registry.register("livestock",     LivestockAdapter())
        registry.register("aquaculture",   AquacultureAdapter())
        registry.register("food_security", FoodSecurityAdapter())
        registry.register("soil_health",   SoilHealthAdapter())
        registry.register("irrigation",    IrrigationAdapter())
        registry.register("agroforestry",  AgroforestryAdapter())
        registry.register("urban_farming", UrbanFarmingAdapter())
        registry.register("famine_risk",   FamineRiskAdapter())

        return registry
