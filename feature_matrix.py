import random
import pandas as pd
from itertools import product

class IrishFeatureMatrix:
    def __init__(self):
        # Person features (1st, 2nd, 3rd singular/plural)
        self.persons = [
            "1sg",  # mé/mise
            "2sg",  # tú/tusa  
            "3sg_m", # sé/seisean
            "3sg_f", # sí/sise
            "1pl",  # muid/sinne
            "2pl",  # sibh/sibhse
            "3pl",   # siad/siadsan
            "saor"
        ]
        
        # Most common 15 Irish verbs (lemma forms)
        self.verbs = [
            "bí",      # be
            "déan",    # do/make
            "faigh",   # get
            "téigh",   # go
            "feic",    # see
            "tabhair", # give
            "tar",     # come
            "abair",   # say
            "ith",     # eat
            "ól",      # drink
            "ceannaigh", # buy
            "léigh",   # read
            "scríobh", # write
            "seas",    # stand
            "suigh"    # sit
        ]
        
        # Most common 10 Irish prepositions
        self.prepositions = [
            "i",       # in
            "ar",      # on
            "le",      # with
            "ó",       # from
            "do",      # to/for
            "ag",      # at
            "faoi",    # under/about
            "roimh",   # before
            "tar éis", # after
            "gan"      # without
        ]
        
        # Irish cases
        self.cases = [
            "nominative",  # tuiseal ainmneach
            "genitive",    # tuiseal ginideach  
            "dative"       # tuiseal tabharthach
        ]
        
        # Irish tenses (now part of the feature matrix)
        self.tenses = [
            "Aimsir Cháite",        # Past tense
            "Aimsir Láithreach",    # Present tense
            "Aimsir Fháistineach",  # Future tense
            "Aimsir Gnáthcháite",   # Past habitual
            "Aimsir Gnáthláithreach" # Present habitual
        ]
        
        # Create the full feature matrix
        self.feature_matrix = self._create_matrix()
    
    def _create_matrix(self):
        """Create a pandas DataFrame with all feature combinations including tense"""
        combinations = list(product(
            self.persons, 
            self.verbs, 
            self.prepositions, 
            self.cases,
            self.tenses  # Add tense to the combinations
        ))
        
        df = pd.DataFrame(combinations, columns=[
            'person', 'verb', 'preposition', 'case', 'tense'
        ])
        
        return df
    
    def sample_features(self, n=1, ensure_variation=True):
        """
        Sample n feature combinations from the matrix
        
        Args:
            n (int): Number of samples to return
            ensure_variation (bool): If True, ensures no duplicate combinations
        
        Returns:
            pd.DataFrame: Sampled feature combinations
        """
        if ensure_variation and n <= len(self.feature_matrix):
            return self.feature_matrix.sample(n=n, replace=False).reset_index(drop=True)
        else:
            return self.feature_matrix.sample(n=n, replace=True).reset_index(drop=True)
    
    def get_features_by_criteria(self, person=None, verb=None, preposition=None, case=None, tense=None):
        """
        Filter the matrix by specific criteria
        
        Args:
            person (str): Specific person to filter by
            verb (str): Specific verb to filter by  
            preposition (str): Specific preposition to filter by
            case (str): Specific case to filter by
            tense (str): Specific tense to filter by
        
        Returns:
            pd.DataFrame: Filtered feature combinations
        """
        filtered = self.feature_matrix.copy()
        
        if person:
            filtered = filtered[filtered['person'] == person]
        if verb:
            filtered = filtered[filtered['verb'] == verb]
        if preposition:
            filtered = filtered[filtered['preposition'] == preposition]
        if case:
            filtered = filtered[filtered['case'] == case]
        if tense:
            filtered = filtered[filtered['tense'] == tense]
            
        return filtered
    
    def sample_random_combination(self):
        """Sample a single random feature combination"""
        return self.sample_features(n=1).iloc[0]
    
    def get_matrix_info(self):
        """Get information about the feature matrix"""
        total_combinations = len(self.feature_matrix)
        
        print(f"Irish Feature Matrix Summary:")
        print(f"- Total combinations: {total_combinations:,}")
        print(f"- Persons: {len(self.persons)} ({', '.join(self.persons)})")
        print(f"- Verbs: {len(self.verbs)} ({', '.join(self.verbs)})")
        print(f"- Prepositions: {len(self.prepositions)} ({', '.join(self.prepositions)})")
        print(f"- Cases: {len(self.cases)} ({', '.join(self.cases)})")
        print(f"- Tenses: {len(self.tenses)} ({', '.join(self.tenses)})")
        
        return {
            'total_combinations': total_combinations,
            'persons': self.persons,
            'verbs': self.verbs,
            'prepositions': self.prepositions,
            'cases': self.cases,
            'tenses': self.tenses
        }