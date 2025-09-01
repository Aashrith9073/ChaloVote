from sqlalchemy.orm import Session
from collections import Counter
from app import models


def tally_votes(trip_id: int, db: Session):
    """
    Calculates the winner of a trip's vote using ranked-choice (instant-runoff) voting.
    """
    # 1. Get all votes and recommendations for this trip
    votes = db.query(models.Vote).join(models.Participant).filter(models.Participant.trip_id == trip_id).all()
    recommendations = db.query(models.Recommendation).filter(models.Recommendation.trip_id == trip_id).all()

    if not votes:
        return None  # No votes have been cast

    total_voters = len(votes)
    active_candidates = {rec.id for rec in recommendations}

    # 2. Run voting rounds until a winner is found
    while len(active_candidates) > 0:
        # Tally the top-ranked active choice for each voter in this round
        round_counts = Counter()
        for vote in votes:
            for choice_id in vote.ranked_choices:
                if choice_id in active_candidates:
                    round_counts[choice_id] += 1
                    break  # Move to the next voter

        # 3. Check for a winner (more than 50% of the vote)
        for candidate_id, count in round_counts.items():
            if count > total_voters / 2:
                # We have a winner!
                winner = db.query(models.Recommendation).filter(models.Recommendation.id == candidate_id).first()
                return winner

        # 4. If no winner, eliminate the candidate with the fewest votes
        if not round_counts:
            # This can happen in a tie where all remaining candidates are eliminated
            return None

        min_votes = min(round_counts.values())
        candidates_to_eliminate = {cid for cid, count in round_counts.items() if count == min_votes}

        # If all remaining candidates are tied, we can just pick one as a tie-breaker
        if set(round_counts.keys()) == candidates_to_eliminate:
            winner_id = list(round_counts.keys())[0]
            winner = db.query(models.Recommendation).filter(models.Recommendation.id == winner_id).first()
            return winner

        active_candidates -= candidates_to_eliminate

    return None  # Should not be reached in a normal vote