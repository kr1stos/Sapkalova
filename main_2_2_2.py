import table
import task_2_1_3

a = input("Введите вид обработки данных: (Статистика или Вакансии)")
if a == "Статистика":
    task_2_1_3.get_answer()
elif a == "Вакансия":
    table.get_answer()
else:
    print("Некорректный ввод комманды")