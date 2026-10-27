import math

from reel import parse_time, x_expr


def evaluate(expr, t):
    return eval(expr.replace("if(", "_if(").replace("lt(", "_lt("), {"_if": lambda c, a, b: a if c else b, "_lt": lambda a, b: a < b, "t": t})


def test_parse_time():
    assert parse_time("12.5") == 12.5
    assert parse_time("1:05") == 65
    assert parse_time("1:00:02") == 3602


def test_x_expr_interpolates_and_clamps():
    expr = x_expr([(0, 0.0), (1, 0.5), (2, 1.0)], src_w=3840, crop_w=1215)
    assert evaluate(expr, 0) == 0
    assert math.isclose(evaluate(expr, 1), 3840 / 2 - 1215 / 2, abs_tol=1)
    assert math.isclose(evaluate(expr, 0.5), (3840 / 2 - 1215 / 2) / 2, abs_tol=1)
    assert evaluate(expr, 3) == 3840 - 1215


if __name__ == "__main__":
    test_parse_time()
    test_x_expr_interpolates_and_clamps()
    print("ok")
