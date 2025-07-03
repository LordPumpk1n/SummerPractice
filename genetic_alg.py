from random import random, uniform, choices, randint, gauss, choice

def generate_point(left, down, right, up):
    x = uniform(left,right)
    y = uniform(down,up)
    return Point(x, y)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Square():
    def __init__(self, x, y, size, points=None):
        self.x = x
        self.y = y
        self.size = size
        self.points = points

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

    def select_individual(self, type):
        if type == 1:
            return self.__roulette_selection()
        if type == 2:
            return self.__tournament_selection()

    def fix_intersections(self):
        def handle_left_bottom(outer, inner, eps=1e-6):
            bl_in = inner.bottom_left()
            tr_in = inner.top_right()

            dx = bl_in.x - outer.x
            dy = bl_in.y - outer.y
            outer.size = max(0.001, min(dx, dy))

            if outer.contains(tr_in):
                max_w = outer.x + outer.size - inner.x - eps
                max_h = outer.y + outer.size - inner.y - eps
                inner.size = max(inner.size, min(max_w, max_h))
                inner.points = inner.find_inner_points(inner.points + outer.points)

            outer.points = outer.find_inner_points(outer.points)
            return outer, inner

        eps = 1e-6
        min_size = 0.001
        for ind in self.individuals:
            for i in range(len(ind.squares)):
                for j in range(i + 1, len(ind.squares)):
                    sq1, sq2 = ind.squares[i], ind.squares[j]
                    if not sq1.intersects(sq2):
                        continue

                    bl1, tr1 = sq1.bottom_left(), sq1.top_right()
                    bl2, tr2 = sq2.bottom_left(), sq2.top_right()

                    if sq2.contains(bl1):
                        ind.squares[j], ind.squares[i] = handle_left_bottom(sq2, sq1, eps)
                        continue

                    if sq1.contains(bl2):
                        ind.squares[i], ind.squares[j] = handle_left_bottom(sq1, sq2, eps)
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
                        ind.squares[j], ind.squares[i] = handle_left_bottom(sq2, tmp1, eps)
                        continue

                    if sq1.intersects(tmp2):
                        tmp2.y += eps
                        ind.squares[i], ind.squares[j] = handle_left_bottom(sq1, tmp2, eps)
                        continue

                    fit1 = len(tmp1.points) + len(base2)
                    fit2 = len(base1) + len(tmp2.points)
                    if fit1 > fit2:
                        ind.squares[i] = tmp1
                    else:
                        ind.squares[j] = tmp2

    def __roulette_selection(self):
        fits = [ind.fitness() for ind in self.individuals]
        total = sum(fits)
        if total == 0:
            return choice(self.individuals)
        probs = [f / total for f in fits]
        return choices(self.individuals, weights=probs, k=1)[0]

    def __tournament_selection(self, k=8):
        tournament = [choice(self.individuals) for _ in range(len(self.individuals)//10)]
        return max(tournament, key=lambda ind: ind.fitness())


class Solution():
    def __init__(self, squares_arr):
        self.squares = squares_arr

    def copy(self):
        return Solution([Square(sq.x, sq.y, sq.size, sq.points) for sq in self.squares])

    def fitness(self):
        score = 0
        empty_count = 0
        for square in self.squares:
            score += len(square.points)
            if len(square.points) == 0:
                empty_count+=1
        score /= 2**empty_count
        return score

class GeneticAlg():
    def __init__(self, population_size, squares_num, points, selection_type, elite_fraction, crossover_prob, mutation_prob):
        self.__population_size = population_size
        self.__squares_num = squares_num
        self.__points = points
        self.__selection_type = selection_type
        self.__elite_fraction = elite_fraction
        self.__crossover_prob = crossover_prob
        self.__mutation_prob = mutation_prob
        self.__populations = []

    def get_solution(self, index):
        if index > len(self.__populations) or index < 0:
            raise IndexError(f"Неверный индекс{index} / {len(self.__populations)}")

        if len(self.__populations) == 0:
            self.__make_start_population()

        elif index == len(self.__populations):
            self.__evolve_population(self.__populations[-1])

        pop = self.__populations[index]
        sorted_individuals = sorted(
            pop.individuals, key=lambda ind: ind.fitness(), reverse=True)
        fitnesses = [ind.fitness() for ind in pop.individuals]
        mean_fit = sum(fitnesses) / len(fitnesses)
        max_fit = max(fitnesses)
        return Population(sorted_individuals), mean_fit, max_fit

    def crossover(self, parent1, parent2):
        new_parent1 = Solution([])
        new_parent2 = Solution([])
        for gene_ind in range(len(parent1.squares)):
            gene1, gene2 = parent1.squares[gene_ind], parent2.squares[gene_ind]
            if randint(0,1):
                gene1, gene2 = gene2, gene1
            new_parent1.squares.append(gene1)
            new_parent2.squares.append(gene2)
        return [new_parent1, new_parent2]

    def mutate(self, individual):
        mutated = []
        for sq in individual.squares:
            sigma = sq.size * 0.3  # 30% от размера квадрата
            new_x = gauss(sq.x, sigma)
            new_y = gauss(sq.y, sigma)
            new_size = max(0.001, gauss(sq.size, sigma))
            new_square = Square(new_x, new_y, new_size)
            new_square.points = new_square.find_inner_points(self.__points)
            mutated.append(new_square)
        return Solution(mutated)

    def __make_start_population(self):
        left, right, down, up = self.__find_bounds()
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
            population_arr.append(Solution(squares))
        population = Population(population_arr)
        population.fix_intersections()
        self.__populations.append(population)

    def __evolve_population(self, population):
        sorted_inds = sorted(population.individuals, key=lambda ind: ind.fitness(), reverse=True)
        elite_count = int(self.__elite_fraction * self.__population_size)
        new_gen = sorted_inds[:elite_count]

        while len(new_gen) < self.__population_size:
            p1 = population.select_individual(self.__selection_type)
            p2 = population.select_individual(self.__selection_type)
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
        new_population = Population(new_gen)
        new_population.fix_intersections()
        self.__populations.append(new_population)

    def __find_bounds(self):
         if len(self.__points) == 1:
            point = self.__points[0]
            left = point.x - 10
            right = point.x + 10
            down = point.y - 10
            up = point.y + 10
            return left, right, down, up
        left = min(p.x for p in self.__points)
        right = max(p.x for p in self.__points)
        down = min(p.y for p in self.__points)
        up = max(p.y for p in self.__points)

        x_len = right - left
        y_len = up - down

        add_x = x_len * 0.05
        add_y = y_len * 0.05
        left -= add_x
        right += add_x
        down -= add_y
        up += add_y
        return left, right, down, up
