from app import app  # Импортируем экземпляр приложения из app.py
from models import db, Promt

def add_and_print_promts():
    with app.app_context():
        # Создание нового Promt
        new_promt = Promt(status='NEW', n_text='Sample n_text', text='Sample text')
        db.session.add(new_promt)
        db.session.commit()
        print("Новый Promt добавлен успешно.")

        # Запрос к существующим Promt
        promts = Promt.query.all()
        for promt in promts:
            print(promt.id, promt.status, promt.n_text, promt.text)

if __name__ == '__main__':
    add_and_print_promts()