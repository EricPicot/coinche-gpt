# Ordre des cartes (du plus fort au plus faible)
CARD_ORDER = {
    'trump': ['jack', '9', 'ace', '10', 'king', 'queen', '8', '7'],
    'normal': ['ace', '10', 'king', 'queen', 'jack', '9', '8', '7']
}

# Points des cartes
CARD_POINTS = {
    'trump': {
        'jack': 20,
        '9': 14,
        'ace': 11,
        '10': 10,
        'king': 4,
        'queen': 3,
        '8': 0,
        '7': 0
    },
    'normal': {
        'ace': 11,
        '10': 10,
        'king': 4,
        'queen': 3,
        'jack': 2,
        '9': 0,
        '8': 0,
        '7': 0
    }
}

# Normalisation des valeurs de cartes (tout en minuscules)
CARD_VALUES_NORMALIZED = {
    'Ace': 'ace',
    'King': 'king',
    'Queen': 'queen',
    'Jack': 'jack',
    'ace': 'ace',
    'king': 'king',
    'queen': 'queen',
    'jack': 'jack',
    '10': '10',
    '9': '9',
    '8': '8',
    '7': '7'
}

def verify_card_consistency():
    """Vérifie la cohérence des constantes de cartes"""
    import logging
    
    # Vérifier que toutes les cartes dans CARD_ORDER sont dans CARD_POINTS
    for game_type in ['trump', 'normal']:
        for card in CARD_ORDER[game_type]:
            if card not in CARD_POINTS[game_type]:
                logging.error(f"Carte {card} dans CARD_ORDER mais pas dans CARD_POINTS pour {game_type}")
                return False
    
    # Vérifier que toutes les cartes dans CARD_POINTS sont dans CARD_ORDER
    for game_type in ['trump', 'normal']:
        for card in CARD_POINTS[game_type]:
            if card not in CARD_ORDER[game_type]:
                logging.error(f"Carte {card} dans CARD_POINTS mais pas dans CARD_ORDER pour {game_type}")
                return False
    
    # Vérifier la normalisation
    test_cards = [
        ('Ace of hearts', 'ace of hearts'),
        ('King of spades', 'king of spades'),
        ('10 of diamonds', '10 of diamonds'),
        ('8 of clubs', '8 of clubs')
    ]
    
    for original, expected in test_cards:
        value = original.split(' of ')[0]
        suit = original.split(' of ')[1]
        if value in CARD_VALUES_NORMALIZED:
            normalized = f"{CARD_VALUES_NORMALIZED[value]} of {suit}"
        else:
            normalized = original.lower()
        
        if normalized != expected:
            logging.error(f"Erreur de normalisation: {original} -> {normalized} (attendu: {expected})")
            return False
    logging.info("Toutes les vérifications de cartes sont OK!")
    return True

# Exécuter la vérification au démarrage
if __name__ == "__main__":
    verify_card_consistency()