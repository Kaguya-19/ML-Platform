from pypmml import Model
from nyoka import xgboost_to_pmml
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import pandas as pd
from xgboost import XGBClassifier

seed = 123456

iris = datasets.load_iris()
target = 'Species'
features = iris.feature_names
iris_df = pd.DataFrame(iris.data, columns=features)
iris_df[target] = iris.target

X, y = iris_df[features], iris_df[target]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=seed)

pipeline = Pipeline([
    ('scaling', StandardScaler()),
    ('xgb', XGBClassifier(n_estimators=5, seed=seed))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
y_pred_proba = pipeline.predict_proba(X_test)
xgboost_to_pmml(pipeline, features, target, "xgb-iris.pmml")

model = Model.load("xgb-iris.pmml")
result = pd.DataFrame(model.predict(X_test))
print(result)
