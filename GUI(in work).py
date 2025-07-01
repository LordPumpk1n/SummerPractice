from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.ttk import Combobox
import random
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class MainApp(Tk):
	def __init__(self):
		super().__init__()
		self.geometry("1280x720")
		self.title("Покрытие точек квадратами")
		self.minsize(1280, 720)
		self.points = [(10, 20), (-5, 15), (0, 0), (30, -10), (-15, -25), (20, 5), (-10, 30), (25, -20)]
		self.squares = [(-20, -30, 20), (-1, -1, 15), (5, -15, 10)]
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
		self.m = 3
		self.generation_size = 100
		self.population_size = 10
		self.elite_fraction = 5
		self.crossover_prob = 50
		self.mutation_prob = 10
		self.create_widgets()

	def initialize_algorithm(self):
		messagebox.showinfo("Info", "Функция инициализации алгоритма будет реализована позже")

	def run_algorithm_to_end(self):
		messagebox.showinfo("Info", "Функция выполнения до конца будет реализована позже")

	def next_algorithm_step(self):
		messagebox.showinfo("Info", "Функция следующего шага будет реализована позже")

	def prev_algorithm_step(self):
		messagebox.showinfo("Info", "Функция предыдущего шага будет реализована позже")

	def load_points_from_file(self):
		filepath = filedialog.askopenfilename(title="Выберите файл с точками", filetypes=(("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")))
		if not filepath:
			return

		try:
			with open(filepath, 'r') as file:
				self.points = []
				for line in file:
					x, y = map(float, line.split())
					self.points.append((x, y))
			self.update_plot()
		except ValueError:
			messagebox.showerror("Ошибка", "Неправильный формат данных")

	def generate_random_points(self):
		di = DialogInput()
		di.wait_window()
		if di.border:
			left,right = map(float,di.border)
			self.points = [(random.uniform(left, right), random.uniform(left, right)) for _ in range(10)]
			self.update_plot()

	def toggle_widgets(self):
		if self.frame_params.winfo_viewable():
			self.frame_params.pack_forget()
			self.toggle_btn.config(text="Показать параметры")
		else:
			self.frame_params.pack(after=self.toggle_btn, fill='x', padx=10, pady=(0, 10))
			self.toggle_btn.config(text="Скрыть параметры")

	def clear_points(self):
		self.points = []
		self.update_plot()

	def update_plot(self):
		if self.scatter:
			self.scatter.remove()
			self.scatter = None

		for patch in self.squares_patches:
			patch.remove()
		self.squares_patches.clear()

		if self.points:
			x_coords = [x for x, y in self.points]
			y_coords = [y for x, y in self.points]
			self.scatter = self.ax.scatter(x_coords, y_coords, c='blue')

			min_x = min(x for x, y in self.points)
			max_x = max(x for x, y in self.points)
			min_y = min(y for x, y in self.points)
			max_y = max(y for x, y in self.points)

			x_padding = max(10, (max_x - min_x) * 0.1)
			y_padding = max(10, (max_y - min_y) * 0.1)

			self.ax.set_xlim(min_x - x_padding, max_x + x_padding)
			self.ax.set_ylim(min_y - y_padding, max_y + y_padding)
		else:
			self.scatter = self.ax.scatter([], [], c='blue')
			self.ax.set_xlim(-10, 10)
			self.ax.set_ylim(-10, 10)

		for x, y, size in self.squares:
			rect = Rectangle((x, y), size, size, edgecolor='red', facecolor='none')
			self.ax.add_patch(rect)
			self.squares_patches.append(rect)

		self.ax.set_aspect('equal')
		self.canvas.draw_idle()

	def add_point(self):
		try:
			x = float(self.x_entry.get())
			y = float(self.y_entry.get())
			self.points.append((x, y))
			self.update_plot()
			self.x_entry.delete(0, END)
			self.y_entry.delete(0, END)
		except ValueError:
			messagebox.showerror("Ошибка", "Неправильно введённые координаты")

	def create_widgets(self):
		left_frame = Frame(self, bg="lightblue")
		left_frame.place(relx=0, rely=0, relwidth=1/3, relheight=1)

		content_frame = Frame(left_frame, bg="lightblue")
		content_frame.pack(fill='both', expand=True, padx=10, pady=10)

		load_button = Button(content_frame, text="Загрузить из файла", command=self.load_points_from_file)
		load_button.pack(fill='x', pady=5)

		random_button = Button(content_frame, text="Генерация случайных точек", command=self.generate_random_points)
		random_button.pack(fill='x', pady=5)

		add_point_button = Button(content_frame, text="Добавить точку", command=self.add_point)
		add_point_button.pack(fill='x', pady=5)

		input_frame = Frame(content_frame, bg="lightgray")
		input_frame.pack(fill='x', pady=5)

		Label(input_frame, text="X:", bg="lightgray").grid(row=0, column=0, padx=(0, 5))
		self.x_entry = Entry(input_frame, width=10)
		self.x_entry.grid(row=0, column=1, padx=(0, 10))

		Label(input_frame, text="Y:", bg="lightgray").grid(row=0, column=2, padx=(0, 5))
		self.y_entry = Entry(input_frame, width=10)
		self.y_entry.grid(row=0, column=3, padx=(0, 10))

		clear_button = Button(content_frame, text="Очистить точки", command=self.clear_points)
		clear_button.pack(fill='x', pady=5)

		self.toggle_btn = Button(content_frame, text="Показать параметры", command=self.toggle_widgets)
		self.toggle_btn.pack(fill='x', pady=(10, 5))

		initialize_button = Button(content_frame, text="Инициализировать алгоритм", command=self.initialize_algorithm)
		initialize_button.pack(fill='x', pady=5)

		finish_button = Button(content_frame, text="Выполнить алгоритм до конца", command=self.run_algorithm_to_end)
		finish_button.pack(fill='x', pady=5)

		next_step_button = Button(content_frame, text="Следующий шаг алгоритма", command=self.next_algorithm_step)
		next_step_button.pack(fill='x', pady=5)

		prev_step_button = Button(content_frame, text="Предыдущий шаг алгоритма", command=self.prev_algorithm_step)
		prev_step_button.pack(fill='x', pady=5)

		self.frame_params = Frame(content_frame, bg="lightgray", bd=1)

		Label(self.frame_params, text="Размер популяции:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
		tmp = str(self.population_size)
		self.population_size = Entry(self.frame_params)
		self.population_size.insert(0, tmp)
		self.population_size.pack(fill='x', padx=5, pady=(0, 5))

		Label(self.frame_params, text="Число поколений:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
		tmp = str(self.generation_size)
		self.generation_size = Entry(self.frame_params)
		self.generation_size.insert(0, tmp)
		self.generation_size.pack(fill='x', padx=5, pady=(0, 5))

		Label(self.frame_params, text="Вероятность мутации(%):", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
		tmp = str(self.mutation_prob)
		self.mutation_prob = Entry(self.frame_params)
		self.mutation_prob.insert(0, tmp)
		self.mutation_prob.pack(fill='x', padx=5, pady=(0,5))

		Label(self.frame_params, text="Вероятность скрещивания(%):", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
		tmp = self.crossover_prob
		self.crossover_prob = Entry(self.frame_params)
		self.crossover_prob.insert(0, tmp)
		self.crossover_prob.pack(fill='x', padx=5, pady=(0, 5))

		Label(self.frame_params, text="Количество квадратов:", bg="lightgray").pack(anchor='w', padx=5, pady=(5, 0))
		tmp = self.m
		self.m = Entry(self.frame_params)
		self.m.insert(0, tmp)
		self.m.pack(fill='x', padx=5, pady=(0, 5))

		solutions = ["Решение 1", "Решение 2", "Решение 3", "Решение 4"]
		combobox = Combobox(content_frame, values=solutions)
		combobox.pack(pady=5)

		graph_frame = Frame(self)
		graph_frame.place(relx=1/3, rely=0, relwidth=2/3, relheight=2/3)

		fig, self.ax = plt.subplots(figsize=(4, 3))
		self.ax.grid(True, linestyle='--', alpha=0.7)
		self.ax.axhline(0, color='black')
		self.ax.axvline(0, color='black')
		self.scatter = None

		self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
		self.update_plot()

		evolution_frame = Frame(self)
		evolution_frame.place(relx=1/3, rely=2/3, relwidth=2/3, relheight=1/3)

		fig_evo, self.ax_evo = plt.subplots(figsize=(4, 1.5))
		self.ax_evo.set_title('Эволюция приспособленности', fontsize=10)
		self.ax_evo.set_xlabel('Поколение', fontsize=8)
		self.ax_evo.set_ylabel('Приспособленность', fontsize=8)
		self.ax_evo.grid(True, linestyle='--', alpha=0.5)
		self.ax_evo.text(0.5, 0.5, 'Заглушка',
						 horizontalalignment='center', verticalalignment='center')
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
		self.geometry("320x200")
		self.resizable(False, False)
		self.grab_set()
		self.border = [-50, 50]
		self.low_border = None
		self.top_border = None

		Label(self, text="Введите нижнее значение").pack(pady=10)
		self.low_border = Entry(self, width=25)
		self.low_border.insert(0, str(self.border[0]))
		self.low_border.pack(pady=5)

		Label(self, text="Введите верхнее значение").pack(pady=10)
		self.top_border = Entry(self, width=25)
		self.top_border.insert(0, str(self.border[1]))
		self.top_border.pack(pady=5)

		ok_btn = Button(self, text="Ок", command=self.submit).pack(side=LEFT, padx=(50,0))
		cancel_btn = Button(self, text="Отмена", command=self.cancel).pack(side=RIGHT, padx=(0,50))

	def submit(self):
		self.border[0] = float(self.low_border.get())
		self.border[1] = float(self.top_border.get())
		self.destroy()

	def cancel(self):
		self.border = False
		self.destroy()



if __name__ == "__main__":
	app = MainApp()
	app.mainloop()