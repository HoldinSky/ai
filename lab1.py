# run example
# py lab1.py -x 1000 -y 500 -c 15 --test
# py lab1.py -x 1000 -y 500 -c 20 -p 50 -g 120

import random
import sys
import os
import math

MAX_X: int
MAX_Y: int
CITIES_COUNT: int
POPULATION_SIZE: int
GENERATION_COUNT: int
TEST: bool
CITIES: list

ARGS_WORDS = {"-x", "-y", "-c", "-p", "-g", "--test"}

IS_DEFAULT = {
    "x": True,
    "y": True,
    "cities": True,
    "population": True,
    "generation": True,
}

BEST_BY_POPULATION_SIZE = {}
BEST_BY_GENERATION_COUNT = {}
TEST_POPULATIONS = [i * 10 for i in range(1, 11)]
TEST_GEN_COUNTS = [2 ** i for i in range(15)]
ABSOLUTE_BEST = {}

def set_default_size():
    global MAX_X, MAX_Y, CITIES_COUNT, POPULATION_SIZE, GENERATION_COUNT, TEST

    MAX_X = 500
    MAX_Y = 500
    CITIES_COUNT = 8
    POPULATION_SIZE = 15
    GENERATION_COUNT = 30
    TEST = False
    
def try_set_parameter(tag, value):
    global MAX_X, MAX_Y, CITIES_COUNT, POPULATION_SIZE, GENERATION_COUNT

    try:
        value = int(value)
    except ValueError:
        print(f"Failed to parse value for \"{tag}\"")
        os._exit(-1)

    if tag == "-x":
        MAX_X = value
        IS_DEFAULT["x"] = False
    elif tag == "-y":
        MAX_Y = value
        IS_DEFAULT["y"] = False
    elif tag == "-c":
        CITIES_COUNT = value
        IS_DEFAULT["cities"] = False
    elif tag == "-p":
        POPULATION_SIZE = value
        IS_DEFAULT["population"] = False
    elif tag == "-g":
        GENERATION_COUNT = value
        IS_DEFAULT["generation"] = False

def parse_args():
    global TEST

    argc = len(sys.argv)
    set_default_size()
    if argc == 1:
        return
    
    i = 1
    while i < argc:
        if sys.argv[i] in ARGS_WORDS:
            if sys.argv[i] == "--test":
                TEST = True
            elif i < argc - 1:        
                try_set_parameter(sys.argv[i], sys.argv[i+1])
                i += 1

        i += 1
    
    print("Program parameters")
    print(f"\tPlane: {MAX_X} wide{" (default)" if IS_DEFAULT["x"] else ""}, {MAX_Y} high{" (default)" if IS_DEFAULT["y"] else ""}")
    print(f"\tCities count: {CITIES_COUNT}{" (default)" if IS_DEFAULT["cities"] else ""}")
    print(f"\tPopulation size: {POPULATION_SIZE}{" (default)" if IS_DEFAULT["population"] else ""}")
    print(f"\tGeneration count: {GENERATION_COUNT}{" (default)" if IS_DEFAULT["generation"] else ""}")
    print()
    
    if POPULATION_SIZE > 2 ** (CITIES_COUNT-1):
        print("Population size must be less then 2 to power of (Cities count - 1)")
        os._exit(-1)

#########################################################################
#########################################################################

def generate_coords(max_x, max_y):
    return (random.randint(0, max_x), random.randint(0, max_y))

def generate_cities(count):
    return [generate_coords(MAX_X, MAX_Y) for _ in range(count)]

def calculate_distance(city1, city2):
    x1, y1 = city1
    x2, y2 = city2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_route_length(route):
    total = 0
    for i in range(len(route) - 1):
        total += calculate_distance(route[i], route[i+1])
    
    return total

def build_route(cities):
    # випадково вибрати точки зі списку "cities"
    remaining = cities[1:]
    random.shuffle(remaining)

    return tuple([cities[0]] + remaining + [cities[0]])

# створити нові або додати до існуючих шляхи між містами
def build_routes(count, routes):
    hashes = set(route["hash"] for route in routes)
    
    for _ in range(count):
        route = build_route(CITIES)
        route_hash = hash(route)
        
        # захист від повторних шляхів
        while route_hash in hashes:
            route = build_route(CITIES)
            route_hash = hash(route)
            
        hashes.update([route_hash])

        route_length = calculate_route_length(route)
        routes.append({"route": route, "length": route_length, "hash": route_hash})

