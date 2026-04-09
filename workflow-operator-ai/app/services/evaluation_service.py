def evaluate_decision(decision: dict):
    score = 0

    if decision.get("qualified"):
        score += 5
    else:
        score += 1

    if decision.get("score", 0) > 70:
        score += 2
    else:
        score += 1

    if decision.get("confidence", 0) > 0.7:
        score += 3
    else:
        score += 1

    return {
        "score": score,
        "details": {
            "qualified": decision.get("qualified"),
            "score": decision.get("score"),
            "confidence": decision.get("confidence")
        }
    }


def evaluate_email(email: dict):
    score = 0

    body = email.get("email_body", "")

    if len(body) > 120:
        score += 3
    else:
        score += 1

    if "you" in body.lower():
        score += 2
    else:
        score += 1

    if "we" in body.lower():
        score += 2
    else:
        score += 1

    if email.get("subject"):
        score += 2
    else:
        score += 1

    return {
        "score": score,
        "details": {
            "length": len(body),
            "has_subject": bool(email.get("subject"))
        }
    }