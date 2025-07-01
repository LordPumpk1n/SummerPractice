from random import random, uniform, choices, randint, gauss
import matplotlib.pyplot as plt

def generate_point(left, down, right, up):
    x = uniform(left,right)
    y = uniform(down,up)
    return Point(x, y)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Square():
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.points = None

    def bottom_left(self):
        return Point(self.x,self.y)

    def top_right(self):
        return Point(self.x + self.size, self.y + self.size)

    def find_inner_points(self, points):
        return [p for p in points if self.contains(p)]

    def contains(self, point):
        return self.x < point.x < self.x + self.size and self.y < point.y < self.y + self.size

    def intersects(self, other):
        return not (self.x + self.size <= other.x or other.x + other.size <= self.x or
                    self.y + self.size <= other.y or other.y + other.size <= self.y)

class Population:
    def __init__(self, individuals):
        self.individuals = individuals

    def fitness(self, individual, full_area):
        score = 0
        empty_count = 0
        for square in individual:
            score += len(square.points) * (1 - (square.size ** 2) / full_area)
            if len(square.points) == 0:
                empty_count+=1
        score /= (empty_count+1)
        return score

    def select_individual(self, full_area):
        fits = [self.fitness(ind, full_area) for ind in self.individuals]
        total = sum(fits)
        if total == 0:
            return random.choice(self.individuals)
        probs = [f / total for f in fits]
        return choices(self.individuals, weights=probs, k=1)[0]

class GeneticAlg():
    def __init__(self, population_size, squares_num, points, elite_fraction, crossover_prob, mutation_prob):
        self.__population_size = population_size
        self.__squares_num = squares_num
        self.__points = points
        self.__elite_fraction = elite_fraction
        self.__crossover_prob = crossover_prob
        self.__mutation_prob = mutation_prob
        self.__full_area = None

    def perform_step(self, population = None):
        if population is None:
            pop = self.__make_start_population()
        else:
            pop = self.__evolve_population(population)
        fitnesses = [pop.fitness(ind, self.__full_area) for ind in pop.individuals]
        mean_fit = sum(fitnesses) / len(fitnesses)
        max_fit = max(fitnesses)
        return pop, mean_fit, max_fit

    def crossover(self, parent1, parent2):
        new_parent1 = []
        new_parent2 = []
        for gene_ind in range(len(parent1)):
            gene1, gene2 = parent1[gene_ind], parent2[gene_ind]
            if randint(0,1):
                gene1, gene2 = gene2, gene1
            new_parent1.append(gene1)
            new_parent2.append(gene2)
        return [new_parent1, new_parent2]

    def mutate(self, individual):
        mutated = []
        for sq in individual:
            sigma = sq.size * 0.1 # 10% от размера квадрата
            new_x = gauss(sq.x, sigma)
            new_y = gauss(sq.y, sigma)
            new_size = max(0.001, gauss(sq.size, sigma))
            new_square = Square(new_x, new_y, new_size)
            new_square.points = new_square.find_inner_points(self.__points)
            mutated.append(new_square)
        return mutated

    def fix_intersections(self, individuals):
        def handle_left_bottom(outer, inner, eps=1e-6):
            bl_in = inner.bottom_left()
            tr_in = inner.top_right()

            dx = bl_in.x - outer.x
            dy = bl_in.y - outer.y
            outer.size = max(0.001, min(dx, dy) - eps)

            if outer.contains(tr_in):
                max_w = outer.x + outer.size - inner.x - eps
                max_h = outer.y + outer.size - inner.y - eps
                inner.size = max(inner.size, min(max_w, max_h))
                inner.points = inner.find_inner_points(inner.points + outer.points)

            outer.points = outer.find_inner_points(outer.points)
            return outer, inner

        eps = 1e-6
        min_size = 0.001
        for ind in individuals:
            for i in range(len(ind)):
                for j in range(i + 1, len(ind)):
                    sq1, sq2 = ind[i], ind[j]
                    if not sq1.intersects(sq2):
                        continue

                    bl1, tr1 = sq1.bottom_left(), sq1.top_right()
                    bl2, tr2 = sq2.bottom_left(), sq2.top_right()

                    if sq2.contains(bl1):
                        ind[j], ind[i] = handle_left_bottom(sq2, sq1, eps)
                        continue

                    if sq1.contains(bl2):
                        ind[i], ind[j] = handle_left_bottom(sq1, sq2, eps)
                        continue

                    base1 = sq1.points
                    base2 = sq2.points
                    step = min(sq1.size, sq2.size) * 0.1 # Уменьшаем на 0.1 от меньшего из размеров пока не перестанут пересекаться

                    tmp1 = Square(sq1.x, sq1.y, sq1.size)
                    while tmp1.intersects(sq2) and tmp1.size > min_size:
                        tmp1.size = max(min_size, tmp1.size - step)
                    tmp1.points = tmp1.find_inner_points(base1)

                    tmp2 = Square(sq2.x, sq2.y, sq2.size)
                    while sq1.intersects(tmp2) and tmp2.size > min_size:
                        tmp2.size = max(min_size, tmp2.size - step)
                    tmp2.points = tmp2.find_inner_points(base2)

                    if tmp1.intersects(sq2):
                        # tmp1 даже с min_size всё ещё пересекается — считаем вложенным
                        tmp1.y += (min_size*2)  # поднимаем чуть-чуть
                        ind[j], ind[i] = handle_left_bottom(sq2, tmp1, eps)
                        continue

                    if sq1.intersects(tmp2):
                        tmp2.y += eps
                        ind[i], ind[j] = handle_left_bottom(sq1, tmp2, eps)
                        continue

                    fit1 = len(tmp1.points) + len(base2)
                    fit2 = len(base1) + len(tmp2.points)
                    if fit1 > fit2:
                        ind[i] = tmp1
                    else:
                        ind[j] = tmp2
        return individuals

    def __make_start_population(self):
        left, right, down, up = self.__find_bounds()
        self.__full_area = (right - left) * (up-down)
        population_arr = []

        for _ in range(self.__population_size):
            squares = []
            for _ in range(self.__squares_num):
                attempts = 0
                while True:
                    attempts += 1
                    if attempts > 100:
                        break
                    point = generate_point(left, down, right, up)
                    max_possible_size = min(right - point.x, up - point.y)
                    if max_possible_size <= 0:
                        continue

                    size = uniform(0.01, max_possible_size)
                    ok = True

                    test_square = Square(point.x, point.y, size)
                    for other in squares:
                        if other.contains(point):
                            ok = False
                            break
                        while test_square.intersects(other):
                            size *= 0.9
                            if size < 0.001:
                                ok = False
                                break
                            test_square.size = size
                        if not ok:
                            break

                    if ok:
                        new_sq = Square(point.x, point.y, size)
                        new_sq.points = new_sq.find_inner_points(self.__points)
                        squares.append(new_sq)
                        break

            population_arr.append(squares)

        return Population(self.fix_intersections(population_arr))

    def __evolve_population(self, population):

        sorted_inds = sorted(population.individuals, key=lambda ind: population.fitness(ind, self.__full_area), reverse=True)
        elite_count = int(self.__elite_fraction * self.__population_size)
        new_gen = sorted_inds[:elite_count]

        while len(new_gen) < self.__population_size:
            p1 = population.select_individual(self.__full_area)
            p2 = population.select_individual(self.__full_area)
            if random() < self.__crossover_prob:
                children = self.crossover(p1, p2)
            else:
                children = [p1.copy(), p2.copy()]
            for ch in children:
                if random() < self.__mutation_prob:
                    ch = self.mutate(ch)
                new_gen.append(ch)
                if len(new_gen) >= self.__population_size:
                    break
        return Population(self.fix_intersections(new_gen))

    def __find_bounds(self):
        left = min(p.x for p in self.__points)
        right = max(p.x for p in self.__points)
        down = min(p.y for p in self.__points)
        up = max(p.y for p in self.__points)

        x_len = right - left
        y_len = up - down

        add_x = x_len * 0.2
        add_y = y_len * 0.2
        left -= add_x
        right += add_x
        down -= add_y
        up += add_y
        return left, right, down, up

