import pytest
from icetime.models import Team, Game, Season, GameResult, Shift, Player, TeamRoster


class TestTeam:
    required_fields = {
        "id": 1,
        "fullName": "New Jersey Devils",
        "leagueId": 133,
        "rawTricode": "NJD",
        "triCode": "NJD",
    }

    optional_fields = {"franchiseId": 23}

    team_data = {**required_fields, **optional_fields}

    @pytest.mark.unit
    def test_team_creation(self):
        team = Team(**self.team_data)

        assert team.id == 1
        assert team.franchise_id == 23
        assert team.full_name == "New Jersey Devils"
        assert team.league_id == 133
        assert team.raw_tricode == "NJD"
        assert team.tri_code == "NJD"

    @pytest.mark.unit
    def test_team_optional_fields(self):
        team = Team(**self.required_fields)

        assert team.franchise_id is None


class TestGame:
    required_fields = {
        "id": 2023020001,
        "easternStartTime": "2023-10-10T19:00:00Z",
        "gameDate": "2023-10-10",
        "gameNumber": 1,
        "gameScheduleStateId": 4,
        "gameStateId": 7,
        "gameType": 2,
        "homeScore": 3,
        "homeTeamId": 1,
        "season": 20232024,  # Integer
        "visitingScore": 2,
        "visitingTeamId": 2,
    }

    optional_fields = {
        "period": 3,
    }

    game_data = {**required_fields, **optional_fields}

    @pytest.mark.unit
    def test_game_creation(self):
        game = Game(**self.game_data)

        assert game.id == 2023020001
        assert game.eastern_start_time == "2023-10-10T19:00:00Z"
        assert game.game_date == "2023-10-10"
        assert game.game_schedule_state_id == 4
        assert game.game_state_id == 7
        assert game.game_type == 2
        assert game.home_score == 3
        assert game.home_team_id == 1
        assert game.period == 3
        assert game.season == 20232024
        assert game.visiting_score == 2
        assert game.visiting_team_id == 2

    @pytest.mark.unit
    def test_game_optional_fields(self):
        game = Game(**self.required_fields)

        assert game.period is None


class TestSeason:
    required_fields = {
        "id": 20232024,
        "allStarGameInUse": 1,
        "conferencesInUse": 1,
        "divisionsInUse": 1,
        "endDate": "2024-06-24T00:00:00",
        "entryDraftInUse": 1,
        "formattedSeasonId": "2023-24",
        "minimumPlayoffMinutesForGoalieStatsLeaders": 180,
        "minimumRegularGamesForGoalieStatsLeaders": 25,
        "nhlStanleyCupOwner": 1,
        "numberOfGames": 82,
        "olympicsParticipation": 0,
        "pointForOTLossInUse": 1,
        "regularSeasonEndDate": "2024-04-18T22:30:00",
        "rowInUse": 1,
        "seasonOrdinal": 107,
        "startDate": "2023-10-10T17:30:00",
        "supplementalDraftInUse": 0,
        "tiesInUse": 0,
        "totalPlayoffGames": 89,
        "totalRegularSeasonGames": 1312,
        "wildcardInUse": 1,
    }

    optional_fields = {
        "preseasonStartdate": "2023-09-23T00:05:00",
    }

    season_data = {**required_fields, **optional_fields}

    @pytest.mark.unit
    def test_season_creation(self):
        season = Season(**self.season_data)

        assert season.id == 20232024
        assert season.name == "20232024"
        assert season.all_star_game_in_use == 1
        assert season.conferences_in_use == 1
        assert season.divisions_in_use == 1
        assert season.end_date == "2024-06-24T00:00:00"
        assert season.entry_draft_in_use == 1
        assert season.formatted_season_id == "2023-24"
        assert season.minimum_playoff_minutes_for_goalie_stats_leaders == 180
        assert season.minimum_regular_games_for_goalie_stats_leaders == 25
        assert season.nhl_stanley_cup_owner == 1
        assert season.number_of_games == 82
        assert season.olympics_participation == 0
        assert season.point_for_ot_loss_in_use == 1
        assert season.preseason_startdate == "2023-09-23T00:05:00"
        assert season.regular_season_end_date == "2024-04-18T22:30:00"
        assert season.row_in_use == 1
        assert season.season_ordinal == 107
        assert season.start_date == "2023-10-10T17:30:00"
        assert season.supplemental_draft_in_use == 0
        assert season.ties_in_use == 0
        assert season.total_playoff_games == 89
        assert season.total_regular_season_games == 1312
        assert season.wildcard_in_use == 1

    @pytest.mark.unit
    def test_season_name_validation(self):
        season = Season(**self.season_data)

        assert isinstance(season.name, str)
        assert season.name == "20232024"

    @pytest.mark.unit
    def test_season_optional_fields(self):
        season = Season(**self.required_fields)

        assert season.preseason_startdate is None


