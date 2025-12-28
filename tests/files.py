import unittest
import tempfile
import shutil
from pathlib import Path
from mc_chunk_analyzer.infrastructure.fs.services import PathInfo, WorldTree  # замени your_module на фактический модуль

class TestPathInfo(unittest.TestCase):

    def setUp(self):
        # Создаём временную директорию
        self.temp_dir = Path(tempfile.mkdtemp())

        # Создаём папку saves и несколько миров
        saves_dir = self.temp_dir / "saves"
        saves_dir.mkdir()
        (saves_dir / "World1").mkdir()
        (saves_dir / "World2").mkdir()

        # Создаём папку bobby с подмирами
        bobby_dir = self.temp_dir / "bobby"
        bobby_dir.mkdir()
        (bobby_dir / "BobbyWorld1").mkdir()
        (bobby_dir / "BobbyWorld1" / "SubworldA").mkdir()
        (bobby_dir / "BobbyWorld1" / "SubworldB").mkdir()
        (bobby_dir / "BobbyWorld2").mkdir()
        (bobby_dir / "BobbyWorld2" / "SubworldX").mkdir()

    def tearDown(self):
        # Удаляем временную директорию после теста
        shutil.rmtree(self.temp_dir)

    def test_pathinfo_data(self):
        pi = PathInfo(self.temp_dir)
        data: WorldTree = pi.get_data

        # Проверяем обычные миры
        self.assertEqual(set(data.worlds.keys()), {"World1", "World2"})
        for path in data.worlds.values():
            self.assertTrue(path.is_dir())

        # Проверяем bobby-миры
        self.assertEqual(set(data.bobby_words.keys()), {"BobbyWorld1", "BobbyWorld2"})
        self.assertEqual(set(data.bobby_words["BobbyWorld1"]), {"SubworldA", "SubworldB"})
        self.assertEqual(set(data.bobby_words["BobbyWorld2"]), {"SubworldX"})

if __name__ == "__main__":
    unittest.main()
