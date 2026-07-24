"""分析器 — 优先级计算测试"""

from tuoman.pipeline.analyzer import Analyzer


def test_calc_priority_hot():
    assert Analyzer._calc_priority("HIGH", {"budget": 3, "authority": 2, "need": 3, "timeline": 2}, 80) == "HOT"
    # bant_total=6+, icp>=60 → HOT
    assert Analyzer._calc_priority("HIGH", {"budget": 2, "authority": 1, "need": 1, "timeline": 1}, 60) == "WARM"


def test_calc_priority_warm():
    # HIGH + bant=4(边界) + icp>=40 → WARM
    assert Analyzer._calc_priority("HIGH", {"budget": 1, "authority": 1, "need": 1, "timeline": 1}, 40) == "WARM"
    # MEDIUM + bant=4 → WARM (不考虑icp)
    assert Analyzer._calc_priority("MEDIUM", {"budget": 2, "authority": 1, "need": 1, "timeline": 0}, 20) == "WARM"
    assert Analyzer._calc_priority("MEDIUM", {"budget": 2, "authority": 1, "need": 1, "timeline": 1}, 50) == "WARM"


def test_calc_priority_cold():
    assert Analyzer._calc_priority("LOW", {"budget": 1, "authority": 1, "need": 1, "timeline": 1}, 30) == "COLD"
    assert Analyzer._calc_priority("LOW", {"budget": 0, "authority": 0, "need": 0, "timeline": 0}, 0) == "COLD"
