import random

# ---------------------------------------------------------
# FINANCE FACT GENERATOR
# ---------------------------------------------------------

def generate_finance_fact():
    """
    Generates a short, structured finance fact for YouTube Shorts.
    Output is always under ~40 words and follows the 4-part format:
    - hook
    - fact
    - explanation
    - curiosity
    """

    hooks = [
        "Most people never learn this money trick.",
        "Rich people do this without thinking.",
        "This simple habit builds wealth fast.",
        "Your bank hopes you never find this out.",
        "This one change can grow your savings."
    ]

    facts = [
        "Paying yourself first is the fastest way to build wealth.",
        "Tracking every dollar makes people save 30% more.",
        "High‑interest debt destroys long‑term financial growth.",
        "Investing early beats investing more later.",
        "Small daily expenses compound into huge losses."
    ]

    explanations = [
        "It forces your brain to treat saving like a bill.",
        "Awareness alone changes spending behavior instantly.",
        "Interest grows faster than most people can pay it down.",
        "Time in the market multiplies gains automatically.",
        "Tiny habits compound just like money does."
    ]

    curiosity = [
        "Most people ignore this—do you?",
        "Try it for one week and watch what happens.",
        "This is why the wealthy stay wealthy.",
        "Your future self will thank you.",
        "This works no matter your income."
    ]

    return {
        "hook": random.choice(hooks),
        "fact": random.choice(facts),
        "explanation": random.choice(explanations),
        "curiosity": random.choice(curiosity)
    }
