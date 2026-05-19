import numpy as np
from sklearn.neighbors import KNeighborsClassifier

# TODO: 우리카드 900만건 데이터로 학습
LIFECYCLE_STAGES = ["사회초년생", "신혼기", "자녀양육기", "중년기", "은퇴기"]

class LifecycleModel:
    def __init__(self):
        self.model = KNeighborsClassifier(n_neighbors=5)
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, age: int, monthly_spend: float, top_category: str) -> str:
        if not self.is_trained:
            # TODO: 실제 모델 로드
            return "사회초년생"
        X = np.array([[age, monthly_spend]])
        return self.model.predict(X)[0]

lifecycle_model = LifecycleModel()