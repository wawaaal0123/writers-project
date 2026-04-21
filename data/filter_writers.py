import pandas as pd

# 1. Загружаем исходный CSV
df = pd.read_csv("writers_karelia_raw.csv")

print(f"Исходных записей: {len(df)}")

# 2. Заполняем пустые значения (NaN) на False
df['isWriter'] = df['isWriter'].fillna(False)
df['isPoet'] = df['isPoet'].fillna(False)

# 3. Фильтруем: оставляем только писателей или поэтов
writers_df = df[(df['isWriter'] == True) | (df['isPoet'] == True)]

print(f"Отфильтровано (писатели и поэты): {len(writers_df)}")

# 4. Сохраняем в НОВЫЙ файл
writers_df.to_csv("writers_karelia_clean.csv", index=False, encoding="utf-8")

print("Создан новый файл: writers_karelia_clean.csv")
