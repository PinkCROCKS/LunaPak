import math
import numpy as np

class Calculator:
    # Определение класса для вычислений
    # Открытие файла с данными и обработка их для дальнейших расчетов
    # Инициализация параметров для каждой ступени и выполнение расчетов траектории
    
    def __init__(self,data):
        self.x_axis_values = []
        self.y_axis_values = []
        self.y_axis_values_kr =[]
        self.r = 600.0  # Радиус Кербина
        self.scale_ratio = 0.001
        values ={}

        with open(data, 'r', encoding='utf-8') as file:
            lines = file.readlines()


        for line in lines:
            if line=='    Первая ступень (один боковой блок из четырёх):' or line=='    Вторая ступень:' or line=='    Третья ступень:':
                continue
            parts = line.split('=')
            if len(parts) >= 2:
                key = parts[0].strip()
                value = parts[1].split('-')[0].strip()
                values[key] = float(value)

        M_1_st = values['M_1_st']
        M_1_dry = values['M_1_dry']
        F_1 = values['F_1']
        t_1 = values['t_1']
        M_2_st = values['M_2_st']
        M_2_dry = values['M_2_dry']
        F_2 = values['F_2']
        t_2 = values['t_2']
        M_3_st = values['M_3_st']
        M_3_dry = values['M_3_dry']
        F_3 = values['F_3']
        t_3 = values['t_3']
        M_1 = values['M_1']
        Fmin_1 = values['Fmin_1']
        M_2 = values['M_2']
        M_3 = values['M_3']
        angle_1 = values['angle_1']
        angle_2 = values['angle_2']
        angle_3 = values['angle_3']

        k_2 = (M_2_st - M_2_dry)/(t_2+t_1) #310.0 
        k_1 = ((M_1_st-M_1_dry)/t_1)*4 + k_2 #1688.0
        k_3 = (M_3_st - M_3_dry)/(t_2+t_1) #84.7

        print(f'Посчитанные значения: k_1={k_1}, k_2={k_2}, k_3={k_3}')
        if input('Заменить на значения в .txt? [y/n]')=='y':
            k_1 = values['k_1']
            k_2 = values['k_2']
            k_3 = values['k_3']

        self.stage_one = StageOne(t_1,F_1,Fmin_1,M_1,angle_1,k_1)
        self.stage_two = StageTwo(t_2,F_2,M_2,angle_2,k_2)
        self.stage_three = StageThree(t_3,F_3,M_3,angle_3,k_3)

        print('\nНачало расчетов...\n')

        self.evaluate_parameters()
        self.calculate_trajectory()

    def evaluate_parameters(self):
        self.stage_two.set_stage_one(self.stage_one)
        self.stage_three.set_stage_two(self.stage_two)

        self.stage_one.calculate_function()
        self.stage_two.calculate_function()
        self.stage_three.calculate_function()

    def calculate_trajectory(self):
        self.x_axis_values.extend(self.stage_one.get_movement_x_values())
        self.x_axis_values.extend(self.stage_two.get_movement_x_values())
        self.x_axis_values.extend(self.stage_three.get_movement_x_values())
        self.y_axis_values.extend(self.stage_one.get_movement_y_values())
        self.y_axis_values.extend(self.stage_two.get_movement_y_values())
        self.y_axis_values.extend(self.stage_three.get_movement_y_values())

        self.y_axis_values_kr=self.y_axis_values.copy()
        for i in range(len(self.x_axis_values)):
            h = self.r / (math.cos(math.atan(self.x_axis_values[i] / self.r))) - self.r
            self.y_axis_values_kr[i] += h

        print("Конечная высота орбиты с учётом поправки кривизны: " +
              f"{self.y_axis_values_kr[len(self.stage_one.get_time_values()) + len(self.stage_two.get_time_values())]/1000:.0f} км")
        #print("Конечная высота орбиты с учётом поправки кривизны: " +
              #f"{self.y_axis_values_kr[-1]/1000:.0f} км")
        
    def get_y_axis_values(self):
        return self.y_axis_values

    def get_y_axis_values_kr(self):
        return self.y_axis_values_kr

    def get_x_axis_values(self):
        return self.x_axis_values

    def get_scale_ratio(self):
        return self.scale_ratio


