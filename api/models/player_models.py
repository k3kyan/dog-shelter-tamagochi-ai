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
    
    # dont need to_floats since since Pydantic's coercion handles both read paths
    # Pydantic coerces Decimals on the return, so from_dynamo and to_floats become dead code and can be deleted
    # TODO: