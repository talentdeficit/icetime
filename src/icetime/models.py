from pydantic import BaseModel, Field, AliasPath, field_validator
from typing import Optional, List


class Team(BaseModel):
    model_config = {"frozen": True}

    id: int
    franchise_id: Optional[int] = Field(alias="franchiseId", default=None)
    full_name: str = Field(alias="fullName")
    league_id: int = Field(alias="leagueId")
    raw_tricode: str = Field(alias="rawTricode")
    tri_code: str = Field(alias="triCode")


class Game(BaseModel):
    model_config = {"frozen": True}

    id: int
    eastern_start_time: str = Field(alias="easternStartTime")
    game_date: str = Field(alias="gameDate")
    game_number: int = Field(alias="gameNumber")
    game_schedule_state_id: int = Field(alias="gameScheduleStateId")
    game_state_id: int = Field(alias="gameStateId")
    game_type: int = Field(alias="gameType")
    home_score: int = Field(alias="homeScore")
    home_team_id: int = Field(alias="homeTeamId")
    period: Optional[int] = None
    season: int
    visiting_score: int = Field(alias="visitingScore")
    visiting_team_id: int = Field(alias="visitingTeamId")


class Season(BaseModel):
    model_config = {"frozen": True}

    id: int
    name: str = Field(alias="id")
    all_star_game_in_use: int = Field(alias="allStarGameInUse")
    conferences_in_use: int = Field(alias="conferencesInUse")
    divisions_in_use: int = Field(alias="divisionsInUse")
    end_date: str = Field(alias="endDate")
    entry_draft_in_use: int = Field(alias="entryDraftInUse")
    formatted_season_id: str = Field(alias="formattedSeasonId")
    minimum_playoff_minutes_for_goalie_stats_leaders: int = Field(
        alias="minimumPlayoffMinutesForGoalieStatsLeaders"
    )
    minimum_regular_games_for_goalie_stats_leaders: int = Field(
        alias="minimumRegularGamesForGoalieStatsLeaders"
    )
    nhl_stanley_cup_owner: int = Field(alias="nhlStanleyCupOwner")
    number_of_games: int = Field(alias="numberOfGames")
    olympics_participation: int = Field(alias="olympicsParticipation")
    point_for_ot_loss_in_use: int = Field(alias="pointForOTLossInUse")
    preseason_startdate: Optional[str] = Field(alias="preseasonStartdate", default=None)
    regular_season_end_date: str = Field(alias="regularSeasonEndDate")
    row_in_use: int = Field(alias="rowInUse")
    season_ordinal: int = Field(alias="seasonOrdinal")
    start_date: str = Field(alias="startDate")
    supplemental_draft_in_use: int = Field(alias="supplementalDraftInUse")
    ties_in_use: int = Field(alias="tiesInUse")
    total_playoff_games: int = Field(alias="totalPlayoffGames")
    total_regular_season_games: int = Field(alias="totalRegularSeasonGames")
    wildcard_in_use: int = Field(alias="wildcardInUse")

    @field_validator("name", mode="before")
    @classmethod
    def cast_season_to_string(cls, v):
        return str(v)


class GameResult(BaseModel):
    model_config = {"frozen": True}

    id: int
    season: int
    game_type: int = Field(alias="gameType")
    game_date: str = Field(alias="gameDate")
    venue: str = Field(alias=AliasPath("venue", "default"))
    venue_location: str = Field(alias=AliasPath("venueLocation", "default"))
    start_time_utc: str = Field(alias="startTimeUTC")
    eastern_utc_offset: str = Field(alias="easternUTCOffset")
    venue_utc_offset: str = Field(alias="venueUTCOffset")
    game_state: str = Field(alias="gameState")
    game_schedule_state: str = Field(alias="gameScheduleState")
    period: Optional[int] = Field(
        alias=AliasPath("periodDescriptor", "number"), default=None
    )
    period_type: Optional[str] = Field(
        alias=AliasPath("periodDescriptor", "periodType"), default=None
    )
    away_team_id: int = Field(alias=AliasPath("awayTeam", "id"))
    away_team_name: str = Field(alias=AliasPath("awayTeam", "commonName", "default"))
    away_team_abbreviation: str = Field(alias=AliasPath("awayTeam", "abbrev"))
    away_team_logo: str = Field(alias=AliasPath("awayTeam", "logo"))
    away_team_dark_logo: str = Field(alias=AliasPath("awayTeam", "darkLogo"))
    home_team_id: int = Field(alias=AliasPath("homeTeam", "id"))
    home_team_name: str = Field(alias=AliasPath("homeTeam", "commonName", "default"))
    home_team_abbreviation: str = Field(alias=AliasPath("homeTeam", "abbrev"))
    home_team_logo: str = Field(alias=AliasPath("homeTeam", "logo"))
    home_team_dark_logo: str = Field(alias=AliasPath("homeTeam", "darkLogo"))
    away_score: int = Field(alias=AliasPath("awayTeam", "score"))
    home_score: int = Field(alias=AliasPath("homeTeam", "score"))
    away_shots: Optional[int] = Field(alias=AliasPath("awayTeam", "sog"), default=None)
    home_shots: Optional[int] = Field(alias=AliasPath("homeTeam", "sog"), default=None)
    time_remaining: str = Field(alias=AliasPath("clock", "timeRemaining"))


