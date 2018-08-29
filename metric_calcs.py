"""Metric calculations."""


def get_srch_term_popularity(num_matches_total):
    """Calculate the search term popularity."""
    # based on the past week
    return num_matches_total // 7


def get_pairing_popularities(pairings_dict, num_matches_returned):
    """
    Determine popularity of pairings with original search term.

    Takes a dictionary containing a pairing food term and the number of times 
    it occured in the search:
        {"food_term": occurences, ..., "food_term_n": occurences}

    Returns a dictionary of the same food term and its popularity score:
        {"food_term": popularity, ..., "food_term_n": popularity}
    """
    return {food_term: (occurences/num_matches_returned)*10 for \
                (food_term, occurences) in pairings_dict.items()}