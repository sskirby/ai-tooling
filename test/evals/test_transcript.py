import json
import tempfile
import unittest
from pathlib import Path

from evals.transcript import Message, SkillLoad, build_records, skill_message_text, write_jsonl

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "natural-skill-load.json").read_text())
SKILL = SkillLoad("demo:teach", "X")
MESSAGES = [
    Message("user", "what is X?"),
    Message("assistant", "X is a thing — used with `WITH` “here” 🙂", SKILL),
    Message("user", "I use it daily."),
    Message("assistant", "Step 1 of 2 — X does Y."),
]
SKILL_MD = "---\nname: teach\ndescription: d\n---\n\n# Teach\n\nBe brief.\n"


def build(with_skill, seed="lesson-replay"):
    return build_records(seed, MESSAGES, cwd="/work/case", skill_md=SKILL_MD,
                         skill_dir="/work/skills/teach", with_skill=with_skill)


def chain(records):
    return [r for r in records if r["type"] != "last-prompt"]


class SkillMessageText(unittest.TestCase):
    def test_matches_real_session_byte_for_byte(self):
        self.assertEqual(
            skill_message_text(FIXTURE["skill_md"], FIXTURE["skill_dir"], FIXTURE["args"]),
            FIXTURE["expected"])

    def test_crlf_skill_md_gives_same_text(self):
        crlf = FIXTURE["skill_md"].replace("\n", "\r\n")
        self.assertEqual(skill_message_text(crlf, "/d", "a"),
                         skill_message_text(FIXTURE["skill_md"], "/d", "a"))

    def test_no_frontmatter_keeps_whole_text(self):
        text = skill_message_text("# Body\n", "/d", "a")
        self.assertEqual(text, "Base directory for this skill: /d\n# Body\n\n\nARGUMENTS: a")


class WithSkill(unittest.TestCase):
    def setUp(self):
        self.records = build(with_skill=True)

    def test_record_order(self):
        self.assertEqual([r["type"] for r in self.records],
                         ["user", "assistant", "user", "user", "assistant", "user", "assistant", "last-prompt"])

    def test_skill_call_tool_result_and_injection_link_up(self):
        call, result, injected = self.records[1], self.records[2], self.records[3]
        tool_use = call["message"]["content"][0]
        self.assertEqual(tool_use["name"], "Skill")
        self.assertEqual(tool_use["input"], {"skill": "demo:teach", "args": "X"})
        self.assertEqual(result["message"]["content"][0]["tool_use_id"], tool_use["id"])
        self.assertEqual(result["sourceToolAssistantUUID"], call["uuid"])
        self.assertEqual(result["toolUseResult"], {"success": True, "commandName": "demo:teach"})
        self.assertTrue(injected["isMeta"])
        self.assertTrue(injected["turnCompanion"])
        self.assertEqual(injected["sourceToolUseID"], tool_use["id"])
        self.assertEqual(injected["message"]["content"][0]["text"],
                         skill_message_text(SKILL_MD, "/work/skills/teach", "X"))

    def test_reply_after_load_is_attributed(self):
        reply = self.records[4]
        self.assertEqual(reply["attributionSkill"], "demo:teach")
        self.assertEqual(reply["attributionPlugin"], "demo")
        self.assertEqual(reply["message"]["content"], [{"type": "text", "text": MESSAGES[1].content}])

    def test_one_parent_chain_and_leaf_pointer(self):
        spine = chain(self.records)
        self.assertIsNone(spine[0]["parentUuid"])
        for prev, cur in zip(spine, spine[1:]):
            self.assertEqual(cur["parentUuid"], prev["uuid"])
        last = self.records[-1]
        self.assertEqual(last["leafUuid"], spine[-1]["uuid"])
        self.assertEqual(last["lastPrompt"], "I use it daily.")
        self.assertEqual({r["sessionId"] for r in self.records}, {last["sessionId"]})

    def test_no_thinking_blocks(self):
        blocks = [b for r in self.records if isinstance(r.get("message", {}).get("content"), list)
                  for b in r["message"]["content"]]
        self.assertNotIn("thinking", {b["type"] for b in blocks})


class Baseline(unittest.TestCase):
    def test_same_turns_without_the_skill_load(self):
        base = build(with_skill=False, seed="lesson-replay-baseline")
        self.assertEqual([r["type"] for r in base], ["user", "assistant", "user", "assistant", "last-prompt"])
        texts = [r["message"]["content"] if r["type"] == "user" else r["message"]["content"][0]["text"]
                 for r in chain(base)]
        self.assertEqual(texts, [m.content for m in MESSAGES])
        self.assertFalse(any(r.get("isMeta") or "attributionSkill" in r for r in base))


class Determinism(unittest.TestCase):
    def test_same_input_same_records(self):
        self.assertEqual(build(True), build(True))

    def test_seed_changes_session(self):
        self.assertNotEqual(build(True)[0]["sessionId"], build(True, seed="other")[0]["sessionId"])

    def test_unicode_round_trips_through_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.jsonl"
            write_jsonl(path, build(True))
            back = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(back[4]["message"]["content"][0]["text"], MESSAGES[1].content)


if __name__ == "__main__":
    unittest.main()
