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
        body="Задание: для каждого понятия слева выбери в выпадающем списке справа подходящее определение.",
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
        body="Задание: отметь галочками все варианты, которые являются реальной причиной. Несколько ответов могут быть правильными.",
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
        body="Задание: выбери ровно один правильный вариант.",
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
        body="Задание: перетащи карточки так, чтобы шаги шли от первого к последнему сверху вниз.",
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
        body="Задание: отметь галочками все валидные подходы к выбору числа компонент K. Несколько ответов могут быть правильными.",
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
        title="Плюсы и минусы PCA",
        body="Задание: перетащи каждую карточку из левой колонки «Карман» в нужный столбец — «Плюсы PCA» или «Минусы PCA».",
        data={
            "bins": [("pros", "Плюсы PCA"), ("cons", "Минусы PCA")],
            "items": [
              ("linear", "Только линейные зависимости"),
                ("outlier", "Чувствителен к выбросам"),
                ("gauss", "Подразумевает гауссовость"),
                ("ortho", "Все компоненты ортогональны"),
                ("mixclass", "Может перемешать классы"),
                ("fast", "Очень быстро, есть IncrementalPCA"),
                ("det", "Детерминирован"),
                ("inv", "Есть обратное преобразование"),
                ("predict", "Predict для новых точек"),
                ("interp", "Интерпретируем (loadings)"),
                ("global", "Сохраняет глобальную структуру"),
                
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
Задание: впиши в каждое поле ___1___, ___2___, ___3___ ровно тот фрагмент кода, который должен быть на этом месте, чтобы получить 10 компонент и применить к новым данным.""",
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
        body="Задание: впиши в поля ___1___ и ___2___ нужный код, чтобы оставить 95% дисперсии и применить преобразование к X_sc.",
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
        body="Задание: выбери ровно один правильный вариант.",
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
        body="Задание: в коде ровно одна ошибка, которая ломает результат. Кликни по строке.",
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
        body="Задание: один из шагов написан неправильно и упадёт или даст бессмысленный результат. Кликни по строке.",
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
        body="Задание: впиши в поля ___1___ и ___2___ код для 2D-визуализации с n_neighbors=15, min_dist=0.1, фиксированным seed=42.",
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
                ("1", ""),
                ("2", ""),
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

    Question(
        id="q13_evr",
        type="single",
        title="Что показывает pca.explained_variance_ratio_?",
        body="Задание: выбери ровно один правильный вариант.",
        data={
            "options": [
                ("ratio", "Долю общей дисперсии, которую объясняет каждая компонента"),
                ("eig", "Сами собственные значения ковариационной матрицы"),
                ("mean", "Среднее по признакам после центрирования"),
                ("acc", "Точность модели после применения PCA"),
            ],
        },
        correct="ratio",
    ),

    Question(
        id="q14_sabotage_ncomp",
        type="sabotage",
        title="Sabotage round: PCA на маленьком датасете",
        body="Задание: одна строка приведёт к ошибке или некорректному результату. Кликни по ней.",
        data={
            "code_lines": [
                "import numpy as np",
                "from sklearn.decomposition import PCA",
                "from sklearn.preprocessing import StandardScaler",
                "",
                "X = np.random.randn(50, 20)",
                "X_sc = StandardScaler().fit_transform(X)",
                "",
                "pca = PCA(n_components=100, random_state=42)",
                "X_pca = pca.fit_transform(X_sc)",
            ],
        },
        correct=7,  # n_components > min(n_samples, n_features)
    ),

    Question(
        id="q15_when_tsne",
        type="multi",
        title="Когда лучше выбрать t-SNE, а не PCA?",
        body="Задание: отметь все ситуации, в которых t-SNE подходит лучше PCA. Несколько ответов могут быть правильными.",
        data={
            "options": [
                ("vis2d", "Хочется визуализацию в 2D, где соседи остаются соседями"),
                ("clusters", "Нужно увидеть кластерную структуру данных"),
                ("nonlinear", "В данных явно нелинейная структура"),
                ("global", "Нужно сохранить глобальные расстояния между всеми точками"),
                ("predict", "Нужно применить преобразование к новым точкам через .transform()"),
                ("speed", "Нужен максимально быстрый и детерминированный метод"),
            ],
        },
        correct=["vis2d", "clusters", "nonlinear"],
    ),

    Question(
        id="q16_perplexity",
        type="single",
        title="Что контролирует perplexity в t-SNE?",
        body="Задание: выбери ровно один правильный вариант.",
        data={
            "options": [
                ("nbrs", "Эффективное число соседей, которое t-SNE учитывает для каждой точки"),
                ("lr", "Скорость обучения градиентного спуска"),
                ("seed", "Случайное зерно генератора"),
                ("iters", "Количество итераций оптимизации"),
            ],
        },
        correct="nbrs",
    ),

    Question(
        id="q17_methods_match",
        type="match",
        title="Сопоставь метод и его сильную сторону",
        body="Задание: для каждого метода слева выбери в списке справа его главное преимущество.",
        data={
            "left": [
                ("PCA", "PCA"),
                ("TSNE", "t-SNE"),
                ("UMAP", "UMAP"),
                ("IncrementalPCA", "IncrementalPCA"),
            ],
            "right": [
                ("a", "Линейный, быстрый, есть .transform() и обратное преобразование"),
                ("b", "Визуализация локальной структуры в 2D/3D"),
                ("c", "Нелинейный, есть .transform(), supervised-режим"),
                ("d", "Обучение по батчам — для очень больших данных"),
            ],
        },
        correct={"PCA": "a", "TSNE": "b", "UMAP": "c", "IncrementalPCA": "d"},
    ),

    Question(
        id="q18_evr_code",
        type="single",
        title="Сколько компонент нужно для 95% дисперсии?",
        body="Задание: выбери код, который корректно считает минимальное число компонент для покрытия 95% дисперсии.",
        data={
            "options": [
                ("cumsum", "np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.95) + 1"),
                ("sum", "np.sum(pca.explained_variance_ratio_ >= 0.95)"),
                ("where", "np.where(pca.explained_variance_ratio_ > 0.95)[0][0]"),
                ("ratio", "int(len(pca.explained_variance_ratio_) * 0.95)"),
            ],
        },
        correct="cumsum",
    ),

    Question(
        id="q19_umap_advantages",
        type="multi",
        title="Чем UMAP лучше t-SNE на практике?",
        body="Задание: отметь все реальные преимущества UMAP. Несколько ответов могут быть правильными.",
        data={
            "options": [
                ("transform", "Есть .transform() для новых точек"),
                ("supervised", "Есть supervised-режим (UMAP с y=labels)"),
                ("speed", "Обычно работает быстрее t-SNE на больших датасетах"),
                ("global", "Лучше сохраняет глобальную структуру"),
                ("det", "Полностью детерминирован без random_state"),
                ("linear", "Линейная модель"),
            ],
        },
        correct=["transform", "supervised", "speed", "global"],
    ),

    Question(
        id="q20_sabotage_umap",
        type="sabotage",
        title="Sabotage round: UMAP train/test",
        body="Задание: одна строка делает плохо для пайплайна с трейном и тестом. Кликни по ней.",
        data={
            "code_lines": [
                "import umap",
                "from sklearn.preprocessing import StandardScaler",
                "",
                "scaler = StandardScaler().fit(X_train)",
                "X_train_sc = scaler.transform(X_train)",
                "X_test_sc  = scaler.transform(X_test)",
                "",
                "reducer = umap.UMAP(n_components=2, random_state=42)",
                "X_train_umap = reducer.fit_transform(X_train_sc)",
                "X_test_umap  = reducer.fit_transform(X_test_sc)",
            ],
        },
        correct=9,  # should be reducer.transform(X_test_sc)
    ),
]


def by_id(qid: str) -> Question:
    for q in QUESTIONS:
        if q.id == qid:
            return q
    raise KeyError(qid)
