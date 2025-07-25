
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import random
import json

app = FastAPI()

origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

with open("full_plan.json", "r") as f:
    plan = json.load(f)

@app.post("/recommend")
async def recommend_courses(request: Request):
    data = await request.json()
    taken = set(data.get("taken", []))
    offered = data.get("offered", [])
    max_hours = data.get("max_hours", 18)

    population = [random.sample(offered, min(len(offered), 5)) for _ in range(30)]

    def fitness(individual):
        score = 0
        total_hours = 0
        seen_times = set()

        for subject in individual:
            info = plan.get(subject)
            if not info:
                continue
            if any(prereq not in taken for prereq in info["prerequisites"]):
                score -= 5
                continue
            if info["time"] in seen_times:
                score -= 10
                continue
            seen_times.add(info["time"])
            total_hours += info["hours"]
            if subject.startswith("COMP3") or subject.startswith("GRAD"):
                score += 3
        if total_hours > max_hours:
            score -= (total_hours - max_hours) * 2
        else:
            score += total_hours
        return score

    for _ in range(30):
        scored = sorted(population, key=fitness, reverse=True)
        next_gen = scored[:10]
        while len(next_gen) < 30:
            p1, p2 = random.sample(scored[:20], 2)
            cut = random.randint(1, min(len(p1), len(p2)) - 1)
            child = list(set(p1[:cut] + p2[cut:]))
            if len(child) > 0:
                next_gen.append(child)
        population = next_gen

    best = max(population, key=fitness)
    return {"recommendations": best}