def run_full_evolution(points_count=40, squares_count=10, population_size=200, generations=100,
                       elite_fraction=0.1, crossover_prob=0.5, mutation_prob=0.3):
    points = [generate_point(-100, -100, 100, 100) for _ in range(points_count)]

    ga = GeneticAlg(population_size=population_size,
                    squares_num=squares_count,
                    points=points,
                    elite_fraction=elite_fraction,
                    crossover_prob=crossover_prob,
                    mutation_prob=mutation_prob)

    population = None
    fitness_progress = []
    mean_progress = []

    for gen in range(1, generations + 1):
        population, mean_fit, max_fit = ga.perform_step(population)
        fitness_progress.append(max_fit)
        mean_progress.append(mean_fit)

        if gen % 20 == 0:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_title(f"Поколение {gen}")
            bounds = ga._GeneticAlg__find_bounds()
            ax.set_xlim(bounds[0], bounds[1])
            ax.set_ylim(bounds[2], bounds[3])

            xs = [p.x for p in points]
            ys = [p.y for p in points]
            ax.scatter(xs, ys, c='black', s=10, label='Points')

            best_fitnesses = [population.fitness(ind, (bounds[1] - bounds[0]) * (bounds[3] - bounds[2]))
                              for ind in population.individuals]
            best_ind = population.individuals[best_fitnesses.index(max(best_fitnesses))]

            for sq in best_ind:
                rect = plt.Rectangle((sq.x, sq.y), sq.size, sq.size,
                                     edgecolor='red', facecolor='orange', alpha=0.4)
                ax.add_patch(rect)
            plt.grid(True)
            plt.show()

    plt.figure(figsize=(8, 5))
    plt.plot(range(1, generations + 1), fitness_progress, color='blue', label='Максимальная приспособленность')
    plt.plot(range(1, generations + 1), mean_progress, color='green', linestyle='--', label='Средняя приспособленность')
    plt.title('Функция приспособленности')
    plt.xlabel('Поколение')
    plt.ylabel('Приспособленность')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

run_full_evolution()