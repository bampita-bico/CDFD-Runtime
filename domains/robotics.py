from domains.base import DomainAdapter

class RoboticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        autonomy_level   = data.get("autonomy_level", 0.5)
        sensor_accuracy  = data.get("sensor_accuracy", 0.7)
        actuator_failure = data.get("actuator_failure_rate", 0.05)
        task_complexity  = data.get("task_complexity", 0.5)
        phi = max(autonomy_level * 0.5 + sensor_accuracy * 0.5, 0.01)
        C   = max(actuator_failure * 0.4 + task_complexity * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Robot failure — sensors or actuators unable to handle task"
        if psi < 0.6:  return "Limited autonomy - frequent human-oversight flag"
        if psi <= 1.2: return "Functional robot — completing assigned tasks reliably"
        return "High-performance autonomous system — exceeding task demands"
