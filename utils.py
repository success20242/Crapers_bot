def clean_predictions(pred_list):
    unique = list(set(pred_list))
    filtered = [p for p in unique if 10 < len(p) < 400]
    return filtered
