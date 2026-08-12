class DynamicInterviewerAgent:
    def __init__(self, resume_context: str):
        self.context = resume_context
        self.turn_count = 0

    def generate_first_question(self) -> str:
        self.turn_count += 1
        return "I see your repository features multi-agent frameworks. Walk me through how you handle memory across turns."

    def process_turn(self, candidate_transcript: str):
        self.turn_count += 1
        evaluation = {"score": 9.5, "reasoning": "Candidate demonstrated clear understanding."}
        
        next_question = "Great. How do you implement guardrails against prompt injection?"
        if self.turn_count >= 2:
            next_question = "TERMINATE" # Triggers the negotiation phase
            
        return evaluation, next_question