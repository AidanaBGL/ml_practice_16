"""
Question definitions. Edit/add freely — `id` must stay unique.

Types:
  single     — radio buttons, one correct
  multi      — checkboxes, set must match exactly
  match      — left items, dropdown of right items per row
  order      — drag to reorder
  bins       — drag items into named buckets
  code_fill  — code with blanks (textareas), normalized exact match
  sabotage   — pick the buggy line of code
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Question:
    id: str
    type: str
    title: str
    body: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    correct: Any = None
    points: int = 100
    speed_window_s: int = 30
    speed_bonus_pct: int = 50


QUESTIONS: list[Question] = [
    Question(
        id="q01_terms",
        type="match",
        title="Сопоставь термин и определение",
        body="К каждому понятию слева — подходящее определение справа.",
        data={
            "left": [
                ("PCA", "PCA"),
                ("t-SNE", "t-SNE"),
                ("UMAP", "UMAP"),
                ("Cluster", "Кластеризация"),
            ],
            "right": [
                ("a", "Линейный метод, максимизирует дисперсию проекций"),
                ("b", "Нелинейная визуализация: сохраняет соседство точек"),
                ("c", "Нелинейный метод с .transform() для новых точек"),
                ("d", "Группирует похожие наблюдения в группы"),
            ],
        },
        correct={"PCA": "a", "t-SNE": "b", "UMAP": "c", "Cluster": "d"},
    ),

    Question(
        id="q02_why_dimred",
        type="multi",
        title="Зачем нужно снижать размерность?",
        body="Выбери всё, что относится к причинам.",
        data={
            "options": [
                ("vis", "Визуализация в 2D/3D"),
                ("speed", "Ускорение обучения моделей"),
                ("reg", "Регуляризация и борьба с переобучением"),
                ("emb", "Получение эмбеддингов"),
                ("crypto", "Шифрование данных"),
                ("storage", "Иногда уменьшение объёма хранения"),
            ],
        },
        correct=["vis", "speed", "reg", "emb", "storage"],
    ),

    Question(
        id="q03_pca_goal",
        type="single",
        title="Цель PCA — это…",
        body="",
        data={
            "options": [
                ("var", "Найти направления максимальной дисперсии"),
                ("corr", "Максимизировать корреляцию между признаками"),
                ("class", "Максимизировать разделимость классов"),
                ("noise", "Удалить шум по уровню энтропии"),
            ],
        },
        correct="var",
    ),

    Question(
        id="q04_pca_steps",
        type="order",
        title="Расставь шаги PCA по порядку",
        body="От первого к последнему.",
        data={
            "items": [
                ("center", "Центрирование: вычесть среднее по признакам"),
                ("cov", "Ковариационная матрица Σ = (1/n)·XᵀX"),
                ("eig", "Решить Σv = λv (собственные векторы)"),
                ("sort", "Отсортировать по убыванию λ, взять top-K"),
                ("proj", "Спроецировать: Z = X·V_K"),
            ],
        },
        correct=["center", "cov", "eig", "sort", "proj"],
    ),

    Question(
        id="q05_choose_k",
        type="multi",
        title="Как выбрать K компонент?",
        body="Выбери все валидные подходы.",
        data={
            "options": [
                ("elbow", "Метод локтя на explained_variance_ratio_"),
                ("threshold", "Накопленная дисперсия ≥ 0.95"),
                ("random", "Взять K = √n_features наугад"),
                ("cv", "Кросс-валидация по downstream-метрике"),
                ("max", "Всегда брать K = n_features"),
            ],
        },
        correct=["elbow", "threshold", "cv"],
    ),

    Question(
        id="q06_pros_cons",
        type="bins",
        title="Перетащи характеристики в плюсы и минусы PCA",
        body="",
        data={
            "bins": [("pros", "Плюсы PCA"), ("cons", "Минусы PCA")],
            "items": [
                ("fast", "Очень быстро, есть IncrementalPCA"),
                ("det", "Детерминирован"),
                ("inv", "Есть обратное преобразование"),
                ("predict", "Predict для новых точек"),
                ("interp", "Интерпретируем (loadings)"),
                ("global", "Сохраняет глобальную структуру"),
                ("linear", "Только линейные зависимости"),
                ("outlier", "Чувствителен к выбросам"),
                ("gauss", "Подразумевает гауссовость"),
                ("ortho", "Все компоненты ортогональны"),
                ("mixclass", "Может перемешать классы"),
            ],
        },
        correct={
            "pros": ["fast", "det", "inv", "predict", "interp", "global"],
            "cons": ["linear", "outlier", "gauss", "ortho", "mixclass"],
        },
    ),

    Question(
        id="q07_pca_code",
        type="code_fill",
        title="Допиши PCA",
        body="""Тебя позвали в стартап с датасетом из 200 признаков.
