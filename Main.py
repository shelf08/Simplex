def is_linear(coefficients):
    # Проверьте, все ли коэффициенты являются числами.
    return all(isinstance(c, (int, float)) for c in coefficients)


def round_value(val, accuracy):
    return round(val, accuracy)


def simplex(obj, constraints, rhs, accuracy, is_maximization):
    n = len(obj)
    m = len(constraints)

    if not is_maximization:
        obj = [-x for x in obj]

    # Строим симплекс таблицу
    table = [[0 for _ in range(n + 1 + m)] for _ in range(m + 1)]  # создание

    for i in range(n):
        table[0][i] = -obj[i]  # Заполняем z-строку

    for i in range(1, m + 1):  # заполняем ограничения
        for j in range(n):
            if j < len(constraints[i - 1]):
                table[i][j] = constraints[i - 1][j]

    table[0][-1] = 0  # заполняем правую часть z
    for i in range(1, m + 1):  # заполняем правую часть других строк
        table[i][-1] = rhs[i - 1]

    for i in range(1, m + 1):  # заполняем значения замедления
        for j in range(n, n + m):
            if j - n == i - 1:
                table[i][j] = 1

    # инициализируем базовые переменные
    basis = [n + i for i in range(m)]  # [n, n+1, ..., n+m-1]

    # инициализируем ответы и z_value

    z_value = 0  # при этом сохраняется значение целевой функции

    while any(round_value(x, accuracy) < 0 for x in table[0][:-1]):  # Исключить правую часть в z-строке
        key_col = -1
        min_val = float('inf')

        # находим самый большой по модулю отрицательный столбец для переворота
        for i in range(n + m):
            if round_value(table[0][i], accuracy) < round_value(min_val, accuracy):
                min_val = table[0][i]
                key_col = i

        if key_col == -1:
            print("No valid pivot column found. The method is not applicable!")
            exit()

        key_row = -1
        min_ratio = float('inf')

        # находим строку для переворота
        for i in range(1, m + 1):
            if round_value(table[i][key_col], accuracy) > 0:
                ratio = table[i][-1] / table[i][key_col]
                if 0 <= round_value(ratio, accuracy) < round_value(min_ratio, accuracy):
                    min_ratio = ratio
                    key_row = i

        if key_row == -1:
            print("Неограниченное решение. Этот метод неприменим!")
            exit()

        # переворачиваем
        pivot = table[key_row][key_col]
        for i in range(n + m + 1):
            table[key_row][i] = round_value(table[key_row][i] / pivot, accuracy)

        for i in range(m + 1):  # делаем все нули в ключевом столбце, кроме ключевой строки
            if i != key_row:
                divisor = table[i][key_col]
                for j in range(n + m + 1):
                    table[i][j] = round_value(table[i][j] - divisor * table[key_row][j], accuracy)

        # обновляем базис
        basis[key_row - 1] = key_col  # обновляем базис с новой переменной

        # проверка на дегенерацию
        if round_value(table[key_row][-1], accuracy) == 0:
            print(f"Обнаружена дегенерация в строке {key_row}. Базовой переменной является ноль.")

        z_value = round_value(table[0][-1], accuracy)  # обновляем текущее значение z


    # после завершения цикла определяем переменные принятия решения
    answers = [0] * n  # инициализируем все переменные принятия решения равными нулю
    for i in range(m):
        if basis[i] < n:  # присваиваем значения только переменным принятия решений, а не переменным замедления
            answers[basis[i]] = round_value(table[i + 1][-1], accuracy)  # присваиваем значения правой части

    return z_value, answers


def input_values():
    # Input validation
    try:
        print("Введите коэффициенты целевой функции, разделенные пробелом:")
        obj = list(map(float, input().split()))  # смотрим, чтоб все значения являются float
        if not is_linear(obj):
            raise ValueError("Нелинейные коэффициенты в целевой функции.")
        n = len(obj)

        print("Введите количество ограничений:")
        m = int(input())
        constraints = []

        print("Введите коэффициенты функции ограничения, разделенные пробелом (каждое ограничение в каждой строке).:")
        for i in range(m):
            constraint = list(map(float, input().split()))
            if len(constraint) > n:  # проверка, каждое ограничение содержит правильное количество коэффициентов
                raise ValueError("Неправильное количество коэффициентов в ограничениях.")
            if not is_linear(constraint):
                raise ValueError("Нелинейные коэффициенты в ограничениях.")
            constraints.append(constraint)

        print("Введите цифры справа, разделенные пробелом:")
        rhs = list(map(float, input().split()))
        if len(rhs) != m:
            raise ValueError("Количество значений RHS не соответствует количеству ограничений.")

        print("Введите точность (количество знаков после запятой для округления):")
        accuracy = int(input())

        print("Функция стремится к: (max/min):")
        is_maximization = input().lower() == 'max'

    except ValueError:
        print("Этот метод неприменим!")
        exit()

    return obj, constraints, rhs, accuracy, is_maximization


def output_values(z_value, answers, is_maximization):
    # ** Обновленная функция вывода**
    # 1. Выводим задачу оптимизации
    if is_maximization:
        optimization_type = "Максимизация"
    else:
        optimization_type = "Минимизация"

    # создаем строку целевой функции
    objective_terms = []
    for i, coeff in enumerate(obj):
        term = f"{coeff}*x{i + 1}"
        objective_terms.append(term)
    objective_str = " + ".join(objective_terms)

    print(f"{optimization_type} z = {objective_str}")

    # выводим ограничения
    print("с ограничениями:")
    for i, constraint in enumerate(constraints):
        constraint_terms = []
        for j, coeff in enumerate(constraint):
            term = f"{coeff}*x{j + 1}"
            constraint_terms.append(term)
        constraint_str = " + ".join(constraint_terms)
        print(f"{constraint_str} <= {rhs[i]}")

    print()

    # 2. Вывод решения
    # выводим значения переменных принятия решения
    for i in range(len(answers)):
        print(f"x^*{i + 1} =", answers[i])

    if is_maximization:
        print("z^* =", z_value)
    else:
        print("z^* =", -z_value)




obj, constraints, rhs, accuracy, is_maximization = input_values()

z_value, answers = simplex(obj, constraints, rhs, accuracy, is_maximization)
output_values(z_value, answers, is_maximization)
