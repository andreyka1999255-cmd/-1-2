import unittest
from app import app, solve_quadratic


class TestSolveQuadratic(unittest.TestCase):
    """Тесты для функции solve_quadratic()"""

    def test_two_roots(self):
        """D > 0: два различных вещественных корня"""
        result, error = solve_quadratic(1, -5, 6)
        self.assertIsNone(error)
        self.assertEqual(result["type"], "two_roots")
        self.assertEqual(result["x1"], 3.0)
        self.assertEqual(result["x2"], 2.0)

    def test_one_root(self):
        """D = 0: один кратный корень"""
        result, error = solve_quadratic(1, -2, 1)
        self.assertIsNone(error)
        self.assertEqual(result["type"], "one_root")
        self.assertEqual(result["x"], 1.0)

    def test_complex_roots(self):
        """D < 0: два комплексных корня"""
        result, error = solve_quadratic(1, 0, 1)
        self.assertIsNone(error)
        self.assertEqual(result["type"], "complex_roots")
        self.assertEqual(result["discriminant"], -4)

    def test_a_is_zero(self):
        """a = 0: не квадратное уравнение — ошибка"""
        result, error = solve_quadratic(0, 5, 3)
        self.assertIsNone(result)
        self.assertIsNotNone(error)

    def test_negative_coefficients(self):
        """Отрицательные коэффициенты"""
        result, error = solve_quadratic(-1, 5, -6)
        self.assertIsNone(error)
        self.assertEqual(result["type"], "two_roots")

    def test_discriminant_value(self):
        """Проверка корректного значения дискриминанта"""
        result, error = solve_quadratic(1, -5, 6)
        self.assertEqual(result["discriminant"], 1.0)

    def test_large_coefficients(self):
        """Большие коэффициенты"""
        result, error = solve_quadratic(2, -8, 6)
        self.assertIsNone(error)
        self.assertEqual(result["type"], "two_roots")
        self.assertEqual(result["x1"], 3.0)
        self.assertEqual(result["x2"], 1.0)


class TestFlaskRoutes(unittest.TestCase):
    """Тесты для маршрутов Flask-приложения"""

    def setUp(self):
        """Настройка тестового клиента перед каждым тестом"""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_request_returns_200(self):
        """GET-запрос возвращает статус 200"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_get_request_contains_form(self):
        """GET-запрос возвращает страницу с формой"""
        response = self.client.get("/")
        self.assertIn("Квадратное уравнение".encode("utf-8"), response.data)

    def test_post_two_roots(self):
        """POST с D > 0: страница содержит два корня"""
        response = self.client.post("/", data={"a": "1", "b": "-5", "c": "6"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("3.0".encode("utf-8"), response.data)
        self.assertIn("2.0".encode("utf-8"), response.data)

    def test_post_one_root(self):
        """POST с D = 0: страница содержит один корень"""
        response = self.client.post("/", data={"a": "1", "b": "-2", "c": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("1.0".encode("utf-8"), response.data)

    def test_post_complex_roots(self):
        """POST с D < 0: страница содержит комплексные корни"""
        response = self.client.post("/", data={"a": "1", "b": "0", "c": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("i".encode("utf-8"), response.data)

    def test_post_invalid_input(self):
        """POST с нечисловым вводом: страница содержит ошибку"""
        response = self.client.post("/", data={"a": "abc", "b": "1", "c": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Пожалуйста".encode("utf-8"), response.data)

    def test_post_a_zero(self):
        """POST с a = 0: страница содержит ошибку"""
        response = self.client.post("/", data={"a": "0", "b": "5", "c": "3"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Коэффициент a".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
