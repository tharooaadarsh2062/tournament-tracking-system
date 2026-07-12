import datetime
from django.utils import timezone
from tournaments.models import Match

def generate_round_robin(tournament, teams):
    """
    Generate round robin fixtures for a tournament.
    Every team plays every other team once.
    """
    teams_list = list(teams)
    if len(teams_list) < 2:
        raise ValueError("At least 2 teams are required to generate fixtures.")
        
    if len(teams_list) % 2 != 0:
        teams_list.append(None) # Bye team placeholder
        
    n = len(teams_list)
    matches_to_create = []
    
    # Schedule matches starting from tomorrow, 1 match day per round
    start_date = timezone.now() + datetime.timedelta(days=1)
    
    # Berger Tables / Circle Method rotation algorithm
    for round_num in range(n - 1):
        round_date = start_date + datetime.timedelta(days=round_num)
        for i in range(n // 2):
            home = teams_list[i]
            away = teams_list[n - 1 - i]
            
            if home is not None and away is not None:
                # Alternate home/away designation to distribute hosting duties
                if round_num % 2 == 1:
                    home, away = away, home
                    
                match = Match(
                    tournament=tournament,
                    home_team=home,
                    away_team=away,
                    scheduled_time=round_date.replace(hour=15, minute=0, second=0, microsecond=0)
                )
                matches_to_create.append(match)
                
        # Rotate list, keeping the first element fixed
        teams_list = [teams_list[0]] + [teams_list[-1]] + teams_list[1:-1]
        
    Match.objects.bulk_create(matches_to_create)
    return len(matches_to_create)


def generate_knockout(tournament, teams):
    """
    Generate the first round of knockout fixtures for a tournament.
    Consequential rounds are generated as winners advance.
    """
    teams_list = list(teams)
    if len(teams_list) < 2:
        raise ValueError("At least 2 teams are required to generate fixtures.")
        
    matches_to_create = []
    start_date = timezone.now() + datetime.timedelta(days=1)
    
    # Pair consecutive teams
    for i in range(0, len(teams_list) - 1, 2):
        match = Match(
            tournament=tournament,
            home_team=teams_list[i],
            away_team=teams_list[i+1],
            scheduled_time=start_date.replace(hour=15, minute=0, second=0, microsecond=0)
        )
        matches_to_create.append(match)
        
    Match.objects.bulk_create(matches_to_create)
    return len(matches_to_create)
