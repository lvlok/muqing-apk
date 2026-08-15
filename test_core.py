# -*- coding: utf-8 -*-
import os, sys, json, tempfile, shutil, unittest
from datetime import datetime, timedelta
sys.path.insert(0, "/data/workspace/muqing_full")
import core

def fresh(tmp):
    core.DATA_DIR = tmp
    core.LEARN_FILE = os.path.join(tmp, "learn_library.json")
    core.MEMORY_FILE = os.path.join(tmp, "memory.json")
    core.SETTINGS_FILE = os.path.join(tmp, "settings.json")

class TestCore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        fresh(self.tmp)
    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ai_name_default(self):
        b = core.AIBrain()
        self.assertEqual(b.settings.get("ai_name"), "沐晴")

    def test_below_threshold(self):
        b = core.AIBrain()
        # 用短单字输入，避免一次贡献多个词导致提前跨过阈值
        msgs = [b.reply("a") for _ in range(25)]
        # 前 25 条应全部为「嗯」（学习库远未到 30）
        self.assertTrue(all(m == "嗯" for m in msgs))

    def test_above_threshold_generates(self):
        b = core.AIBrain()
        # 先喂 35 条让学习库稳定 ≥30，再验证后续回复进入组句
        for i in range(35):
            b.reply("测试消息%d 喜欢你 永远"%i)
        later = [b.reply("再多说一点 永远 喜欢") for _ in range(5)]
        self.assertTrue(all(m != "嗯" for m in later))

    def test_memory_50day_expiry(self):
        b = core.AIBrain()
        old = (datetime.now() - timedelta(days=60)).isoformat()
        b.memory.memories.append({"text":"old","tag":"user","importance":1,"time":old})
        b.memory.memories.append({"text":"new","tag":"user","importance":1,
                                  "time":datetime.now().isoformat()})
        b.memory._clean_expired()
        texts = [m["text"] for m in b.memory.memories]
        self.assertNotIn("old", texts)
        self.assertIn("new", texts)

    def test_persona_learner_90day_window(self):
        b = core.AIBrain()
        old = (datetime.now() - timedelta(days=100)).isoformat()
        new = datetime.now().isoformat()
        b.memory.memories = [
            {"text":"a","tag":"user","importance":2,"time":old},
            {"text":"b","tag":"user","importance":2,"time":new},
        ]
        wm = b.learner._weighted_memories()
        self.assertEqual(wm[0][1], 0.2)   # >90 天权重 0.2
        self.assertEqual(wm[1][1], 1.0)   # ≤90 天权重 1.0

    def test_memory_cap_500(self):
        b = core.AIBrain()
        now = datetime.now()
        # 明确：i 越大越新（i=0 最老，i=519 最新）
        for i in range(520):
            b.memory.memories.append({
                "text":"m%d"%i,"tag":"user","importance":1,
                "time":(now - timedelta(minutes=519-i)).isoformat()
            })
        b.memory._enforce_limit()
        self.assertEqual(len(b.memory.memories), 500)
        texts = [m["text"] for m in b.memory.memories]
        # 最老的 20 条(m0..m19)应被淘汰
        for i in range(20):
            self.assertNotIn("m%d"%i, texts)
        # 最新的 m519 应保留
        self.assertIn("m519", texts)

    def test_base_persona_capped(self):
        b = core.AIBrain()
        lvl = b.persona._dynamic_level()
        self.assertLessEqual(lvl, 0.72)
        self.assertGreaterEqual(lvl, 0.60)

if __name__ == "__main__":
    unittest.main(verbosity=2)
