def consensus(nodes_outputs):
    """
    🔁 Consensus Engine : Valide une décision via un vote majoritaire.
    C'est la 'blockchain mentale' d'AGIcore pour éviter les hallucinations IA isolées.
    """
    if not nodes_outputs:
        return None

    votes = {}
    for output in nodes_outputs:
        votes[output] = votes.get(output, 0) + 1

    # On retourne la décision ayant reçu le plus de votes
    winner = max(votes, key=votes.get)
    print(f"🤝 [CONSENSUS] Décision validée par vote : {winner} ({votes[winner]} voix)")
    return winner
