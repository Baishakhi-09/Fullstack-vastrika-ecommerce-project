class AIShippingOptimizer:
    @staticmethod
    def recommend_best_courier(rates):

        cheapest = min(
            rates,
            key=lambda item: item["price"],
        )

        fastest = min(
            rates,
            key=lambda item: item["delivery_days"],
        )

        return {
            "cheapest": cheapest,
            "fastest": fastest,
        }