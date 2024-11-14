def calculate_ctr(clicks, impressions):
    return clicks / impressions if impressions > 0 else 0

def calculate_map(precision_at_k):
    return sum(precision_at_k) / len(precision_at_k)

if __name__ == "__main__":
    # Example usage
    ctr = calculate_ctr(100, 1000)
    map_score = calculate_map([0.5, 0.6, 0.7])
    print(f"CTR: {ctr}, MAP: {map_score}")
