from typing import List, Optional

class Player:
    unique_identifier: str
    name: str
    draft_probability_score: float
    
    def __init__(self, name):
        self.name = name
        self.draft_probability_score = 1.0
        
        self._initialize_unique_identifier()
        
    def _initialize_unique_identifier(self):
        self.unique_identifier = self.name
        
    def get_unique_identifier(self):
        return str(self.unique_identifier)
    
    def get_draft_probability_score(self):
        return self.draft_probability_score
    
    def set_draft_probability_score(self, value: float):
        self.draft_probability_score = value
        
    def add_to_draft_probability_score(self, value: float):
        self.draft_probability_score += value
        
    def __str__(self) -> str:
        return self.get_unique_identifier()
    
    def __repr__(self) -> str:
        return self.__str__()

class Team:
    unique_identifier: str
    player_1: Player
    player_2: Player
    
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        
        self._initialize_unique_identifier()
    
    @classmethod
    def from_names(cls, player_1_name: str, player_2_name: str):
        return cls(Player(player_1_name), Player(player_2_name))
        
    def _initialize_unique_identifier(self):
        player_1_uid = self.player_1.get_unique_identifier()
        player_2_uid = self.player_2.get_unique_identifier()
        
        player_uids = [player_1_uid, player_2_uid]
        
        player_uids = sorted(player_uids)
        
        self.unique_identifier = player_uids[0] + " & " + player_uids[1]
        
    def get_unique_identifier(self):
        return str(self.unique_identifier)
    
    def get_all_player_uids(self) -> List[str]:
        return [self.player_1.get_unique_identifier(), self.player_2.get_unique_identifier()]
    
    def __str__(self) -> str:
        return self.get_unique_identifier()
    
    def __repr__(self) -> str:
        return self.__str__()


class Matchup:
    unique_identifier: str
    team_a: Team
    team_b: Team
    
    def __init__(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b
        
        self._initialize_unique_identifier()
    
    @classmethod
    def create_dummy(cls):
        return cls.from_names("n.a.", "n.a.", "n.a.", "n.a.")
    
    @classmethod
    def from_names(cls, player_name_1, player_name_2, player_name_3, player_name_4):
        
        return cls(Team.from_names(player_name_1, player_name_2), Team.from_names(player_name_3, player_name_4))
        
    def _initialize_unique_identifier(self):
        team_a_uid = self.team_a.get_unique_identifier()
        team_b_uid = self.team_b.get_unique_identifier()
        team_uids = [team_a_uid, team_b_uid]
        
        team_uids = sorted(team_uids)
        
        self.unique_identifier = team_uids[0] + " vs. "+ team_uids[1]
    
    def get_unique_identifier(self):
        return str(self.unique_identifier)
    
    def get_all_player_uids(self) -> List[str]:
        
        players = []
        
        players.append(self.team_a.player_1.get_unique_identifier())
        players.append(self.team_a.player_2.get_unique_identifier())
        players.append(self.team_b.player_1.get_unique_identifier())
        players.append(self.team_b.player_2.get_unique_identifier())
        
        return players
    
    def get_teams(self) -> List[Team]:
        return [self.team_a, self.team_b]
    
    def get_teammate(self, player_uid: str) -> Optional[Player]:
        if player_uid == self.team_a.player_1.get_unique_identifier():
            return self.team_a.player_2
        elif player_uid == self.team_a.player_2.get_unique_identifier():
            return self.team_a.player_1
        elif player_uid == self.team_b.player_1.get_unique_identifier():
            return self.team_b.player_2
        elif player_uid == self.team_b.player_2.get_unique_identifier():
            return self.team_b.player_1
        else:
            return None
        
    def get_enemy_team(self, player_uid: str) -> Optional[Team]:
        if player_uid in self.team_a.get_unique_identifier():
            return self.team_b
        elif player_uid in self.team_b.get_unique_identifier():
            return self.team_a
        else:
            return None
    
    def __str__(self) -> str:
        return self.get_unique_identifier()
    
    def __repr__(self) -> str:
        return self.__str__()