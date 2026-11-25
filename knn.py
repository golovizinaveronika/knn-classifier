import math
import json

DATA_FILE = "data.json"

def read_point():
    while True:
        try:
            x = float(input("Введите координату точки по оси x: "))
            y = float(input("Введите координату точки по оси y: "))
            return (x, y)
        except ValueError:
            print("Ошибка: введите числовое значение.")

def collect_points():
    data = {}
    labels_set = set()

    def input_point():
        while True:
            try:
                x = float(input("Введите координату точки по оси x: "))
                y = float(input("Введите координату точки по оси y: "))
                return (x, y)
            except ValueError:
                print("Ошибка: введите числовое значение.")

    def input_label():
        while True:
            label = input("Введите метку класса объекта: ").strip()
            if label:
                return label
            print("Метка класса не может быть пустой.")

    def check_conditions():
        if len(labels_set) < 2:
            print(f"Ошибка: должно быть введено не менее 2 различных меток классов (сейчас введено {len(labels_set)}).")
            return False
        for label in labels_set:
            if len(data[label]) < 3:
                print(f"Ошибка: для метки '{label}' должно быть введено не менее 3 точек (сейчас {len(data[label])}).")
                return False
        return True

    while True:
        point = input_point()
        label = input_label()
        if label not in data:
            data[label] = []
        data[label].append(point)
        labels_set.add(label)

        cont = input("Добавить ещё одну точку? (y — да, любой другой символ — нет): ").strip().lower()
        if cont != 'y':
            if check_conditions():
                break
            print("Условия не выполнены. Необходимо продолжить ввод точек.")

    while not check_conditions():
        point = input_point()
        label = input_label()
        if label not in data:
            data[label] = []
        data[label].append(point)
        labels_set.add(label)

    return data

def read_k(total):
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
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def neighbours(data, point, k):
    all_points = []
    for label, points in data.items():
        for p in points:
            d = distance(point, p)
            all_points.append((d, label, p))
    all_points.sort(key=lambda x: x[0])
    return all_points[:k]

def predict(data, point, k):
    k_neighbours = neighbours(data, point, k)
    votes = {}
    for d, label, p in k_neighbours:
        votes[label] = votes.get(label, 0) + 1
    max_votes = max(votes.values())
    top_labels = [label for label, count in votes.items() if count == max_votes]
    if len(top_labels) == 1:
        return top_labels[0], votes, k_neighbours
    for d, label, p in k_neighbours:
        if label in top_labels:
            return label, votes, k_neighbours
    return top_labels[0], votes, k_neighbours

def save_data(data, path):
    plain = {label: [list(p) for p in points] for label, points in data.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plain, f, ensure_ascii=False)

def load_data(path):
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return {label: [tuple(p) for p in points] for label, points in raw.items()}

def remove_label(data, label_to_remove):
    if label_to_remove in data:
        del data[label_to_remove]
        return True
    return False

def check_data_validity(data):
    labels = set(data.keys())
    if len(labels) < 2:
        return False
    for label in labels:
        if len(data[label]) < 3:
            return False
    return True

def main():
    data = load_data(DATA_FILE)

    if data is not None:
        total = sum(len(p) for p in data.values())
        print(f"\nНайдена сохранённая выборка ({total} точек).")
        answer = input("Использовать сохранённую выборку? (y/n): ").strip().lower()

        if answer == 'y':
            labels = sorted(data.keys())
            print(f"\nТекущие метки классов: {', '.join(labels)}")
            remove_answer = input("Хотите удалить какую-то метку класса? (y/n): ").strip().lower()

            if remove_answer == 'y':
                label_to_remove = input("Введите метку для удаления: ").strip()
                if remove_label(data, label_to_remove):
                    print(f"Метка '{label_to_remove}' удалена.")
                    if not check_data_validity(data):
                        print("Ошибка: после удаления метки выборка не удовлетворяет условиям. Будет запрошен ввод новых точек.")
                        data = None
                    else:
                        save_data(data, DATA_FILE)
                        print("Выборка сохранена после удаления метки.")
                else:
                    print(f"Метка '{label_to_remove}' не найдена в выборке.")
        else:
            data = None

    if data is None:
        print("\n--- Сбор обучающих точек ---")
        data = collect_points()
        save_data(data, DATA_FILE)
        print("Выборка сохранена.")

    total = sum(len(points) for points in data.values())
    labels_set = set(data.keys())
    print(f"\nВведено {total} точек, метки классов: {', '.join(sorted(labels_set))}")

    print("\n--- Введите координаты точки неизвестного класса ---")
    while True:
        try:
            x = float(input("Введите координату точки по оси x: "))
            y = float(input("Введите координату точки по оси y: "))
            predict_point = (x, y)
            break
        except ValueError:
            print("Ошибка: введите числовое значение.")

    k = read_k(total)
    predicted_label, votes, k_neighbours = predict(data, predict_point, k)

    print(f"\nБлижайшие соседи точки {predict_point}:")
    for d, label, p in k_neighbours:
        print(f"  {p}  расстояние {round(d, 2)}  метка {label}")

    sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    votes_str = ", ".join(f"{label} – {count}" for label, count in sorted_votes)
    print(f"\nГолоса: {votes_str}")
    print(f"Предсказанная метка класса: {predicted_label}")

if __name__ == '__main__':
    main()