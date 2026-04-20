from schemas.player_schema import StartGameSchema, AdopterProfileSchema, PlayerProfileSchema

class StartGameModel:
    # init
    def __init__(
        self,
        player_name: str,
        breed: str,
        adopter_profile: dict
    ):
        self.player_name=player_name
        self.breed=breed
        self.adopter_profile=adopter_profile


    # TODO:
    # create a model from schema
    def to_model(cls, schema: StartGameSchema):
        return cls(
            player_name=schema.player_name,
            breed=schema.breed,
            adopter_profile=schema.adopter_profile
        )

    # convert dynamodb Decimals to python floats
    def to_floats(self):
        return {
            "player_name": self.player_name,
            "breed": self.breed,
            "adopter_profile": self.adopter_profile
        }

    # convert python floats to Decimals
    def to_decimals(self):
        return StartGameModel(
            player_name=self.player_name,
            breed=self.breed,
            adopter_profile=self.adopter_profile
        )
    
class AdopterProfileModel:
    # init
    def __init__(
        self,
        living_situation: str,
        climate: str,
        time_home: str,
        experience: str
    ):
        self.living_situation=living_situation
        self.climate=climate
        self.time_home=time_home
        self.experience=experience


    # TODO:
    # create a model from schema
    def to_model(cls, schema: AdopterProfileSchema):
        return cls(
            living_situation=schema.living_situation,
            climate=schema.climate,
            time_home=schema.time_home,
            experience=schema.experience
        )

    # convert dynamodb Decimals to python floats
    def to_floats(self):
        return {
            "living_situation": self.living_situation,
            "climate": self.climate,
            "time_home": self.time_home,
            "experience": self.experience
        }

    # convert python floats to Decimals
    def to_decimals(self):
        return StartGameModel(
            living_situation=self.living_situation,
            climate=self.climate,
            time_home=self.time_home,
            experience=self.experience
        )

class PlayerProfileModel:
    # init
    def __init__(
        self,
        player_name: str,
        breed: str,
        adopter_profile: str,
        hunger: str,
        happiness: str,
        energy: str,
        health: str,
        trust: str,
        avg_days_in_shelter: str,
        personality_type: str,
        temperament: str,
        energy_level: str,
        trainability: str,
        grooming_frequency: str,
        weight_gain_risk: str,
        exercise_needs: str,
        affectionate: str,
        stranger_friendly: str
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

    # convert dynamodb Decimals to python floats
    def to_floats(self):
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
            "stranger_friendly": self.stranger_friendly
        }

    # convert python floats to Decimals
    def to_decimals(self):
        return PlayerProfileModel(
            player_name=self.player_name,
            breed=self.breed,
            adopter_profile=self.adopter_profile,
            hunger=self.hunger,
            happiness=self.happiness,
            energy=self.energy,
            health=self.health,
            trust=self.trust,
            avg_days_in_shelter=self.avg_days_in_shelter,
            personality_type=self.personality_type,
            temperament=self.temperament,
            energy_level=self.energy_level,
            trainability=self.trainability,
            grooming_frequency=self.grooming_frequency,
            weight_gain_risk=self.weight_gain_risk,
            exercise_needs=self.exercise_needs,
            affectionate=self.affectionate,
            stranger_friendly=self.stranger_friendly
        )