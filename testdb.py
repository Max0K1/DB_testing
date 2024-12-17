import time
import random
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Author, Book  # Імпорт моделей

# Параметри підключення до бази даних
DATABASE_URL = "youurl"

# Підключення до бази даних
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Вимірювання часу
def measure_time(func, *args):
    start = time.time()
    result = func(*args)
    elapsed = round(time.time() - start, 4)
    return elapsed, result

# Очистка таблиць
def clear_tables(session):
    session.query(Book).delete()
    session.query(Author).delete()
    session.commit()

# Операції для тестування
def insert_rows(session, count):
    authors = [
        Author(name=f"Author {random.randint(1, 1000)}", books=[
            Book(title=f"Book {random.randint(1, 1000)}")
        ]) for _ in range(count)
    ]
    session.bulk_save_objects(authors)
    session.commit()

def select_rows(session, count):
    return session.query(Author).limit(count).all()

def update_rows(session, count):
    ids = session.query(Author.id).limit(count).all()
    ids = [id[0] for id in ids]
    session.query(Author).filter(Author.id.in_(ids)).update(
        {Author.name: f"Updated {random.randint(1, 1000)}"},
        synchronize_session=False
    )
    session.commit()

def delete_rows(session, count):
    ids = session.query(Author.id).limit(count).all()
    ids = [id[0] for id in ids]
    session.query(Author).filter(Author.id.in_(ids)).delete(synchronize_session=False)
    session.commit()

# Основна функція
def test_operations():
    row_counts = [1000, 10000, 100000, 1000000]  # Обсяги даних
    operations = [
        ("INSERT", insert_rows),
        ("SELECT", select_rows),
        ("UPDATE", update_rows),
        ("DELETE", delete_rows),
    ]
    
    results = []  # Збираємо результати для таблиці

    for operation_name, operation_func in operations:
        print(f"\nTesting {operation_name} operation:")

        for count in row_counts:
            with Session() as session:
                clear_tables(session)  # Очистка перед кожним новим обсягом

                # Вставка даних для SELECT/UPDATE/DELETE
                if operation_name != "INSERT":
                    insert_rows(session, count)

                # Вимірювання часу операції
                elapsed_time, _ = measure_time(operation_func, session, count)

                # Збереження результатів
                results.append([operation_name, count, elapsed_time])
                print(f"{operation_name} {count} records: {elapsed_time} seconds")

    # Запис результатів у CSV
    with open("performance_results.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Operation", "Record Count", "Elapsed Time (s)"])
        writer.writerows(results)
    print("\nResults saved to 'performance_results.csv'")

if __name__ == "__main__":
    test_operations()