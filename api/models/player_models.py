from decimal import Decimal
from schemas.player_schema import PlayerProfileSchema

class PlayerProfileModel:
    # init
    def __init__(
        self,
        player_name: str,
        breed: str,
        adopter_profile: dict,
        hunger: float,
        happiness: float,
        energy: float,
        health: float,
        trust: float,
        avg_days_in_shelter: float,
        personality_type: str,
        temperament: str,
        energy_level: float,
        trainability: float,
        grooming_frequency: float,
        weight_gain_risk: float,
        exercise_needs: float,
        affectionate: int,
        stranger_friendly: int
    ):
        self.player_name=player_name
        self.breed=breed
        self.adopter_profile=adopter_profile
        self.hunger=hunger
        self.happiness=happiness
        self.energy=energy
        self.health=health
        self.trust=trust
        self.avg_days_in_shelter=avg_days_in_shelter
        self.personality_type=personality_type
        self.temperament=temperament
        self.energy_level=energy_level
        self.trainability=trainability
        self.grooming_frequency=grooming_frequency
        self.weight_gain_risk=weight_gain_risk
        self.exercise_needs=exercise_needs
        self.affectionate=affectionate
        self.stranger_friendly=stranger_friendly


    # TODO:
    # create a model from schema
    @classmethod
    def to_model(cls, schema: PlayerProfileSchema):
        return cls(
            player_name=schema.player_name,
            breed=schema.breed,
            adopter_profile=schema.adopter_profile,
            hunger=schema.hunger,
            happiness=schema.happiness,
            energy=schema.energy,
            health=schema.health,
            trust=schema.trust,
            avg_days_in_shelter=schema.avg_days_in_shelter,
            personality_type=schema.personality_type,
            temperament=schema.temperament,
            energy_level=schema.energy_level,
            trainability=schema.trainability,
            grooming_frequency=schema.grooming_frequency,
            weight_gain_risk=schema.weight_gain_risk,
            exercise_needs=schema.exercise_needs,
            affectionate=schema.affectionate,
            stranger_friendly=schema.stranger_friendly
        )

    @classmethod
    def from_dynamo(cls, item: dict):
        return cls(
            player_name=item['player_name'],
            breed=item['breed'],
            adopter_profile=item['adopter_profile'],
            hunger=float(item['hunger']),
            happiness=float(item['happiness']),
            energy=float(item['energy']),
            health=float(item['health']),
            trust=float(item['trust']),
            avg_days_in_shelter=float(item['avg_days_in_shelter']),
            personality_type=item['personality_type'],
            temperament=item['temperament'],
            energy_level=float(item['energy_level']),
            trainability=float(item['trainability']),
            grooming_frequency=float(item['grooming_frequency']),
            weight_gain_risk=float(item['weight_gain_risk']),
            exercise_needs=float(item['exercise_needs']),
            affectionate=int(item['affectionate']),
            stranger_friendly=int(item['stranger_friendly']),
        )

    def to_floats(self) -> dict:
        return {
            "player_name": self.player_name,
            "breed": self.breed,
            "adopter_profile": self.adopter_profile,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "health": self.health,
            "trust": self.trust,
            "avg_days_in_shelter": self.avg_days_in_shelter,
            "personality_type": self.personality_type,
            "temperament": self.temperament,
            "energy_level": self.energy_level,
            "trainability": self.trainability,
            "grooming_frequency": self.grooming_frequency,
            "weight_gain_risk": self.weight_gain_risk,
            "exercise_needs": self.exercise_needs,
            "affectionate": self.affectionate,
            "stranger_friendly": self.stranger_friendly,
        }

    def to_decimals(self) -> dict:
        return {
            "player_name": self.player_name,
            "breed": self.breed,
            "adopter_profile": self.adopter_profile,
            "hunger": Decimal(str(self.hunger)),
            "happiness": Decimal(str(self.happiness)),
            "energy": Decimal(str(self.energy)),
            "health": Decimal(str(self.health)),
            "trust": Decimal(str(self.trust)),
            "avg_days_in_shelter": Decimal(str(self.avg_days_in_shelter)),
            "personality_type": self.personality_type,
            "temperament": self.temperament,
            "energy_level": Decimal(str(self.energy_level)),
            "trainability": Decimal(str(self.trainability)),
            "grooming_frequency": Decimal(str(self.grooming_frequency)),
            "weight_gain_risk": Decimal(str(self.weight_gain_risk)),
            "exercise_needs": Decimal(str(self.exercise_needs)),
            "affectionate": self.affectionate,
            "stranger_friendly": self.stranger_friendly,
        }