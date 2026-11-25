import math

def read_point():
    """
    Запрашивает координаты точки у пользователя.

    """
    while True:
        try:
            x = float(input("Введите координату точки по оси x: "))
            y = float(input("Введите координату точки по оси y: "))
            return (x, y)  # tuple — координаты неизменяемы
        except ValueError:
            print("Ошибка: введите числовое значение.")


def collect_points():
    """
    Диалог ввода обучающих точек.

    Возвращает:
        словарь структуры {метка_класса: [(x1,y1), (x2,y2), ...]}.

    Условия завершения ввода:
        - Пользователь отказывается добавлять точки (вводит не 'y').
        - Введено не менее 2 различных меток классов.
        - Для каждой метки введено не менее 3 точек.

    Если условия не выполнены после отказа пользователя —
    программа продолжает запрашивать точки без вопроса о продолжении.
    """
    data = {}  # dict: метка класса -> список точек
    labels_set = set()  # set: множество уникальных меток

    def input_point():
        """Ввод одной точки с защитой от нечислового ввода."""
        while True:
            try:
                x = float(input("Введите координату точки по оси x: "))
                y = float(input("Введите координату точки по оси y: "))
                return (x, y)
            except ValueError:
                print("Ошибка: введите числовое значение.")

    def input_label():
        """Ввод метки класса (непустой строки)."""
        while True:
            label = input("Введите метку класса объекта: ").strip()
            if label:
                return label
            print("Метка класса не может быть пустой.")

    def check_conditions():
        """
        Проверяет обязательные условия:
        - не менее 2 различных меток классов;
        - не менее 3 точек для каждой метки.
        Возвращает True, если условия выполнены.
        """
        if len(labels_set) < 2:
            print(f"Ошибка: должно быть введено не менее 2 различных меток классов "
                  f"(сейчас введено {len(labels_set)}).")
            return False
        for label in labels_set:
            if len(data[label]) < 3:
                print(f"Ошибка: для метки '{label}' должно быть введено не менее 3 точек "
                      f"(сейчас {len(data[label])}).")
                return False
        return True

    # --- Основной цикл ввода ---
    while True:
        point = input_point()
        label = input_label()

        # Добавляем точку в словарь
        if label not in data:
            data[label] = []  # создаём новый список для новой метки
        data[label].append(point)  # добавляем точку в список
        labels_set.add(label)  # добавляем метку в множество

        # Спрашиваем, хочет ли пользователь добавить ещё точку
        cont = input("Добавить ещё одну точку? (y — да, любой другой символ — нет): "
                     ).strip().lower()
        if cont != 'y':
            if check_conditions():
                break  # все условия выполнены — выходим
            print("Условия не выполнены. Необходимо продолжить ввод точек.")

    # Если пользователь отказался, но условия не выполнены —
    # продолжаем ввод без вопроса о продолжении
    while not check_conditions():
        point = input_point()
        label = input_label()

        if label not in data:
            data[label] = []
        data[label].append(point)
        labels_set.add(label)

    return data


def read_k(total):
    """
    Запрашивает у пользователя значение k.

    Аргументы:
        total — общее число введённых точек.

    Возвращает:
        целое число k, удовлетворяющее условию 1 <= k <= total.

    Особенности:
        - Обрабатывает нечисловой ввод (ValueError).
        - Проверяет диапазон значений.
        - Повторяет запрос до получения корректного значения.
    """
    while True:
        try:
            k = int(input(f"Введите количество ближайших соседей k (1..{total}): "))
            if 1 <= k <= total:
                return k
            else:
                print(f"Ошибка: k должно быть целым числом от 1 до {total}.")
        except ValueError:
            print("Ошибка: введите целое число.")