class Shift(BaseModel):
    model_config = {"frozen": True}

    id: int
    detail_code: Optional[int] = Field(alias="detailCode", default=None)
    duration: Optional[str] = Field(default=None)
    end_time: str = Field(alias="endTime")
    event_description: Optional[str] = Field(alias="eventDescription", default=None)
    event_details: Optional[str] = Field(alias="eventDetails", default=None)
    event_number: Optional[int] = Field(alias="eventNumber", default=None)
    first_name: str = Field(alias="firstName")
    game_id: int = Field(alias="gameId")
    hex_value: Optional[str] = Field(alias="hexValue", default=None)
    last_name: str = Field(alias="lastName")
    period: int
    player_id: int = Field(alias="playerId")
    shift_number: int = Field(alias="shiftNumber")
    start_time: str = Field(alias="startTime")
    team_abbrev: str = Field(alias="teamAbbrev")
    team_id: int = Field(alias="teamId")
    team_name: str = Field(alias="teamName")
    type_code: int = Field(alias="typeCode")
    game_type: int


class Player(BaseModel):
    model_config = {"frozen": True}

    id: int = Field(alias="playerId")
    is_active: bool = Field(alias="isActive")
    current_team_id: Optional[int] = Field(alias="currentTeamId", default=None)
    current_team_abbrev: Optional[str] = Field(alias="currentTeamAbbrev", default=None)
    full_team_name: str = Field(alias=AliasPath("fullTeamName", "default"))
    team_common_name: str = Field(alias=AliasPath("teamCommonName", "default"))
    team_place_name: str = Field(
        alias=AliasPath("teamPlaceNameWithPreposition", "default")
    )
    first_name: str = Field(alias=AliasPath("firstName", "default"))
    last_name: str = Field(alias=AliasPath("lastName", "default"))
    team_logo: str = Field(alias="teamLogo")
    sweater_number: int = Field(alias="sweaterNumber")
    position: str
    headshot: str
    hero_image: str = Field(alias="heroImage")
    height_in_inches: int = Field(alias="heightInInches")
    height_in_centimeters: int = Field(alias="heightInCentimeters")
    weight_in_pounds: int = Field(alias="weightInPounds")
    weight_in_kilograms: int = Field(alias="weightInKilograms")
    birth_date: str = Field(alias="birthDate")
    birth_city: str = Field(alias=AliasPath("birthCity", "default"))
    birth_state_province: str = Field(alias=AliasPath("birthStateProvince", "default"))
    birth_country: str = Field(alias="birthCountry")
    shoots_catches: str = Field(alias="shootsCatches")
    draft_year: Optional[int] = Field(
        alias=AliasPath("draftDetails", "year"), default=None
    )
    draft_team_abbrev: Optional[str] = Field(
        alias=AliasPath("draftDetails", "teamAbbrev"), default=None
    )
    draft_round: Optional[int] = Field(
        alias=AliasPath("draftDetails", "round"), default=None
    )
    draft_pick_in_round: Optional[int] = Field(
        alias=AliasPath("draftDetails", "pickInRound"), default=None
    )
    draft_overall_pick: Optional[int] = Field(
        alias=AliasPath("draftDetails", "overallPick"), default=None
    )


class TeamRoster(BaseModel):
    model_config = {"frozen": True}

    """Team roster containing player IDs by position."""

    forwards: List[int]
    defensemen: List[int]
    goalies: List[int]

    @property
    def all_player_ids(self) -> List[int]:
        """Get all player IDs from all positions."""
        return self.forwards + self.defensemen + self.goalies

    def get_position_for_player(self, player_id: int) -> Optional[str]:
        """Get the position group for a given player ID."""
        if player_id in self.forwards:
            return "forwards"
        elif player_id in self.defensemen:
            return "defensemen"
        elif player_id in self.goalies:
            return "goalies"
        return None

    def has_player(self, player_id: int) -> bool:
        """Check if a player ID exists in the roster."""
        return player_id in self.all_player_ids
