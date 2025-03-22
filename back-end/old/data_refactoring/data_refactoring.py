import json
import pandas as pd
import category_encoders as ce
import os

make = 'bmw'
folder_path = f"data_refactoring/cars_data/{make}"
all_data = []

for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            try:
                data = json.loads(content)
                all_data.append(data)
            except json.JSONDecodeError as e:
                print(f"Nie udało się wczytać pliku {filename}: {e}")

df = pd.DataFrame(all_data)

if 'price' in df.columns:
    df['price_amount'] = df['price'].apply(lambda x: x['amount'])
    df['price_currency'] = df['price'].apply(lambda x: x['currency'])
    df.drop(columns=['price'], inplace=True)

categorical_cols = [col for col in df.columns if df[col].dtype == 'object']
cols_to_adjust = []

for col in categorical_cols:
    try:
        df[col] = pd.to_numeric(df[col], errors='raise')
    except ValueError:
        cols_to_adjust.append(col)

if 'new_used' in df.columns:
    df['new_used'] = df['new_used'].replace({'new': 1, 'used': 0})

columns_to_drop = ['make', 'has_vin', 'date_registration', 'registration', 'vin', 'has_registration', 'catalog_urn']
df.drop(columns=[col for col in columns_to_drop if col in df.columns], inplace=True)

if 'price_currency' in df.columns and 'price_amount' in df.columns:
    df.loc[df['price_currency'] == 'EUR', 'price_amount'] = df['price_amount'] * 4.25
    df.loc[df['price_currency'] == 'USD', 'price_amount'] = df['price_amount'] * 3.75
    df.drop(columns=['price_currency'], inplace=True)

rest_cat_cols = [col for col in df.columns if df[col].dtype == 'object']

if rest_cat_cols:
    encoder = ce.BinaryEncoder(cols=rest_cat_cols)
    df_encoded = encoder.fit_transform(df)
else:
    df_encoded = df

df_encoded.to_parquet(f"data_refactoring/cars_data/{make}/{make}_encoded.parquet", index=False)