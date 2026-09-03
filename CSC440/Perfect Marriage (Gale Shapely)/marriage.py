import sys
import os
import time

def gale_shapley(knight_preferences, lady_preferences):
    """
    Implements the Gale-Shapley algorithm to solve the stable marriage problem.

    Args:
    knight_preferences: A dictionary where keys are knight names and values are lists of lady names in preference order.
    lady_preferences: A dictionary where keys are lady names and values are lists of knight names in preference order.

    Returns:
    A dictionary mapping knights to their matched lady (stable marriage).
    """

    
    
    # Initialize all men and women as free (unengaged)
    single_knights = list(knight_preferences.keys())

    # Track proposals each knight has made
    proposals = {knight: [] for knight in knight_preferences}

    # Track engagements
    engagements = {}

    # Create a reverse lookup table for women's preferences
    lady_ranking = {
        lady: {knight: rank for rank, knight in enumerate(lady_preferences[lady])}
        for lady in lady_preferences
    }

    """INVARIANTS: knight_preferences and lady_preferences stay the same throughout the loop"""
    # initialization: we populate the knight_preferences and lady_preferences with the correct preferences
    # Maintenence: we reference the next preference in the loop, but never append or pop values
    # termination: the preference dictionaries stay the same.

    # TODO: Implement Gale-Shapely
    #as long as there are no unengaged knights
    while single_knights:
        #take out the current knight from singlelist: he is about to propose
        current_knight = single_knights.pop(0)
        #find knights preferences
        preference_list = knight_preferences[current_knight]
        #see which one of his prefered ladies has not been proposed to BY HIM. if not proposed to yet, make a proposal
        for current_lady in preference_list:
            if current_lady not in proposals[current_knight]:
                proposals[current_knight].append(current_lady)
                #lady is unengaged, she accepts the proposal. we break since the knight has proposed to his current most prefer
                if current_lady not in engagements:
                    engagements[current_lady]=current_knight
                    break
                #lady IS engaged to someone else. check if she prefers the current knight more than the knight she is currently engaged to 
                #if she likes him more, they get engaged and the old knight becomes single again. else, do nothing
                old_knight = engagements[current_lady]
                if lady_ranking[current_lady][current_knight]<lady_ranking[current_lady][old_knight]:
                    engagements[current_lady]=current_knight
                    single_knights.append(old_knight)
                    break
    # Return the engagements (man to woman)
    return {knight: lady for lady, knight in engagements.items()}

def read_file(file_path):
    knight_dict = {}
    lady_dict = {}
    # TODO: Load the data from file
    try:
        with open(file_path, 'r', encoding='latin-1') as file:
            lines = file.readlines()  
            n = int(lines[0].strip())
            for i in range(n*2):
                preflist = lines[i+1].split()
                if len(preflist) != n+1:
                    exit(2)
                name = preflist[0]
                preflist.pop(0)
                if i<n:
                    knight_dict[name] = preflist
                else:
                    lady_dict[name] = preflist
            #print(knight_dict)
            #print(lady_dict)
    except:
        exit(2)
    return knight_dict, lady_dict

if __name__ == "__main__":
    # Check input validity
    # TODO

    if len(sys.argv)<2:
        exit(2)
    # Load the preferences for knights & ladies
    knight_prefs, lady_prefs = read_file(sys.argv[1])

    # Conduct perfect marriages
    start = time.time()
    engagements = gale_shapley(knight_prefs, lady_prefs)
    end = time.time()
    runtime = end - start
    print(f"Runtime: {runtime:.6f} seconds")


    #for knight, lady in engagements.items():
        #print(f"{knight} {lady}")

