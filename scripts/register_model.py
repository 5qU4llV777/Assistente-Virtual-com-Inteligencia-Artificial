import mlflow
import mlflow.pyfunc
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def main():
    # Define o experimento
    mlflow.set_experiment("gandalf-mlops")

    # Carrega dataset de exemplo
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )

    # Treina modelo simples
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    # Inicia o run no MLflow
    with mlflow.start_run():
        mlflow.log_param("modelo", "LogisticRegression")
        mlflow.log_metric("accuracy", model.score(X_test, y_test))

        # Registra o modelo
        mlflow.sklearn.log_model(model, "model")

        print("✅ Modelo registrado com sucesso no MLflow!")

if __name__ == "__main__":
    main()
