import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import joblib

df = pd.read_csv('C:\\Users\\szymo\\Desktop\\PythonProjects\\PUM_semester_project\\data_refactoring\\cars_data\\bmw\\extracted_bmw_data\\bmw_encoded.csv')

y = df['price_amount']
X = df.drop(columns=['price_amount'])

def model_handler(X, y, random_state=1):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=random_state)

    models = [
        {
            'name': 'RandomForestRegressor',
            'model': RandomForestRegressor(random_state=random_state),
            'params': {
                'n_estimators': [100, 200, 300, 400, 500],
                'max_depth': [None, 10, 20, 30, 40, 50],
                'min_samples_split': [2, 5, 10]
            }
        },
        {
            'name': 'GradientBoostingRegressor',
            'model': GradientBoostingRegressor(random_state=random_state),
            'params': {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.1, 0.5],
                'max_depth': [3, 5, 7]
            }
        },
        {
            'name': 'XGBRegressor',
            'model': XGBRegressor(random_state=random_state),
            'params': {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.01, 0.1, 0.5],
                'max_depth': [3, 5, 7]
            }
        },
        {
            'name': 'LGBMRegressor',
            'model': LGBMRegressor(random_state=random_state),
            'params': {
                'n_estimators': [100, 200],
                'learning_rate': [0.01, 0.1],
                'max_depth': [3, 5]
            }
        },
        {
            'name': 'LinearRegression',
            'model': LinearRegression(),
            'params': {}
        }
    ]

    best_model = None
    best_mae = float('inf')
    best_model_name = ""

    for model_config in models:
        print(f"Training model: {model_config['name']}")
        
        grid_search = GridSearchCV(model_config['model'], model_config['params'], scoring='neg_mean_absolute_error', cv=5, n_jobs=-1, verbose=1)

        grid_search.fit(X_train, y_train)

        y_pred = grid_search.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        print(f"MAE for {model_config['name']}: {mae}")
        print(f"Best parameters: {grid_search.best_params_}")

        if mae < best_mae:
            best_mae = mae
            best_model = grid_search
            best_model_name = model_config['name']

    print(f"Best model: {best_model_name}")
    print(f"Lowest MAE: {best_mae}")
    return best_model

best_model = model_handler(X, y)
joblib.dump(best_model, 'machine_learning/bmw_model.pkl')