Допиши код так, чтобы получить 10 компонент и применить к новым данным.""",
        data={
            "template": (
                "from sklearn.decomposition import PCA\n"
                "from sklearn.preprocessing import StandardScaler\n"
                "\n"
                "scaler = StandardScaler()\n"
                "X_sc = scaler.fit_transform(X)\n"
                "\n"
                "pca = ___1___\n"
                "X_pca = ___2___\n"
                "\n"
                "X_new_sc = scaler.transform(X_new)\n"
                "X_new_pca = ___3___\n"
            ),
            "blanks": [
                ("1", "PCA(...)"),
                ("2", "fit_transform"),
                ("3", "transform"),
            ],
        },
        correct={
            "1": ["pca(n_components=10)", "pca(n_components=10, random_state=42)"],
            "2": ["pca.fit_transform(x_sc)"],
            "3": ["pca.transform(x_new_sc)"],
        },
    ),

    Question(
        id="q08_variance_code",
        type="code_fill",
        title="PCA по доле дисперсии",
        body="Хотим оставить 95% дисперсии — допиши.",
        data={
            "template": (
                "pca = ___1___\n"
                "X_pca = ___2___\n"
            ),
            "blanks": [
                ("1", "PCA(...)"),
                ("2", "fit_transform"),
            ],
        },
        correct={
            "1": ["pca(n_components=0.95)", "pca(0.95)"],
            "2": ["pca.fit_transform(x_sc)"],
        },
    ),

    Question(
        id="q09_tsne_truth",
        type="single",
        title="Что верно про t-SNE?",
        body="",
        data={
            "options": [
                ("nbrs", "Сохраняет локальную структуру: близкие соседи остаются близкими"),
                ("global", "Сохраняет глобальные расстояния между всеми точками"),
                ("predict", "У него есть .transform() для новых точек"),
                ("linear", "Это линейный метод"),
            ],
        },
        correct="nbrs",
    ),

    Question(
        id="q10_sabotage_pca",
        type="sabotage",
        title="Sabotage round: найди баг",
        body="""В коде ровно одна ошибка, которая ломает результат.
Какая строка виновна?""",
        data={
            "code_lines": [
                "from sklearn.decomposition import PCA",
                "from sklearn.preprocessing import StandardScaler",
                "",
                "scaler = StandardScaler()",
                "X_train_sc = scaler.fit_transform(X_train)",
                "X_test_sc  = scaler.fit_transform(X_test)",
                "",
                "pca = PCA(n_components=10, random_state=42)",
                "X_train_pca = pca.fit_transform(X_train_sc)",
                "X_test_pca  = pca.transform(X_test_sc)",
            ],
        },
        correct=5,  # 0-indexed: scaler.fit_transform(X_test) — leak/refit
    ),

    Question(
        id="q11_sabotage_tsne",
        type="sabotage",
        title="Sabotage round: t-SNE",
        body="Один из шагов делает плохо. Какой?",
        data={
            "code_lines": [
                "from sklearn.manifold import TSNE",
                "from sklearn.preprocessing import StandardScaler",
                "",
                "X_sc = StandardScaler().fit_transform(X)",
                "",
                "tsne = TSNE(n_components=2, perplexity=30, init='pca', random_state=42)",
                "X_tsne = tsne.fit_transform(X_sc)",
                "",
                "X_new_tsne = tsne.transform(X_new)",
            ],
        },
        correct=8,  # tsne has no .transform()
    ),

    Question(
        id="q12_umap_code",
        type="code_fill",
        title="UMAP для визуализации",
        body="2D-визуализация, n_neighbors=15, min_dist=0.1, фиксированный seed.",
        data={
            "template": (
                "import umap\n"
                "from sklearn.preprocessing import StandardScaler\n"
                "\n"
                "X_sc = StandardScaler().fit_transform(X)\n"
                "reducer = ___1___\n"
                "X_umap = ___2___\n"
            ),
            "blanks": [
                ("1", "umap.UMAP(...)"),
                ("2", "fit_transform"),
            ],
        },
        correct={
            "1": [
                "umap.umap(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)",
                "umap.umap(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)",
            ],
            "2": ["reducer.fit_transform(x_sc)"],
        },
    ),
]


def by_id(qid: str) -> Question:
    for q in QUESTIONS:
        if q.id == qid:
            return q
    raise KeyError(qid)
