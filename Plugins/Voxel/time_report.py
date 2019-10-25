import csv
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import numpy as np
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def get_arrays(path):
    with open(path, newline='') as csv_file:
        csv.field_size_limit(100000000)
        reader = list(csv.reader(csv_file, delimiter=';', quotechar='"'))
        num_stats = len(reader) - 1
        print("Num stats:", num_stats)
        labels = [label.strip() for label in reader[0]]
        # print("Labels:", ", ".join(labels))

        level_of_details = np.zeros(num_stats, dtype=int)
        number_of_indices = np.zeros(num_stats, dtype=int)
        number_of_vertices = np.zeros(num_stats, dtype=int)
        is_empty = np.zeros(num_stats, dtype=bool)
        work_times_map = {}
        value_queries = np.zeros(num_stats, dtype=object)
        material_queries = np.zeros(num_stats, dtype=object)

        work_time_indices = []
        level_of_detail_index = labels.index("LOD")
        number_of_indices_index = labels.index("NumIndices")
        number_of_vertices_index = labels.index("NumVertices")
        is_empty_index = labels.index("bIsEmpty")
        value_queries_index = labels.index("Value queries")
        material_queries_index = labels.index("Material queries")

        for field_index in range(len(labels)):
            label = labels[field_index]
            if label.startswith("work time:"):
                work_time_indices.append(field_index)
                work_times_map[label] = np.zeros(num_stats)

        for row_index in range(num_stats):
            row = reader[row_index + 1]

            for field_index in work_time_indices:
                work_times_map[labels[field_index]][row_index] = row[field_index]

            level_of_details[row_index] = row[level_of_detail_index]

            num_indices = row[number_of_indices_index]
            number_of_indices[row_index] = 0 if len(num_indices) == 0 else num_indices
            num_vertices = row[number_of_vertices_index]
            number_of_vertices[row_index] = 0 if len(num_vertices) == 0 else num_vertices

            is_empty[row_index] = row[is_empty_index] == "true"

            value_queries[row_index] = np.fromstring(row[value_queries_index], dtype=float, sep=", ")
            material_queries[row_index] = np.fromstring(row[material_queries_index], dtype=float, sep=", ")

    return level_of_details, \
           number_of_indices, \
           number_of_vertices, \
           is_empty, \
           work_times_map, \
           value_queries, \
           material_queries


class Application(Frame):
    def __init__(self, master, csv_path):
        super().__init__(master)
        self.master = master
        self.pack()

        self.level_of_details, \
        self.number_of_indices, \
        self.number_of_vertices, \
        self.is_empty, \
        self.work_times_map, \
        self.value_queries, \
        self.material_queries = get_arrays(csv_path)
        self.total_times = np.sum(np.clip(np.array(list(self.work_times_map.values())), 0, None), axis=0)

        print("{}/{} empty chunks".format(np.sum(self.is_empty), len(self.is_empty)))

        left = Frame(root)
        right = Frame(root)

        left.pack(side=LEFT, expand=True, fill=BOTH)
        right.pack(side=RIGHT, expand=True, fill=BOTH)

        figure = Figure(figsize=(5, 5))
        figure.subplots_adjust(left=0.15)
        self.axis = figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(figure, left)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, left)
        self.toolbar.update()
        self.toolbar.pack(side=BOTTOM, fill=X, expand=False)

        def set_plotted_values(x, y):
            self.x = np.array(x)
            self.y = np.array(y)
            update_plot()

        def update_plot():
            show_empty = self.show_empty.instate(["selected"])
            x = self.x if show_empty else self.x[np.logical_not(self.is_empty)]
            y = self.y if show_empty else self.y[np.logical_not(self.is_empty)]
            x = x[y >= 0]
            y = y[y >= 0]
            self.axis.clear()
            self.axis.set_xlabel("LOD")
            self.axis.set_ylabel("Time (ms)")
            self.plot(x, y)

        self.show_empty = ttk.Checkbutton(right, text="Show empty", command=update_plot)
        self.show_empty.pack()
        self.show_empty.state(["!alternate"])

        Button(right,
               text="Total",
               command=lambda: set_plotted_values(self.level_of_details, self.total_times)).pack()

        for name, value in self.work_times_map.items():
            name = name[len("work time:"):]
            Button(right,
                   text=name,
                   command=lambda value=value: set_plotted_values(self.level_of_details, value)).pack()

        ttk.Separator(right).pack(pady=20)

        def plot_queries(queries):
            self.axis.clear()
            self.axis.set_yscale("log")
            self.axis.set_xlabel("Time (ms)")
            self.axis.set_ylabel("Queries count")
            data = []
            for query in queries:
                data += list(query)
            mean = np.mean(data)
            print("mean: ", mean)
            self.axis.hist(data, bins=int(self.spinbox.get()))
            self.axis.axvline(mean, color="red")
            self.canvas.draw()

        bins_frame = Frame(right)
        bins_frame.pack()

        Label(bins_frame, text="Bins").pack(side=LEFT)

        self.spinbox = Spinbox(bins_frame)
        self.spinbox.pack(side=RIGHT)
        self.spinbox.delete(0, "end")
        self.spinbox.insert(0, 50)

        Button(right,
               text="Value queries",
               command=lambda: plot_queries(self.value_queries)).pack()

        Button(right,
               text="Material queries",
               command=lambda: plot_queries(self.material_queries)).pack()

        ttk.Separator(right).pack(pady=20)

        def plot_num(array, name):
            self.axis.clear()
            self.axis.set_xlabel("LOD")
            self.axis.set_ylabel("Number of " + name)
            self.plot(self.level_of_details, array)

        Button(right,
               text="Num indices",
               command=lambda: plot_num(self.number_of_indices, "indices")).pack()
        Button(right,
               text="Num vertices",
               command=lambda: plot_num(self.number_of_vertices, "vertices")).pack()

        set_plotted_values(self.level_of_details, self.total_times)

    def plot(self, x, y):
        self.axis.plot(x, y, "o", color="blue")
        unique_x = sorted(set(x))
        self.axis.plot(unique_x,
                       [np.mean(y[x == i]) for i in unique_x],
                       "o" if len(unique_x) == 1 else "-",
                       color="red")
        self.canvas.draw()


root = Tk()
root.withdraw()

csv_path = filedialog.askopenfilename(title="Select log file")

root = Tk()
app = Application(root, csv_path)
app.mainloop()
