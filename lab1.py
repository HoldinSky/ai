# run example
# py lab1.py -x 1000 -y 500 -cr 15 --test
# py lab1.py -x 1000 -y 500 -cr 20 -p 50 -g 120

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

ARGS_WORDS = {"-x", "-y", "-c", "-cr", "-p", "-g", "--test"}

IS_DEFAULT = {
    "x": True,
    "y": True,
    "manual_cities": True,
    "cities_count": True,
    "population": True,
    "generation": True,
}

BEST_BY_POPULATION_SIZE = {}
BEST_BY_GENERATION_COUNT = {}
TEST_POPULATIONS = [i * 10 for i in range(1, 11)]
TEST_GEN_COUNTS = [2 ** i for i in range(15)]
ABSOLUTE_BEST = {}

HELP_STR = """
USAGE: python <filename> -x 500 -y 500 [-cr 20][ -p 50 -g 100| --test]
Arguments:
    -x      Length of the plane
    -y      Height of the plane
    -cr     Count of the randomly generated cities
    -c      Flag followed by coordinates of cities until next flag is encountered or end of the arguments
            (ex: -c 100,50 150,100 200,100 60,175 80,45)
    -p      Number of cities in "population"
    -g      Number of generations
    --test  Flag for running the automated test ("-p" and "-g" flags are ignored). Ignored when "-c" is specified
"""

def print_help_and_halt():
    print(HELP_STR)
    exit(-1)

def set_default_size():
    global MAX_X, MAX_Y, CITIES_COUNT, POPULATION_SIZE, GENERATION_COUNT, TEST

    MAX_X = 500
    MAX_Y = 500
    CITIES_COUNT = 8
    POPULATION_SIZE = 15
    GENERATION_COUNT = 30
    TEST = False
    
def cities_from_coords(coords):
    global CITIES
    CITIES = []
    for coord in coords:
        CITIES.append(coord)
    
def try_set_parameter(flag, value):
    global MAX_X, MAX_Y, CITIES_COUNT, POPULATION_SIZE, GENERATION_COUNT

    try:
        value = int(value)
    except ValueError:
        print(f"ERROR: Failed to parse value for \"{flag}\"")
        print_help_and_halt()

    if flag == "-x":
        MAX_X = value
        if value < 100:
            print("ERROR: Panel's width cannot be less then 100")
            exit(-1)
        IS_DEFAULT["x"] = False
    elif flag == "-y":
        MAX_Y = value
        if value < 100:
            print("ERROR: Panel's height cannot be less then 100")
            exit(-1)
        IS_DEFAULT["y"] = False
    elif flag == "-cr":
        if not IS_DEFAULT["manual_cities"]:
            return
        CITIES_COUNT = value
        IS_DEFAULT["cities_count"] = False
    elif flag == "-p":
        POPULATION_SIZE = value
        IS_DEFAULT["population"] = False
    elif flag == "-g":
        GENERATION_COUNT = value
        IS_DEFAULT["generation"] = False

def parse_args():
    global TEST

    argc = len(sys.argv)
    set_default_size()
    if argc == 1:
        return
    
    if argc == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        print(HELP_STR)
        exit(0)
    
    i = 1
    while i < argc:
        if sys.argv[i] in ARGS_WORDS:
            if sys.argv[i] == "--test":
                TEST = True
            elif sys.argv[i] == "-c":
                i += 1
                if not IS_DEFAULT["cities_count"]:
                    continue

                IS_DEFAULT["manual_cities"] = False
                coords = []
                err = False

                while i < argc:
                    try:
                        x, y = [int(x) for x in sys.argv[i].split(",")]
                        if x < 0 or y < 0:
                            print("ERROR: Point's coordinates must be greater or equal to 0")
                            exit(-1)
                        coords.append((x, y))
                    except:
                        if sys.argv[i] in ARGS_WORDS:
                            i -= 1
                        else:
                            err = True
                        break
                    i += 1
                if err:
                    print("ERROR: Failed to parse list of coordinates after \"-c\"")
                    exit(-1)

                cities_from_coords(coords)
            elif i < argc - 1:        
                try_set_parameter(sys.argv[i], sys.argv[i+1])
                i += 1
        i += 1
        
    if not IS_DEFAULT["manual_cities"]:
        for x, y in CITIES:
            if x > MAX_X:
                print("ERROR: Manually set point is beyond plane's width")
                exit(-1)
            if y > MAX_Y:
                print("ERROR: Manually set point is beyond plane's height")
                exit(-1)
    
    print("Program parameters")
    print(f"\tPlane: {MAX_X} wide{" (default)" if IS_DEFAULT["x"] else ""}, {MAX_Y} high{" (default)" if IS_DEFAULT["y"] else ""}")
    if IS_DEFAULT["manual_cities"]:
        print(f"\tCities count: {CITIES_COUNT}{" (default)" if IS_DEFAULT["cities_count"] else ""}")
    else:
        print(f"\tCities: {CITIES}")
    print(f"\tPopulation size: {POPULATION_SIZE}{" (default)" if IS_DEFAULT["population"] else ""}")
    print(f"\tGeneration count: {GENERATION_COUNT}{" (default)" if IS_DEFAULT["generation"] else ""}")
    print()
    
    if POPULATION_SIZE > 2 ** ((CITIES_COUNT-1) if IS_DEFAULT["manual_cities"] else len(CITIES)-1):
        print("ERROR: Population size must be less then 2 to power of (Cities count - 1)")
        exit(-1)

#########################################################################
#########################################################################

def generate_coords(max_x, max_y):
    return (random.randint(0, max_x), random.randint(0, max_y))

def generate_cities(count):
    cities = []
    for _ in range(count):
        city = generate_coords(MAX_X, MAX_Y)
        while city in cities:
            city = generate_coords(MAX_X, MAX_Y)
        cities.append(city)

    return cities

def calculate_distance(city1, city2):
    x1, y1 = city1
    x2, y2 = city2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_route_length(route):
    total = 0
    for i in range(len(route) - 1):
        total += calculate_distance(route[i], route[i+1])
    
    return total

def build_route():
    # випадково вибрати точки зі списку "cities"
    remaining = CITIES[1:]
    random.shuffle(remaining)

    return tuple([CITIES[0]] + remaining + [CITIES[0]])

# створити нові або додати до існуючих шляхи між містами
def build_routes(count, routes):
    hashes = set(route["hash"] for route in routes)
    
    for _ in range(count):
        route = build_route()
        route_hash = hash(route)
        
        # захист від повторних шляхів
        while route_hash in hashes:
            route = build_route()
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
        print(f"Population size: {len(population)}")
    else:
        print(f"Best route: {best_route["route"]}")

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
    global CITIES, TEST
    parse_args()
    TEST = TEST and IS_DEFAULT["manual_cities"]
    
    # ініціювання першого покоління
    # кожен елемент списку "population" має такі поля:
    # route - tuple координат міст в маршруті (починається і закінчується одним містом)
    # length - загальна довжина маршруту (сума відстаней між точками в route)
    # hash - службове значення, необхідне для уникання повторних маршрутів у колекції
    initial_population = []
    
    if IS_DEFAULT["manual_cities"]:
        CITIES = generate_cities(CITIES_COUNT)

    build_routes(POPULATION_SIZE, initial_population)
    initial_population = sorted(initial_population, key=lambda x: x["length"])

    if TEST:
        test_program()
    else:
        program(initial_population, GENERATION_COUNT)
    

if __name__ == "__main__":
    main()