class Stages:
    # Определение базового класса ступеней
    # Расчет параметров, скорости, ускорения и т.д.

    def __init__(self):
        self.t = None #Время работы ступени, с
        self.F = None #Тяга двигателя в вакууме, Н
        self.Fmin = None #Минимальная тяга двигателя, Н
        self.M = None #Масса ракеты, кг
        self.angle = None #Конечный угол поворота ракеты относительно вертикальной оси за время работы ступени, град
        self.k = None #Расход массы ступени, кг/с
        self.g = 9.81665  # Ускорение свободного падения, Н/кг
        self.time_values = []
        self.movement_x_values = []
        self.movement_y_values = []
        self.speed_x_values = []
        self.speed_y_values = []
        self.acceleration_x_values = []
        self.acceleration_y_values = []
        self.step = 0.01

    def calculate_time_values(self):
        start_number = 0.0
        end_number = self.t
        self.time_values = np.arange(start_number, end_number, self.step)

    def euler(self, arg1, arg2):
        return arg1 + 2 * self.step * arg2

    def set_start_values(self, values, previous_values, i):
        if i >= 2:
            return values[i - 2]
        elif previous_values is not None:
            return previous_values[-1 - (2 - i)]
        else:
            return 0.0

    def rotation_angle_function(self):
        return self.angle * ((math.pi / 2) / 90) / self.t

    def get_end_angle(self):
        return self.rotation_angle_function() * self.t

    def print_parameters(self):
        if self.__class__.__name__=='StageOne':
            num="1"
        elif self.__class__.__name__=='StageTwo':
            num="2"
        elif self.__class__.__name__=='StageThree':
            num="3"
        print(f"Параметры в конце работы ступени {num}")
        print(f"Скорость по X: = {self.speed_x_values[-1]:.0f} м/с ({self.speed_x_values[-1] * 3.6:.0f} км/ч)")
        print(f"Скорость по Y: = {self.speed_y_values[-1]:.0f} м/с ({self.speed_y_values[-1] * 3.6:.0f} км/ч)")
        sp = math.sqrt(self.speed_x_values[-1]**2 + self.speed_y_values[-1]**2)
        print(f"Суммарная скорость: = {sp:.0f} м/с ({sp * 3.6:.0f} км/ч)")
        print()

    def get_time_values(self):
        return self.time_values

    def get_movement_x_values(self):
        return self.movement_x_values

    def get_movement_y_values(self):
        return self.movement_y_values

    def get_speed_x_values(self):
        return self.speed_x_values

    def get_speed_y_values(self):
        return self.speed_y_values

    def get_acceleration_x_values(self):
        return self.acceleration_x_values

    def get_acceleration_y_values(self):
        return self.acceleration_y_values


class StageOne(Stages):
    # Определение класса для первой ступени
    # Вычисление параметров для первой ступени и построение её траектории

    def __init__(self,t,F,Fmin,M,angle,k):
        super().__init__()
        self.t = t
        self.F = F
        self.Fmin = Fmin
        self.M = M
        self.angle = angle
        self.k = k
        self.calculate_time_values()

    def calculate_function(self):
        for i in range(len(self.time_values)):
            self.acceleration_x_values.append(self.x_function(self.time_values[i]))
            self.acceleration_y_values.append(self.y_function(self.time_values[i]))
            self.speed_x_values.append(self.euler(self.set_start_values(self.speed_x_values, None, i),
                                                  self.acceleration_x_values[i]))
            self.speed_y_values.append(self.euler(self.set_start_values(self.speed_y_values, None, i),
                                                  self.acceleration_y_values[i]))
            self.movement_x_values.append(self.euler(self.set_start_values(self.movement_x_values, None, i),
                                                     self.speed_x_values[i]))
            self.movement_y_values.append(self.euler(self.set_start_values(self.movement_y_values, None, i),
                                                     self.speed_y_values[i]))

        self.print_parameters()

    def x_function(self, arg):
        return ((self.Fmin + self.engine_force_increase() * arg) * math.sin(self.rotation_angle_function() * arg)) / (
                self.M - self.k * arg)

    def y_function(self, arg):
        return ((self.Fmin + self.engine_force_increase() * arg) * math.cos(self.rotation_angle_function() * arg)) / (
                self.M - self.k * arg) - self.g

    def engine_force_increase(self):
        return (self.F - self.Fmin) / self.t


