import unittest

from app.services.script_generator import ScriptRequest, _starter_script


class StarterScriptTests(unittest.TestCase):
    def test_scene_timing_matches_selected_runtime(self):
        for duration in (10, 15, 20, 30, 45, 60):
            with self.subTest(duration=duration):
                request = ScriptRequest(
                    brief="Promote a refreshing drink after a football match.",
                    product_name="Maji Fresh",
                    language="Sheng",
                    duration_seconds=duration,
                )
                script = _starter_script(request)
                self.assertEqual(script.duration_seconds, duration)
                self.assertEqual(sum(scene.duration_seconds for scene in script.scenes), duration)
                self.assertEqual(
                    [scene.scene_number for scene in script.scenes],
                    list(range(1, len(script.scenes) + 1)),
                )

    def test_all_supported_languages_generate_valid_scene_json(self):
        for language in ("English", "Kiswahili", "Sheng"):
            with self.subTest(language=language):
                request = ScriptRequest(
                    brief="Advertise a neighbourhood salon for young professionals.",
                    product_name="Glow Studio",
                    language=language,
                    duration_seconds=15,
                )
                script = _starter_script(request)
                self.assertEqual(script.language, language)
                self.assertGreaterEqual(len(script.scenes), 3)
                self.assertTrue(script.call_to_action)


if __name__ == "__main__":
    unittest.main()