class TestGameResult:
    game_result_data = {
        "id": 2023020001,
        "season": 20232024,
        "gameType": 2,
        "gameDate": "2023-10-10",
        "venue": {"default": "Prudential Center"},
        "venueLocation": {"default": "Newark"},
        "startTimeUTC": "2023-10-10T23:00:00Z",
        "easternUTCOffset": "-04:00",
        "venueUTCOffset": "-04:00",
        "gameState": "FINAL",
        "gameScheduleState": "OK",
        "periodDescriptor": {"number": 3, "periodType": "REG"},
        "awayTeam": {
            "id": 2,
            "commonName": {"default": "Rangers"},
            "abbrev": "NYR",
            "logo": "https://assets.nhle.com/logos/nhl/svg/NYR_light.svg",
            "darkLogo": "https://assets.nhle.com/logos/nhl/svg/NYR_dark.svg",
            "score": 2,
            "sog": 25,
        },
        "homeTeam": {
            "id": 1,
            "commonName": {"default": "Devils"},
            "abbrev": "NJD",
            "logo": "https://assets.nhle.com/logos/nhl/svg/NJD_light.svg",
            "darkLogo": "https://assets.nhle.com/logos/nhl/svg/NJD_dark.svg",
            "score": 3,
            "sog": 30,
        },
        "clock": {"timeRemaining": "00:00"},
        "plays": [],
    }

    @pytest.mark.unit
    def test_game_result_creation(self):
        result = GameResult(**self.game_result_data)

        assert result.id == 2023020001
        assert result.season == 20232024
        assert result.game_type == 2
        assert result.game_date == "2023-10-10"
        assert result.venue == "Prudential Center"
        assert result.venue_location == "Newark"
        assert result.start_time_utc == "2023-10-10T23:00:00Z"
        assert result.eastern_utc_offset == "-04:00"
        assert result.venue_utc_offset == "-04:00"
        assert result.game_state == "FINAL"
        assert result.game_schedule_state == "OK"
        assert result.period == 3
        assert result.period_type == "REG"
        assert result.away_team_id == 2
        assert result.away_team_name == "Rangers"
        assert result.away_team_abbreviation == "NYR"
        assert (
            result.away_team_logo
            == "https://assets.nhle.com/logos/nhl/svg/NYR_light.svg"
        )
        assert (
            result.away_team_dark_logo
            == "https://assets.nhle.com/logos/nhl/svg/NYR_dark.svg"
        )
        assert result.away_score == 2
        assert result.away_shots == 25
        assert result.home_team_id == 1
        assert result.home_team_name == "Devils"
        assert result.home_team_abbreviation == "NJD"
        assert (
            result.home_team_logo
            == "https://assets.nhle.com/logos/nhl/svg/NJD_light.svg"
        )
        assert (
            result.home_team_dark_logo
            == "https://assets.nhle.com/logos/nhl/svg/NJD_dark.svg"
        )
        assert result.home_score == 3
        assert result.home_shots == 30
        assert result.time_remaining == "00:00"


class TestShift:
    required_fields = {
        "id": 15400423,
        "detailCode": 0,
        "duration": "00:36",
        "endTime": "01:25",
        "eventNumber": 56,
        "firstName": "Brad",
        "gameId": 2024030121,
        "hexValue": "#C8102E",
        "lastName": "Marchand",
        "period": 1,
        "playerId": 8473419,
        "shiftNumber": 1,
        "startTime": "00:49",
        "teamAbbrev": "FLA",
        "teamId": 13,
        "teamName": "Florida Panthers",
        "typeCode": 517,
        "game_type": 3,
    }

    optional_fields = {
        "eventDescription": "Some event description",
        "eventDetails": "Some event details",
    }

    shift_data = {**required_fields, **optional_fields}

    @pytest.mark.unit
    def test_shift_creation(self):
        shift = Shift(**self.shift_data)

        assert shift.id == 15400423
        assert shift.detail_code == 0
        assert shift.duration == "00:36"
        assert shift.end_time == "01:25"
        assert shift.event_description == "Some event description"
        assert shift.event_details == "Some event details"
        assert shift.event_number == 56
        assert shift.first_name == "Brad"
        assert shift.game_id == 2024030121
        assert shift.hex_value == "#C8102E"
        assert shift.last_name == "Marchand"
        assert shift.period == 1
        assert shift.player_id == 8473419
        assert shift.shift_number == 1
        assert shift.start_time == "00:49"
        assert shift.team_abbrev == "FLA"
        assert shift.team_id == 13
        assert shift.team_name == "Florida Panthers"
        assert shift.type_code == 517
        assert shift.game_type == 3

    @pytest.mark.unit
    def test_shift_optional_fields(self):
        shift = Shift(**self.required_fields)

        assert shift.event_description is None
        assert shift.event_details is None