class StageTwo(Stages):
    # Определение класса для второй ступени
    # Вычисление параметров для второй ступени и построение её траектории, используя данные о первой ступени

    def __init__(self,t,F,M,angle,k):
        super().__init__()
        self.stage_one = None
        self.t = t
        self.F = F
        self.M = M
        self.angle = angle
        self.k = k
        self.calculate_time_values()

    def calculate_function(self):
        for i in range(len(self.time_values)):
            self.acceleration_x_values.append(self.x_function(self.time_values[i]))
            self.acceleration_y_values.append(self.y_function(self.time_values[i]))
            self.speed_x_values.append(self.euler(self.set_start_values(self.speed_x_values,
                                                                         self.stage_one.get_speed_x_values(), i),
                                                  self.acceleration_x_values[i]))
            self.speed_y_values.append(self.euler(self.set_start_values(self.speed_y_values,
                                                                         self.stage_one.get_speed_y_values(), i),
                                                  self.acceleration_y_values[i]))
            self.movement_x_values.append(self.euler(self.set_start_values(self.movement_x_values,
                                                                           self.stage_one.get_movement_x_values(), i),
                                                     self.speed_x_values[i]))
            self.movement_y_values.append(self.euler(self.set_start_values(self.movement_y_values,
                                                                           self.stage_one.get_movement_y_values(), i),
                                                     self.speed_y_values[i]))

        self.print_parameters()

    def x_function(self, arg):
        return (self.F * math.sin(self.stage_one.get_end_angle() + self.rotation_angle_function() * arg)) / (
                self.M - self.k * arg)

    def y_function(self, arg):
        return (self.F * math.cos(self.stage_one.get_end_angle() + self.rotation_angle_function() * arg)) / (
                self.M - self.k * arg) - self.g

    def set_stage_one(self, stage_one):
        self.stage_one = stage_one

    def get_stage_one(self):
        return self.stage_one


class StageThree(Stages):
    # Определение класса для третьей ступени
    # Вычисление параметров для третьей ступени и построение её траектории, используя данные о второй ступени

    def __init__(self,t,F,M,angle,k):
        super().__init__()
        self.stage_two = None
        self.t = t
        self.F = F
        self.M = M
        self.angle = angle
        self.k = k
        self.calculate_time_values()

    def calculate_function(self):
        for i in range(len(self.time_values)):
            self.acceleration_x_values.append(self.x_function(self.time_values[i]))
            self.acceleration_y_values.append(self.y_function(self.time_values[i]))
            self.speed_x_values.append(self.euler(self.set_start_values(self.speed_x_values,
                                                                         self.stage_two.get_speed_x_values(), i),
                                                  self.acceleration_x_values[i]))
            self.speed_y_values.append(self.euler(self.set_start_values(self.speed_y_values,
                                                                         self.stage_two.get_speed_y_values(), i),
                                                  self.acceleration_y_values[i]))
            self.movement_x_values.append(self.euler(self.set_start_values(self.movement_x_values,
                                                                           self.stage_two.get_movement_x_values(), i),
                                                     self.speed_x_values[i]))
            self.movement_y_values.append(self.euler(self.set_start_values(self.movement_y_values,
                                                                           self.stage_two.get_movement_y_values(), i),
                                                     self.speed_y_values[i]))

        self.print_parameters()

    def x_function(self, arg):
        return (self.F * math.sin(
            self.stage_two.get_stage_one().get_end_angle() + self.stage_two.get_end_angle() +
            self.rotation_angle_function() * arg)) / (self.M - self.k * arg)

    def y_function(self, arg):
        return (self.F * math.cos(
            self.stage_two.get_stage_one().get_end_angle() + self.stage_two.get_end_angle() +
            self.rotation_angle_function() * arg)) / (self.M - self.k * arg) - self.g

    def set_stage_two(self, stage_two):
        self.stage_two = stage_two