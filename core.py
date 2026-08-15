# -*- coding: utf-8 -*-
import json, os, random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
LEARN_FILE = os.path.join(DATA_DIR, "learn_library.json")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

COMMON_WORDS = set([
    "今天","明天","昨天","开心","难过","喜欢","讨厌","你好","谢谢",
    "没关系","可爱","漂亮","帅气","生气","快乐","伤心","爱你",
    "摆烂","躺平","破防","社死","绝绝子","yyds","emo","真的",
    "非常","特别","有点","太","很","超级","极其","挺","好",
    "我","你","他","她","它","我们","你们","他们","这","那",
    "什么","怎么","为什么","吗","呢","吧","啊","哦","嗯"
])

DEFAULT_SETTINGS = {
    "ai_name": "沐晴",
    "persona_level": 0.6,
    "learn_threshold": 30,
    "cycle_hours": 24,
    "theme_color": "#ff6699",
    "avatar_path": "",
    "bg_path": "",
    "memory_max_days": 50,
    "memory_max_count": 500,
    "persona_learn_days": 90,
}

def _load(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default.copy() if isinstance(default, dict) else default

def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class LearnLibrary:
    def __init__(self):
        self.data = _load(LEARN_FILE, {})
    def size(self):
        return len(self.data)
    def add(self, text):
        for p in self._split(text):
            self._add_one(p, text)
    def _split(self, text):
        parts = set()
        for ch in text:
            if ch.strip(): parts.add(ch)
        for i in range(len(text)-1):
            bi = text[i:i+2]
            if bi.strip(): parts.add(bi)
        for w in COMMON_WORDS:
            if w in text: parts.add(w)
        return parts
    def _add_one(self, word, context):
        if not word or len(word) > 20: return
        if word in self.data:
            e = self.data[word]
            e.setdefault("meanings", [e.get("meaning","")])
            if context not in e["meanings"]:
                e["meanings"].append(context)
            e["count"] = e.get("count",1)+1
            e["last_seen"] = datetime.now().isoformat()
        else:
            self.data[word] = {
                "meaning": context, "meanings": [context],
                "count": 1, "contexts": [context],
                "created": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
            }
    def get_words(self): return list(self.data.keys())
    def get_entry(self, word): return self.data.get(word)
    def clear(self): self.data = {}
    def save(self): _save(LEARN_FILE, self.data)


class MemorySystem:
    def __init__(self):
        self.memories = _load(MEMORY_FILE, [])
        self.settings = _load(SETTINGS_FILE, DEFAULT_SETTINGS)
        self._clean_expired()
    def _clean_expired(self):
        max_days = self.settings.get("memory_max_days", 50)
        cutoff = datetime.now() - timedelta(days=max_days)
        before = len(self.memories)
        self.memories = [m for m in self.memories
                         if datetime.fromisoformat(m["time"]) > cutoff]
        if len(self.memories) < before: self.save()
    def _enforce_limit(self):
        max_count = self.settings.get("memory_max_count", 500)
        if len(self.memories) > max_count:
            self.memories.sort(key=lambda m:m["time"], reverse=True)
            self.memories = self.memories[:max_count]
            self.memories.sort(key=lambda m:m["time"])
    def add(self, text, tag="", importance=1):
        self._clean_expired()
        self.memories.append({"text":text,"tag":tag,
                             "importance":importance,
                             "time":datetime.now().isoformat()})
        self._enforce_limit(); self.save()
    def recall(self, keyword=""):
        self._clean_expired()
        if not keyword:
            recent = sorted(self.memories, key=lambda m:m["time"], reverse=True)[:10]
            recent.sort(key=lambda m:(m.get("importance",1),m["time"]), reverse=True)
            return recent
        matched = [m for m in self.memories if keyword in m["text"]]
        matched.sort(key=lambda m:(m.get("importance",1),m["time"]), reverse=True)
        return matched
    def get_important_memories(self, limit=5):
        self._clean_expired()
        imp = [m for m in self.memories if m.get("importance",1)>=2]
        imp.sort(key=lambda m:(m["importance"],m["time"]), reverse=True)
        return imp[:limit]
    def get_recent_texts(self, limit=5):
        self._clean_expired()
        recent = sorted(self.memories, key=lambda m:m["time"], reverse=True)[:limit]
        return [m["text"] for m in reversed(recent)]
    def clear(self): self.memories = []
    def save(self): _save(MEMORY_FILE, self.memories)


class PersonaLearner:
    def __init__(self, memory_system, settings):
        self.memory = memory_system; self.settings = settings
    def _weighted_memories(self):
        max_days = self.settings.get("persona_learn_days", 90)
        now = datetime.now(); weighted=[]
        for m in self.memory.memories:
            age = (now-datetime.fromisoformat(m["time"])).days
            weighted.append((m, 1.0 if age<=max_days else 0.2))
        return weighted
    def emotional_closeness(self):
        wm = self._weighted_memories()
        if not wm: return 0.3
        base = 0.3
        wc = sum(w for _,w in wm)
        base += min(wc/10*0.05, 0.35)
        imp = sum(1 for m,w in wm if m.get("importance",1)>=2)
        base += min(imp*0.02, 0.15)
        wa = datetime.now()-timedelta(days=7)
        recent = sum(1 for m,w in wm if datetime.fromisoformat(m["time"])>wa)
        base += min(recent*0.01, 0.08)
        return min(base, 0.95)
    def personality_boost(self):
        c = self.emotional_closeness()
        return max(0.0, min((c-0.3)/(0.95-0.3)*0.12, 0.12))


class Persona:
    def __init__(self, level=0.6, learner=None):
        self.base_level=level; self.learner=learner
    def _dynamic_level(self):
        lvl=self.base_level
        if self.learner: lvl+=self.learner.personality_boost()
        return min(lvl, 0.72)
    def weights(self):
        l=self._dynamic_level()
        return {"cute":0.3+l*0.4,"clingy":0.2+l*0.5,
                "tsundere":0.1+l*0.3,"emotional":0.2+l*0.4,
                "long":0.3,"punct":0.4}
    def style_prefix(self):
        l=self._dynamic_level()
        if random.random()<l*0.5:
            return random.choice(["哼，","才、才不是…","你…","笨蛋，","唔…",""])
        return ""
    def style_suffix(self):
        l=self._dynamic_level()
        if random.random()<l*0.6:
            return random.choice(["呢~","哦！","啦~","！","…",""])
        return ""


class AIBrain:
    def __init__(self):
        self.learn_lib=LearnLibrary()
        self.memory=MemorySystem()
        self.settings=_load(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.learner=PersonaLearner(self.memory, self.settings)
        self.persona=Persona(self.settings.get("persona_level",0.6), self.learner)
        self._last_cycle=datetime.now()
    def reply(self, user_input):
        imp=self._judge_importance(user_input)
        self.learn_lib.add(user_input)
        self.memory.add(user_input,"user",imp)
        self.learn_lib.save(); self.memory.save()
        if self.learn_lib.size()<self.settings.get("learn_threshold",30):
            return "嗯"
        return self._generate_reply(user_input)
    def _judge_importance(self, text):
        for w in ["永远","一辈子","最爱","只对你","绝不","发誓"]:
            if w in text: return 3
        for w in ["喜欢","爱","恨","讨厌","生气","伤心","开心","难过"]:
            if w in text: return 2
        return 1
    def _generate_reply(self, user_input):
        words=self.learn_lib.get_words()
        if not words: return "嗯"
        uc=set(user_input)
        overlap=[w for w in words if any(c in uc for c in w) and len(w)>1]
        if not overlap: overlap=words
        w=self.persona.weights()
        ps=min(len(overlap),6)
        chosen=random.sample(overlap,ps) if len(overlap)>=ps else overlap[:]
        imp=self.memory.get_important_memories(3); ms=""
        if imp and random.random()<0.35:
            p=random.choice(imp); ms=p["text"][:6]+("…" if len(p["text"])>6 else "")
        rt=self.memory.get_recent_texts(3); rw=""
        if rt and random.random()<0.25:
            for t in rt:
                r=[ww for ww in self.learn_lib.get_words() if ww in t]
                if r: rw=random.choice(r); break
        pre=self.persona.style_prefix(); suf=self.persona.style_suffix()
        mid="".join(chosen[:5] if random.random()<w["long"] else chosen[:3])
        if ms: mid=ms+mid
        if rw: mid=mid+rw
        result=("{}{}{}".format(pre,mid,suf)).strip() or "嗯"
        rip=1
        if any(x in result for x in ["永远","爱你","笨蛋","才不是"]): rip=2
        self.memory.add(result,"ai",rip)
        self.learn_lib.save(); self.memory.save()
        return result
    def 主动_message(self):
        words=self.learn_lib.get_words()
        if len(words)<self.settings.get("learn_threshold",30): return None
        w=self.persona.weights()
        sample=random.sample(words, min(len(words),5))
        pre=self.persona.style_prefix(); suf=self.persona.style_suffix()
        mid="".join(sample[:4])
        imp=self.memory.get_important_memories(2)
        if imp and random.random()<0.4:
            mid=imp[0]["text"][:5]+"…"+mid
        msg=("{}{}{}".format(pre,mid,suf)).strip()
        if msg:
            self.memory.add(msg,"ai_auto",1); self.memory.save()
        return msg if msg else None
    def get_settings(self): return self.settings
    def update_settings(self, key, value):
        self.settings[key]=value
        _save(SETTINGS_FILE, self.settings)
        if key=="persona_level":
            self.persona=Persona(value,self.learner)
        if key in ("memory_max_days","memory_max_count","persona_learn_days"):
            self.memory.settings=self.settings; self.learner.settings=self.settings
    def clear_learn(self): self.learn_lib.clear(); self.learn_lib.save()
    def clear_memory(self): self.memory.clear(); self.memory.save()
    def get_learn_data(self): return self.learn_lib.data
    def get_learn_size(self): return self.learn_lib.size()
