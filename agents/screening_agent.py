class ScreeningAgent:
    def __init__(self, job_description: str, target_department: str = "General"):
        self.jd = job_description
        self.department = target_department

    def evaluate_resume(self, resume_text: str) -> dict:
        """Evaluates resume text against any department's Job Description."""
        if not resume_text or len(resume_text) < 50:
            return {
                "score": 0.0,
                "passed": False,
                "feedback": "Invalid or unreadable resume document."
            }

        # Extracts keywords from the target JD to calculate match percentage
        jd_words = set(self.jd.lower().split())
        resume_words = set(resume_text.lower().split())
        
        # Calculate overlap ratio
        overlap = jd_words.intersection(resume_words)
        match_score = round(min(100.0, (len(overlap) / max(1, len(jd_words))) * 250), 1)

        passed = match_score >= 65.0

        return {
            "department": self.department,
            "score": match_score,
            "passed": passed,
            "feedback": (
                f"Qualified candidate for {self.department} position." 
                if passed 
                else f"Missing key qualifications required for {self.department} role."
            )
        }