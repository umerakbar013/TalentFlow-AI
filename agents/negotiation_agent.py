class SalaryNegotiationEngine:
    def __init__(self):
        self.max_ceiling = 95000.0
        self.current_offer = 80000.0
        self.rounds = 0

    def process_demand(self, demand: float) -> dict:
        self.rounds += 1
        if demand > self.max_ceiling:
            if self.rounds >= 3:
                return {"action": "TERMINATE", "amount": self.current_offer, "msg": f"Our absolute ceiling is ${self.current_offer:,.2f}."}
            
            self.current_offer = min(self.current_offer + 5000, self.max_ceiling)
            return {"action": "COUNTER", "amount": self.current_offer, "msg": f"That exceeds our budget limit. We can counter with ${self.current_offer:,.2f}."}
        
        return {"action": "ACCEPT", "amount": demand, "msg": f"Agreed. We accept your target of ${demand:,.2f}."}