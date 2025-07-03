from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
import random
from genetic_alg import GeneticAlg, Point

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

M = '5'
GENERATION_SIZE = '100'
POPULATION_SIZE = '200'
CROSSOVER_PROB = '70'
MUTATION_PROB = '30'
ELITE_FRACTION = '10'
LOW_BOUND = '-100'
TOP_BOUND = '100'
COUNT = '20'


class MainApp(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("1280x720")
        self.title("Покрытие точек квадратами")
        self.minsize(1280, 720)
        self.points = []
        self.squares = []
        self.scatter = None
        self.squares_patches = []
        self.ax = None
        self.ax_evo = None
        self.canvas = None
        self.canvas_evo = None
        self.x_entry = None
        self.y_entry = None
        self.toggle_btn = None
        self.frame_params = None
        self.m = None
        self.generation_size = None
        self.population_size = None
        self.crossover_prob = None
        self.mutation_prob = None
        self.elite_fraction = None
        self.current_generation_label = None
        self.current_generation = 1
        self.current_generation_size = int(GENERATION_SIZE)
        self.running = False
        self.combobox = None
        self.genetic_alg = None
        self.mean_fit = []
        self.max_fit = []
        self.current_solution = 0
        self.create_widgets()
        self.init_plots()

    def init_plots(self):
        if self.points:
            x_coords = [p.x for p in self.points]
            y_coords = [p.y for p in self.points]
            self.scatter = self.ax.scatter(x_coords, y_coords, c='blue')
        else:
            self.scatter = self.ax.scatter([], [], c='blue')

        self.mean_line, = self.ax_evo.plot([], [], 'b-', label='Средняя приспособленность')
        self.max_line, = self.ax_evo.plot([], [], 'r-', label='Лучшая приспособленность')
        self.ax_evo.legend(fontsize=6)
        self.ax_evo.grid(True, linestyle='--', alpha=0.5)

        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.set_aspect('equal')
        self.ax_evo.set_xlim(0, 1)
        self.ax_evo.set_ylim(0, 1)

        self.canvas.draw()
        self.canvas_evo.draw()

    def initialize_algorithm(self):
        try:
            m_val = int(self.m.get())
            if m_val <= 0:
                raise ValueError("Количество квадратов должно быть положительным целым числом")

            pop_size = int(self.population_size.get())
            if pop_size <= 0:
                raise ValueError("Размер популяции должен быть положительным целым числом")

            gen_size = int(self.generation_size.get())
            if gen_size <= 0:
                raise ValueError("Число поколений должно быть положительным целым числом")

            crossover_prob = float(self.crossover_prob.get())
            mutation_prob = float(self.mutation_prob.get())
            elite_fraction = float(self.elite_fraction.get())
            if any(map(lambda x: x < 0 or x > 100,[crossover_prob, mutation_prob, elite_fraction])):
                raise ValueError("Вероятность должна быть от 0 до 100")

            if len(self.points) == 0:
                raise ValueError("Необходимо добавить точки")

        except ValueError as e:
            messagebox.showerror(title="Ошибка ввода параметров", message=str(e))
            return

        if self.next_step_button['state'] == 'disabled':
            self.next_step_button["state"] = 'normal'
            self.prev_step_button["state"] = 'normal'
            self.finish_button["state"] = 'normal'
            self.combobox['state'] = 'normal'
            self.combobox.insert(0, 'Лучшее решение')

        method = 2 if self.ga_combobox.get() == "Турнирный отбор" else 1
        self.genetic_alg = GeneticAlg(pop_size, m_val, self.points, method,
                                      elite_fraction / 100, crossover_prob / 100, mutation_prob / 100)

        self.current_generation = 1
        self.max_fit = []
        self.mean_fit = []
        self.current_generation_size = gen_size
        self.current_generation_label["text"] = f"Поколение {self.current_generation}/{self.current_generation_size}"
        self.update_plot()

    def enable_controls(self):
        self.finish_button.config(state='normal')
        self.next_step_button.config(state='normal')
        self.prev_step_button.config(state='normal')
        self.combobox.config(state='normal')
        self.load_button.config(state='normal')
        self.random_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.add_point_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def stop_algorithm(self):
        self.running = False
        self.enable_controls()

    def run_algorithm_to_end(self):
        self.stop_button.config(state='normal')
        self.finish_button.config(state='disabled')
        self.next_step_button.config(state='disabled')
        self.prev_step_button.config(state='disabled')
        self.combobox.config(state='disabled')
        self.load_button.config(state='disabled')
        self.random_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        self.add_point_button.config(state='disabled')

        self.running = True
        self.after(10, self._run_algorithm_step)

    def _run_algorithm_step(self):
        if not self.running:
            return

        if self.current_generation < self.current_generation_size:
            self.current_generation += 1
            self.current_generation_label["text"] = f"Поколение {self.current_generation}/{self.current_generation_size}"
            self.update_plot()

            self.update_idletasks()
            self.after(0, self._run_algorithm_step)
        else:
            self.running = False
            self.enable_controls()

    def reset(self):
        self.squares = []
        self.current_generation = 1
        self.running = False
        self.genetic_alg = None
        self.mean_fit = []
        self.max_fit = []
        self.current_solution = 0
        self.finish_button.config(state='disabled')
        self.next_step_button.config(state='disabled')
        self.prev_step_button.config(state='disabled')
        self.combobox.config(state='disabled')
        self.combobox.set('')


    def next_algorithm_step(self):
        if self.current_generation < self.current_generation_size:
            self.current_generation += 1
        self.current_generation_label["text"] = f"Поколение {self.current_generation}/{self.current_generation_size}"
        self.update_plot()

    def prev_algorithm_step(self):
        if self.current_generation > 1:
            self.current_generation -= 1
        self.current_generation_label["text"] = f"Поколение {self.current_generation}/{self.current_generation_size}"
        self.update_plot()

    def load_points_from_file(self):
        filepath = filedialog.askopenfilename(title="Выберите файл с точками", filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")))
        if not filepath:
            return
        try:
            with open(filepath, 'r') as file:
                self.points = []
                for line in file:
                    x, y = map(float, line.split())
                    self.points.append(Point(x, y))
            self.reset()
            self.update_plot()
        except ValueError:
            messagebox.showerror("Ошибка", "Неправильный формат данных")

    def generate_random_points(self):
        self.reset()
        di = DialogInput()
        di.wait_window()
        if di.border:
            n = di.count
            left, right = map(float, di.border)
            self.points = [Point(random.uniform(left, right), random.uniform(left, right)) for _ in range(n)]
            self.update_plot()

    def toggle_widgets(self):
        if self.frame_params.winfo_viewable():
            self.frame_params.pack_forget()
            self.toggle_btn.config(text="Показать параметры")
        else:
            self.frame_params.pack(after=self.toggle_btn, fill='x', padx=10, pady=(0, 10))
            self.toggle_btn.config(text="Скрыть параметры")

    def clear_points(self):
        self.reset()
        self.points = []
        self.scatter.set_offsets(np.empty((0, 2)))
        self.update_plot()


    def update_plot(self):
        all_x = []
        all_y = []

        if self.points:
            x_coords = [p.x for p in self.points]
            y_coords = [p.y for p in self.points]
            all_x.extend(x_coords)
            all_y.extend(y_coords)
            self.scatter.set_offsets(list(zip(x_coords, y_coords)))
        else:
            self.scatter.set_offsets(np.empty((0,2)))

        for patch in self.squares_patches:
            patch.remove()
        self.squares_patches = []

        if self.genetic_alg is not None:
            population, mean_fit, max_fit = self.genetic_alg.get_solution(self.current_generation - 1)
            if len(self.max_fit) < self.current_generation:
                self.mean_fit.append(mean_fit)
                self.max_fit.append(max_fit)

            for square in population.individuals[self.current_solution].squares:
                rect = Rectangle((square.x, square.y), square.size, square.size, edgecolor='red', facecolor='none')
                self.ax.add_patch(rect)
                self.squares_patches.append(rect)

                all_x.append(square.x)
                all_x.append(square.x + square.size)
                all_y.append(square.y)
                all_y.append(square.y + square.size)

            generations = list(range(1, len(self.max_fit) + 1))
            if self.genetic_alg is not None:
                self.mean_line.set_data(generations, self.mean_fit)
                self.max_line.set_data(generations, self.max_fit)

                self.ax_evo.set_xlim(1, max(generations))
                self.ax_evo.set_ylim(0, max(self.max_fit) * 1.1)
        else:
            self.mean_line.set_data([], [])
            self.max_line.set_data([], [])

            self.ax_evo.set_xlim(0, 1)
            self.ax_evo.set_ylim(0, 1)
            self.canvas_evo.draw_idle()

        if all_x:
            min_x = min(x for x in all_x)
            max_x = max(x for x in all_x)
            min_y = min(y for y in all_y)
            max_y = max(y for y in all_y)

            x_padding = max(10, (max_x - min_x) * 0.1)
            y_padding = max(10, (max_y - min_y) * 0.1)

            self.ax.set_xlim(min_x - x_padding, max_x + x_padding)
            self.ax.set_ylim(min_y - y_padding, max_y + y_padding)
        else:
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(-10, 10)

        self.canvas.draw_idle()
        self.canvas_evo.draw_idle()

    def add_point(self):
        try:
            if len(self.squares_patches) != 0:
                self.reset()
                self.update_plot()
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            self.points.append(Point(x, y))

            x_coords = [p.x for p in self.points]
            y_coords = [p.y for p in self.points]
            self.scatter.set_offsets(list(zip(x_coords, y_coords)))

            if len(self.points) == 1:
                self.ax.set_xlim(x - 10, x + 10)
                self.ax.set_ylim(y - 10, y + 10)
            else:
                min_x = min(p.x for p in self.points)
                max_x = max(p.x for p in self.points)
                min_y = min(p.y for p in self.points)
                max_y = max(p.y for p in self.points)

                x_padding = max(10, (max_x - min_x) * 0.1)
                y_padding = max(10, (max_y - min_y) * 0.1)

                self.ax.set_xlim(min_x - x_padding, max_x + x_padding)
                self.ax.set_ylim(min_y - y_padding, max_y + y_padding)

            self.canvas.draw_idle()
            self.x_entry.delete(0, END)
            self.y_entry.delete(0, END)
        except ValueError:
            messagebox.showerror("Ошибка", "Неправильно введённые координаты")

    def selected(self, event):
        selection = self.combobox.get()
        try:
            selection = int(selection.split()[1])
        except ValueError:
            selection = 0
        self.current_solution = selection
        self.update_plot()

    def create_widgets(self):
        left_frame = Frame(self, bg="lightblue")
        left_frame.place(relx=0, rely=0, relwidth=1 / 3, relheight=1)

        content_frame = Frame(left_frame, bg="lightblue")
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.load_button = Button(content_frame, text="Загрузить из файла", command=self.load_points_from_file)
        self.load_button.pack(fill='x', pady=5)

        self.random_button = Button(content_frame, text="Генерация случайных точек", command=self.generate_random_points)
        self.random_button.pack(fill='x', pady=5)

        self.add_point_button = Button(content_frame, text="Добавить точку", command=self.add_point)
        self.add_point_button.pack(fill='x', pady=5)

        input_frame = Frame(content_frame, bg="lightgray")
        input_frame.pack(fill='x', pady=5)

        Label(input_frame, text="X:", bg="lightgray").grid(row=0, column=0, padx=(0, 5))
        self.x_entry = Entry(input_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=(0, 10))

        Label(input_frame, text="Y:", bg="lightgray").grid(row=0, column=2, padx=(0, 5))
        self.y_entry = Entry(input_frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=(0, 10))

        self.clear_button = Button(content_frame, text="Очистить точки", command=self.clear_points)
        self.clear_button.pack(fill='x', pady=5)

        self.toggle_btn = Button(content_frame, text="Показать параметры", command=self.toggle_widgets)
        self.toggle_btn.pack(fill='x', pady=(10, 5))

        initialize_button = Button(content_frame, text="Инициализировать алгоритм", command=self.initialize_algorithm)
        initialize_button.pack(fill='x', pady=5)

        self.finish_button = Button(content_frame, text="Выполнить алгоритм до конца", command=self.run_algorithm_to_end, state='disabled')
        self.finish_button.pack(fill='x', pady=5)

        self.stop_button = Button(content_frame, text='Остановить алгоритм', command=self.stop_algorithm, state='disabled')
        self.stop_button.pack(fill='x', pady=5)

        self.next_step_button = Button(content_frame, text="Следующий шаг алгоритма", command=self.next_algorithm_step, state="disabled")
        self.next_step_button.pack(fill='x', pady=5)

        self.prev_step_button = Button(content_frame, text="Предыдущий шаг алгоритма", command=self.prev_algorithm_step, state="disabled")
        self.prev_step_button.pack(fill='x', pady=5)

        self.frame_params = Frame(content_frame, bg="lightgray", bd=1)

        Label(self.frame_params, text="Количество квадратов:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
        self.m = Entry(self.frame_params)
        self.m.insert(0, M)
        self.m.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Размер популяции:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
        self.population_size = Entry(self.frame_params)
        self.population_size.insert(0, POPULATION_SIZE)
        self.population_size.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Число поколений:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
        self.generation_size = Entry(self.frame_params)
        self.generation_size.insert(0, GENERATION_SIZE)
        self.generation_size.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Вероятность мутации(%):", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
        self.mutation_prob = Entry(self.frame_params)
        self.mutation_prob.insert(0, MUTATION_PROB)
        self.mutation_prob.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Вероятность скрещивания(%):", bg="lightgray").pack(anchor='w', padx=5,
                                                                                          pady=(5, 0))
        self.crossover_prob = Entry(self.frame_params)
        self.crossover_prob.insert(0, CROSSOVER_PROB)
        self.crossover_prob.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Процент элиты(%):", bg='lightgray').pack(anchor='w', padx=5, pady=(5, 0))
        self.elite_fraction = Entry(self.frame_params)
        self.elite_fraction.insert(0, ELITE_FRACTION)
        self.elite_fraction.pack(fill='x', padx=5, pady=(0, 5))

        Label(self.frame_params, text="Метод отбора:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
        gas = ["Правило рулетки", "Турнирный отбор"]
        self.ga_combobox = Combobox(self.frame_params, values=gas)
        self.ga_combobox.insert(0, gas[0])
        self.ga_combobox.pack(fill='x', padx=5, pady=(0, 5))

        solutions = [f"Решение {x}" for x in range(1, int(POPULATION_SIZE))]
        solutions.insert(0, "Лучшее решение")
        self.combobox = Combobox(content_frame, values=solutions, state='disabled')
        self.combobox.pack(pady=5)
        self.combobox.bind("<<ComboboxSelected>>", func=self.selected)

        graph_frame = Frame(self, background="white")
        graph_frame.place(relx=1 / 3, rely=0, relwidth=2 / 3, relheight=2 / 3)

        self.current_generation_label = Label(graph_frame, text=f"Поколение 0/{GENERATION_SIZE}", background='white')
        self.current_generation_label.pack(pady=(10, 0))

        fig, self.ax = plt.subplots(figsize=(4, 3))
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.axhline(0, color='black')
        self.ax.axvline(0, color='black')
        self.scatter = None

        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        evolution_frame = Frame(self)
        evolution_frame.place(relx=1/3, rely=2/3, relwidth=2/3, relheight=1/3)

        fig_evo, self.ax_evo = plt.subplots(figsize=(4, 1))
        self.ax_evo.set_title('Эволюция приспособленности', fontsize=10)
        self.ax_evo.set_ylabel('Приспособленность', fontsize=8, labelpad=0.5)
        self.ax_evo.grid(True, linestyle='--', alpha=0.5)
        self.ax_evo.set_xlim(0, 1)
        self.ax_evo.set_ylim(0, 1)

        self.canvas_evo = FigureCanvasTkAgg(fig_evo, master=evolution_frame)
        self.canvas_evo.draw()
        self.canvas_evo.get_tk_widget().pack(fill=BOTH, expand=True)

        self.frame_params.pack_forget()


class DialogInput(Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Диапозон генерации точек")
        self.geometry("420x300")
        self.resizable(False, False)
        self.grab_set()
        self.border = [LOW_BOUND, TOP_BOUND]
        self.count = COUNT
        self.count_input = None
        self.low_border = None
        self.top_border = None
        self.error_message = None

        Label(self, text="Введите количество точек").pack(pady=10)
        self.count_input = Entry(self, width=25)
        self.count_input.insert(0, str(self.count))
        self.count_input.pack(pady=5)

        Label(self, text="Введите нижнее значение").pack(pady=10)
        self.low_border = Entry(self, width=25)
        self.low_border.insert(0, str(self.border[0]))
        self.low_border.pack(pady=5)

        Label(self, text="Введите верхнее значение").pack(pady=10)
        self.top_border = Entry(self, width=25)
        self.top_border.insert(0, str(self.border[1]))
        self.top_border.pack(pady=5)

        self.error_message = Label(self, text='', foreground='red')
        self.error_message.pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        Button(self, text="Ок", command=self.submit).pack(side=LEFT, padx=(50, 0), pady=10)
        Button(self, text="Отмена", command=self.cancel).pack(side=RIGHT, padx=(0, 50), pady=10)

    def submit(self):
        try:
            self.count = int(self.count_input.get())
            self.border[0] = float(self.low_border.get())
            self.border[1] = float(self.top_border.get())
            self.destroy()
        except ValueError:
            self.error_message["text"] = "Ошибка ввода данных"

    def cancel(self):
        self.border = False
        self.destroy()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()