# алгоритм одноточкового кросинговеру
def crossover(route1, route2):
    n = len(route1)
    divide_point = random.randint(0, n - 1)
    child_route = []
    
    for i in range(divide_point):
        child_route.append(route1[i])
    
    for i in range(divide_point, n):
        if route2[i] not in child_route:
            child_route.append(route2[i])
    
    if len(child_route) == n:
        return child_route
        
    for i in range(divide_point, n):
        if route1[i] not in child_route:
            child_route.append(route1[i])
    
    child_route.append(child_route[0])
    return tuple(child_route)

def pick_parents(population):
    population_len = len(population)
    ind1 = random.randint(0, population_len - 1)
    ind2: int

    if ind1 == population_len - 1:
        ind2 = ind1 - 1
    else:
        ind2 = ind1 + 1
    
    return population[ind1], population[ind2]

def create_child(population):
    # вибір осіб для кросинговеру
    p1, p2 = pick_parents(population)

    child = crossover(p1["route"], p2["route"])
    _hash = hash(child)
    
    while _hash == p1["hash"] or _hash == p2["hash"]:
        p1, p2 = pick_parents(population)
        child = crossover(p1["route"], p2["route"])
        _hash = hash(child)
        
    return {"route": child, "length": calculate_route_length(child), "hash": _hash}    

def program(_population, gen_count):
    population = _population.copy()
    for _ in range(gen_count):
        new_route = create_child(population)

        population.pop()
        population.pop()
        population.append(new_route)
        
        build_routes(1, population)
        population = sorted(population, key=lambda ind: ind["length"])
    
    best_route = population[0]
    
    if TEST:
        print()
        print(f"Generation count: {gen_count}")
    else:
        print(f"Best route: {best_route["route"]}")
    print(f"Population size: {len(population)}")
    print(f"Total length: {best_route["length"]:.2f}")

    update_test_data(gen_count, len(population), best_route["length"])

def update_test_data(gen_count, population_size, curr_len):
    global ABSOLUTE_BEST

    best = BEST_BY_GENERATION_COUNT.get(gen_count)
    if best is None or curr_len < best["len"]:
        BEST_BY_GENERATION_COUNT.update({gen_count: {"len": curr_len, "population": population_size}})

    best = BEST_BY_POPULATION_SIZE.get(population_size)
    if best is None or curr_len < best["len"]:
        BEST_BY_POPULATION_SIZE.update({population_size: {"len": curr_len, "generation": gen_count}})
    
    best_len = ABSOLUTE_BEST.get("len")
    if best_len is None or curr_len < best_len:
        ABSOLUTE_BEST = {"len": curr_len, "generation": gen_count, "population": population_size}

def test_program():
    for population_size in TEST_POPULATIONS:
        initial_population = []
        build_routes(population_size, initial_population)
        initial_population = sorted(initial_population, key=lambda x: x["length"])
        
        for gen_count in TEST_GEN_COUNTS:
            program(initial_population, gen_count)
        
    print("\n\nBest py population size")
    for population_size in TEST_POPULATIONS:
        best = BEST_BY_POPULATION_SIZE[population_size]
        print(f"\t{population_size:5}: {best["len"]:8.2f} (generations={best["generation"]})")
    
    print("\nBest py generations count")
    for gen_count in TEST_GEN_COUNTS:
        best = BEST_BY_GENERATION_COUNT[gen_count]
        print(f"\t{gen_count:5}: {best["len"]:8.2f} (population={best["population"]})")
    
    print(f"\nAbsolute best{ABSOLUTE_BEST["len"]:8.2f} (generations={ABSOLUTE_BEST["generation"]}, population={ABSOLUTE_BEST["population"]})")

def main():
    global CITIES
    parse_args()
    
    # ініціювання першого покоління
    # кожен елемент списку "population" має такі поля:
    # route - tuple координат міст в маршруті (починається і закінчується одним містом)
    # length - загальна довжина маршруту (сума відстаней між точками в route)
    # hash - службове значення, необхідне для уникання повторних маршрутів у колекції
    initial_population = []
    
    CITIES = generate_cities(CITIES_COUNT)
    build_routes(POPULATION_SIZE, initial_population)
    initial_population = sorted(initial_population, key=lambda x: x["length"])

    if not TEST:
        program(initial_population, GENERATION_COUNT)
    else:
        test_program()
    

if __name__ == "__main__":
    main()