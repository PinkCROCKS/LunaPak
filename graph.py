import matplotlib.pyplot as plt
from model import Calculator

def main(data):
    # Создание экземпляра калькулятора и обработка данных для построения графика
    calc = Calculator(data)
    x_values = [x / 1000 for x in calc.get_x_axis_values()]  # Преобразование значений оси X в километры
    y_values = [y / 1000 for y in calc.get_y_axis_values()]  # Преобразование значений оси Y в километры
    y_kr_values = [y / 1000 for y in calc.get_y_axis_values_kr()]  # Преобразование значений оси Y с поправкой кривизны в километры
    # Построение графиков для траекторий с и без поправки кривизны
    graph(calc, 'Траектория', x_values, y_values)
    #graph(calc, '12', x_values, y_kr_values)

def graph(calc, name, x_values, y_values, earth_y=None):
    # Настройка параметров графика
    aspect_ratio = 7 / 33
    fig, ax = plt.subplots(figsize=(8, 8 * aspect_ratio))

    # Построение траектории и отметок для отделения ступеней
    ax.plot(x_values, y_values, color='black', label='Траектория', linewidth=0.7, zorder=1)
    separation_times = (
        len(calc.stage_one.get_time_values()),
        len(calc.stage_one.get_time_values()) + len(calc.stage_two.get_time_values())
    )
    red_points_x = [x_values[t] for t in separation_times]
    red_points_y = [y_values[t] for t in separation_times]
    ax.scatter(red_points_x, red_points_y, color='red', label='Отделение ступеней', s=20, zorder=2)

    # Настройка осей и меток
    ax.set_xlabel('x, км')
    ax.set_ylabel('y, км')
    ax.set_ylim(min(y_values)-50, max(y_values)+150)
    ax.set_xlim(min(x_values)-50, max(x_values)+50)
    x_ticks = [i * 100 for i in range(int(min(x_values) / 100), int((max(x_values)+50) / 100) + 1)]
    y_ticks = [i * 100 for i in range(int(min(y_values) / 100), int((max(y_values)+150) / 100) + 1)]
    
    # Настройка отображения делений осей
    ax.tick_params(axis='both', which='both', direction='in', length=0, width=0)
    ax.xaxis.set_tick_params(width=0)
    ax.yaxis.set_tick_params(width=0)
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)

    # Отображение линий осей и сетки, добавление легенды
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.grid(color='gray', linestyle=':', linewidth=0.5)
    ax.legend()

    # Скрытие верхней и правой границы, настройка размеров и сохранение изображения
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.subplots_adjust(left=0.04, right=1, top=1, bottom=0.14)
    fig.set_size_inches(1852/100, 397/100)
    plt.savefig(f"{name}.png", dpi=100)

main('data.txt')