class TestPlayer:
    required_fields = {
        "playerId": 8478402,
        "isActive": True,
        "fullTeamName": {"default": "Edmonton Oilers"},
        "teamCommonName": {"default": "Oilers"},
        "teamPlaceNameWithPreposition": {"default": "Edmonton"},
        "firstName": {"default": "Connor"},
        "lastName": {"default": "McDavid"},
        "teamLogo": "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg",
        "sweaterNumber": 97,
        "position": "C",
        "headshot": "https://assets.nhle.com/mugs/nhl/20252026/EDM/8478402.png",
        "heroImage": "https://assets.nhle.com/mugs/actionshots/1296x729/8478402.jpg",
        "heightInInches": 73,
        "heightInCentimeters": 185,
        "weightInPounds": 194,
        "weightInKilograms": 88,
        "birthDate": "1997-01-13",
        "birthCity": {"default": "Richmond Hill"},
        "birthStateProvince": {"default": "Ontario"},
        "birthCountry": "CAN",
        "shootsCatches": "L",
    }

    optional_fields = {
        "currentTeamId": 22,
        "currentTeamAbbrev": "EDM",
        "draftDetails": {
            "year": 2015,
            "teamAbbrev": "EDM",
            "round": 1,
            "pickInRound": 1,
            "overallPick": 1,
        },
    }

    player_data = {**required_fields, **optional_fields}

    @pytest.mark.unit
    def test_player_creation(self):
        player = Player(**self.player_data)

        assert player.id == 8478402
        assert player.is_active is True
        assert player.current_team_id == 22
        assert player.current_team_abbrev == "EDM"
        assert player.full_team_name == "Edmonton Oilers"
        assert player.team_common_name == "Oilers"
        assert player.team_place_name == "Edmonton"
        assert player.first_name == "Connor"
        assert player.last_name == "McDavid"
        assert player.team_logo == "https://assets.nhle.com/logos/nhl/svg/EDM_light.svg"
        assert player.sweater_number == 97
        assert player.position == "C"
        assert (
            player.headshot
            == "https://assets.nhle.com/mugs/nhl/20252026/EDM/8478402.png"
        )
        assert (
            player.hero_image
            == "https://assets.nhle.com/mugs/actionshots/1296x729/8478402.jpg"
        )
        assert player.height_in_inches == 73
        assert player.height_in_centimeters == 185
        assert player.weight_in_pounds == 194
        assert player.weight_in_kilograms == 88
        assert player.birth_date == "1997-01-13"
        assert player.birth_city == "Richmond Hill"
        assert player.birth_state_province == "Ontario"
        assert player.birth_country == "CAN"
        assert player.shoots_catches == "L"
        assert player.draft_year == 2015
        assert player.draft_team_abbrev == "EDM"
        assert player.draft_round == 1
        assert player.draft_pick_in_round == 1
        assert player.draft_overall_pick == 1

    @pytest.mark.unit
    def test_player_optional_fields(self):
        player = Player(**self.required_fields)

        assert player.current_team_id is None
        assert player.current_team_abbrev is None
        assert player.draft_year is None
        assert player.draft_team_abbrev is None
        assert player.draft_round is None
        assert player.draft_pick_in_round is None
        assert player.draft_overall_pick is None


class TestTeamRoster:
    roster_data = {
        "forwards": [8479318, 8478483, 8477939],  # Matthews, Marner, Nylander
        "defensemen": [8476853, 8480043],  # Rielly, Liljegren
        "goalies": [8479361, 8483710],  # Woll, Hildeby
    }

    @pytest.mark.unit
    def test_team_roster_creation(self):
        roster = TeamRoster(**self.roster_data)

        assert len(roster.forwards) == 3
        assert len(roster.defensemen) == 2
        assert len(roster.goalies) == 2
        assert 8479318 in roster.forwards
        assert 8476853 in roster.defensemen
        assert 8479361 in roster.goalies

    @pytest.mark.unit
    def test_team_roster_all_player_ids_property(self):
        roster = TeamRoster(**self.roster_data)
        all_player_ids = roster.all_player_ids

        assert len(all_player_ids) == 7
        assert 8479318 in all_player_ids  # Matthews
        assert 8476853 in all_player_ids  # Rielly
        assert 8479361 in all_player_ids  # Woll

    @pytest.mark.unit
    def test_team_roster_get_position_for_player(self):
        roster = TeamRoster(**self.roster_data)

        assert roster.get_position_for_player(8479318) == "forwards"
        assert roster.get_position_for_player(8476853) == "defensemen"
        assert roster.get_position_for_player(8479361) == "goalies"
        assert roster.get_position_for_player(99999) is None

    @pytest.mark.unit
    def test_team_roster_has_player(self):
        roster = TeamRoster(**self.roster_data)

        assert roster.has_player(8479318) is True  # Matthews
        assert roster.has_player(8476853) is True  # Rielly
        assert roster.has_player(8479361) is True  # Woll
        assert roster.has_player(99999) is False

    @pytest.mark.unit
    def test_team_roster_empty_positions(self):
        empty_roster_data = {
            "forwards": [],
            "defensemen": [],
            "goalies": [],
        }
        roster = TeamRoster(**empty_roster_data)

        assert len(roster.forwards) == 0
        assert len(roster.defensemen) == 0
        assert len(roster.goalies) == 0
        assert len(roster.all_player_ids) == 0
        assert roster.has_player(8479318) is False