def distance(p1, p2):
    """
    Вычисляет евклидово расстояние между двумя точками.

    Формула: d = sqrt((x1 - x2)**2 + (y1 - y2)**2)

    Аргументы:
        p1, p2 — кортежи координат (x, y).

    Возвращает:
        вещественное число — расстояние между точками.
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def neighbours(data, point, k):
    """
    Находит k ближайших соседей для заданной точки.

    Аргументы:
        data  — словарь {метка: [точки]};
        point — кортеж координат неизвестной точки;
        k     — количество соседей.

   Собирает все точки из выборки, считает расстояние от каждой
   до неизвестной точки point, сортирует по расстоянию и возвращает
    k самых близких.

    Алгоритм:
        1. Проходим по всем точкам всех классов.
        2. Для каждой точки вычисляем расстояние до point.
        3. Собираем все (расстояние, метка, координаты) в один список.
        4. Сортируем список по расстоянию.
        5. Возвращаем первые k элементов.
    """
    all_points = []
    for label, points in data.items():
        for p in points:
            d = distance(point, p)
            all_points.append((d, label, p))

    # Сортировка по первому элементу кортежа — расстоянию (по возрастанию)
    all_points.sort(key=lambda x: x[0])

    # Возвращаем k ближайших
    return all_points[:k]


def predict(data, point, k):
    """
    Предсказывает метку класса для точки point методом k-NN.

    Аргументы:
        data  — словарь обучающих данных;
        point — кортеж координат неизвестной точки;
        k     — количество соседей.

    Возвращает:
        кортеж (предсказанная_метка, словарь_голосов, список_соседей).

    """
    k_neighbours = neighbours(data, point, k)

    # Подсчёт голосов: сколько раз каждая метка встречается среди k соседей
    votes = {}
    for d, label, p in k_neighbours:
        votes[label] = votes.get(label, 0) + 1

    # Находим максимальное число голосов
    max_votes = max(votes.values())

    # Собираем метки, набравшие максимальное число голосов
    top_labels = [label for label, count in votes.items() if count == max_votes]

    # Если победитель один — возвращаем его
    if len(top_labels) == 1:
        return top_labels[0], votes, k_neighbours

    # Разрешение ничьей: ищем первого соседа из списка лидеров
    # (список отсортирован по расстоянию, поэтому первый = ближайший)
    for d, label, p in k_neighbours:
        if label in top_labels:
            return label, votes, k_neighbours

    return top_labels[0], votes, k_neighbours



def main():
    """
    Точка входа в программу.

    Последовательность действий:
        1. Сбор обучающих точек.
        2. Вывод статистики (число точек, метки классов).
        3. Ввод координат точки неизвестного класса.
        4. Ввод значения k.
        5. Классификация и вывод результатов.
    """

    # --- Шаг 1: Сбор обучающих точек ---
    print("\n--- Сбор обучающих точек ---")
    data = collect_points()

    # Подсчёт общего числа точек и получение множества меток
    total = sum(len(points) for points in data.values())
    labels_set = set(data.keys())

    print(f"\nВведено {total} точек, метки классов: {', '.join(sorted(labels_set))}")

    # --- Шаг 2: Ввод точки неизвестного класса ---
    print("\n--- Введите координаты точки неизвестного класса ---")
    while True:
        try:
            x = float(input("Введите координату точки по оси x: "))
            y = float(input("Введите координату точки по оси y: "))
            predict_point = (x, y)
            break
        except ValueError:
            print("Ошибка: введите числовое значение.")

    # --- Шаг 3: Ввод k ---
    k = read_k(total)

    # --- Шаг 4: Классификация ---
    predicted_label, votes, k_neighbours = predict(data, predict_point, k)

    # --- Шаг 5: Вывод результатов ---
    print(f"\nБлижайшие соседи точки {predict_point}:")
    for d, label, p in k_neighbours:
        print(f"  {p}  расстояние {round(d, 2)}  метка {label}")

    # Вывод голосов, отсортированных по убыванию (для наглядности)
    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    votes_str = ", ".join(f"{label} – {count}" for label, count in sorted_votes)
    print(f"\nГолоса: {votes_str}")
    print(f"Предсказанная метка класса: {predicted_label}")

if __name__ == '__main__':
    main()