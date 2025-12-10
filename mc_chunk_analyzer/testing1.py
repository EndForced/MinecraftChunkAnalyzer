import time
import timeit
import statistics
from pathlib import Path
import cProfile
import pstats
from typing import Dict, List, Any
import sys
from domain.services.ChunkAnalyzer import McaParser
from mc_chunk_analyzer.domain.models.Chunk import TwoDimCord
from mc_chunk_analyzer.domain.models.Region import RawRegion

parser = McaParser()

class NBTBenchmark:
    def __init__(self, test_file_path: str):
        self.test_file_path = Path(test_file_path)
        self.test_data = self._load_test_data()

    def _load_test_data(self) -> bytes:
        """Загружаем тестовые данные"""
        with open(self.test_file_path, "rb") as f:
            return f.read()

    def benchmark_nbtlib(self):
        """Бенчмарк для nbtlib"""
        try:
            import nbtlib
        except ImportError:
            print("nbtlib не установлен. Установите: pip install nbtlib")
            return None

        def parse_with_nbtlib():
            # nbtlib работает с файлами, нужно сохранить данные во временный файл
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix='.nbt', delete=False) as tmp:
                tmp.write(self.test_data)
                tmp.flush()

                try:
                    # Парсим файл
                    nbt_file = nbtlib.load(tmp.name)
                    return nbt_file
                finally:
                    os.unlink(tmp.name)

        return self._run_benchmark("nbtlib", parse_with_nbtlib)

    def benchmark_your_parser(self):
        """Бенчмарк для вашего парсера"""
        # Импортируем ваш парсер
        from mc_chunk_analyzer.domain.services.ChunkAnalyzer import NBTTagReader

        def parse_with_your_parser():
            region = parser.parse(RawRegion(self.test_data, TwoDimCord((0,0)),"Nether"))
            reader = None
            for i in region.raw_chunks.keys():
                reader = NBTTagReader(region.raw_chunks[i])
            return reader.read()

        return self._run_benchmark("Ваш парсер", parse_with_your_parser)

    def benchmark_py_nbt(self):
        """Бенчмарк для PyNBT (еще одна популярная библиотека)"""
        try:
            import nbt  # pip install PyNBT
        except ImportError:
            print("PyNBT не установлен. Установите: pip install PyNBT")
            return None

        def parse_with_pynbt():
            import io
            # PyNBT работает с файлоподобными объектами
            return nbt.NBTFile(fileobj=io.BytesIO(self.test_data))

        return self._run_benchmark("PyNBT", parse_with_pynbt)

    def benchmark_fast_nbt(self):
        """Бенчмарк для fast-nbt (если есть)"""
        try:
            import fastnbt
        except ImportError:
            try:
                from fastnbt import nbt
            except ImportError:
                print("fast-nbt не установлен. Установите: pip install fast-nbt")
                return None

        def parse_with_fastnbt():
            return fastnbt.read_nbt(self.test_data)

        return self._run_benchmark("fast-nbt", parse_with_fastnbt)

    def _run_benchmark(self, name: str, parse_func, warmup_runs: int = 3, bench_runs: int = 10):
        """Запускает бенчмарк для парсера"""
        print(f"\n{'=' * 60}")
        print(f"БЕНЧМАРК: {name}")
        print('=' * 60)

        # 1. Разогрев (warmup)
        print("Разогрев...", end=" ")
        sys.stdout.flush()

        for i in range(warmup_runs):
            result = parse_func()
        print("✓")

        # 2. Замер времени
        print(f"Запуск {bench_runs} итераций...")
        times = []

        for i in range(bench_runs):
            start = time.perf_counter()
            result = parse_func()
            end = time.perf_counter()
            times.append(end - start)

            if i < 5 or i % 5 == 0:  # Выводим прогресс
                print(f"  Итерация {i + 1}: {times[-1]:.6f} сек")

        # 3. Статистика
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0

        print(f"\nРезультаты {name}:")
        print(f"  Среднее:   {avg_time:.6f} сек")
        print(f"  Минимум:   {min_time:.6f} сек")
        print(f"  Максимум:  {max_time:.6f} сек")
        print(f"  Станд. откл: {std_dev:.6f} сек")
        print(f"  Скорость:  {1 / avg_time:.1f} парсов/сек")

        # 4. Профилирование (только для первой итерации)
        if name == "Ваш парсер" or name == "nbtlib":
            print("\nПрофилирование...")
            self._profile_parser(name, parse_func)

        return {
            'name': name,
            'avg_time': avg_time,
            'min_time': min_time,
            'max_time': max_time,
            'std_dev': std_dev,
            'result': result
        }

    def _profile_parser(self, name: str, parse_func):
        """Профилирует парсер с помощью cProfile"""
        import cProfile
        import pstats
        from pstats import SortKey

        profiler = cProfile.Profile()
        profiler.enable()

        # Запускаем несколько раз для статистики
        for _ in range(5):
            parse_func()

        profiler.disable()

        # Сохраняем результаты
        stats = pstats.Stats(profiler)
        stats.strip_dirs()

        # Сохраняем в файл
        profile_file = f"profile_{name.lower().replace(' ', '_')}.prof"
        stats.dump_stats(profile_file)

        # Анализ топ-10 функций
        print(f"  Профиль сохранен в: {profile_file}")
        print(f"  Топ-10 функций по времени:")

        stats.sort_stats(SortKey.TIME)
        stats.print_stats(10)

    def compare_all(self):
        """Сравнивает все доступные парсеры"""
        print("\n" + "=" * 80)
        print("СРАВНИТЕЛЬНЫЙ БЕНЧМАРК NBT ПАРСЕРОВ")
        print("=" * 80)
        print(f"Тестовый файл: {self.test_file_path}")
        print(f"Размер данных: {len(self.test_data):,} байт")
        print("=" * 80)

        results = []

        # Ваш парсер
        your_result = self.benchmark_your_parser()
        if your_result:
            results.append(your_result)

        # nbtlib
        nbtlib_result = self.benchmark_nbtlib()
        if nbtlib_result:
            results.append(nbtlib_result)

        # PyNBT
        pynbt_result = self.benchmark_py_nbt()
        if pynbt_result:
            results.append(pynbt_result)

        # fast-nbt
        fastnbt_result = self.benchmark_fast_nbt()
        if fastnbt_result:
            results.append(fastnbt_result)

        # Вывод сравнения
        if len(results) > 1:
            self._print_comparison_table(results)

    def _print_comparison_table(self, results: List[Dict]):
        """Выводит таблицу сравнения"""
        print("\n" + "=" * 80)
        print("ИТОГОВОЕ СРАВНЕНИЕ")
        print("=" * 80)

        # Сортируем по скорости
        results.sort(key=lambda x: x['avg_time'])

        fastest = results[0]['avg_time']

        print(f"{'Парсер':<20} {'Среднее время':<15} {'Отн. скорость':<15} {'Скорость/сек':<15}")
        print("-" * 65)

        for r in results:
            rel_speed = fastest / r['avg_time']
            speed_per_sec = 1 / r['avg_time']

            print(f"{r['name']:<20} {r['avg_time']:.6f} сек  {rel_speed:>6.2f}x         {speed_per_sec:>7.1f}")

        print("=" * 80)

        # Рекомендации
        winner = results[0]['name']
        print(f"\n🏆 Победитель: {winner}")

        if winner == "Ваш парсер":
            print("🎉 Ваш парсер быстрее всех! Отличная работа!")
        else:
            print(f"💡 Совет: Изучите как устроен {winner} для дальнейшей оптимизации")


# ------------------------------------------------------------
# БЕНЧМАРК С РАЗНЫМИ ТИПАМИ ДАННЫХ
# ------------------------------------------------------------

class ComprehensiveNBTBenchmark:
    """Бенчмарк с разными типами NBT данных"""

    @staticmethod
    def create_test_data() -> Dict[str, bytes]:
        """Создает тестовые NBT данные разных типов"""
        import struct

        test_cases = {}

        # 1. Простой compound
        simple_data = bytearray()
        # { "test": 12345i }
        simple_data.extend(b'\x0A\x00\x00'  # Compound, пустое имя
                           b'\x03\x00\x04test'  # Int tag, имя "test"
                           b'\x00\x00\x30\x39'  # 12345
                           b'\x00')  # TAG_End
        test_cases['simple'] = bytes(simple_data)

        # 2. Список интов
        list_data = bytearray()
        # { "numbers": [1000i, 2000i, 3000i] }
        list_data.extend(b'\x0A\x00\x00'  # Compound
                         b'\x09\x00\x07numbers'  # List tag, имя "numbers"
                         b'\x03\x00\x00\x00\x03'  # Тип int, размер 3
                         b'\x00\x00\x03\xE8'  # 1000
                         b'\x00\x00\x07\xD0'  # 2000
                         b'\x00\x00\x0B\xB8'  # 3000
                         b'\x00')  # TAG_End
        test_cases['list_int'] = bytes(list_data)

        # 3. Вложенный compound
        nested_data = bytearray()
        # { "outer": { "inner": 42i } }
        nested_data.extend(b'\x0A\x00\x00'  # Compound
                           b'\x0A\x00\x05outer'  # Compound tag, имя "outer"
                           b'\x03\x00\x05inner'  # Int tag, имя "inner"
                           b'\x00\x00\x00\x2A'  # 42
                           b'\x00'  # TAG_End внутреннего compound
                           b'\x00')  # TAG_End внешнего
        test_cases['nested'] = bytes(nested_data)

        # 4. Большой массив интов (1000 элементов)
        large_array = bytearray()
        large_array.extend(b'\x0A\x00\x00'  # Compound
                           b'\x0B\x00\x0Blarge_array'  # Int Array tag
                           b'\x00\x00\x03\xE8')  # 1000 элементов

        # Добавляем 1000 интов
        for i in range(1000):
            large_array.extend(struct.pack('>i', i))

        large_array.extend(b'\x00')  # TAG_End
        test_cases['large_array'] = bytes(large_array)

        return test_cases

    @staticmethod
    def run_microbenchmarks(your_reader_class):
        """Микробенчмарки для отдельных операций"""
        print("\n" + "=" * 80)
        print("МИКРОБЕНЧМАРКИ ОТДЕЛЬНЫХ ОПЕРАЦИЙ")
        print("=" * 80)

        test_cases = ComprehensiveNBTBenchmark.create_test_data()

        for name, data in test_cases.items():
            print(f"\nТест: {name} ({len(data)} байт)")
            print("-" * 40)

            # Ваш парсер
            start = time.perf_counter()
            for _ in range(100):
                reader = your_reader_class(data)
                result = reader.read()
            your_time = time.perf_counter() - start

            # nbtlib (если есть)
            try:
                import nbtlib
                import tempfile
                import os

                start = time.perf_counter()
                for _ in range(100):
                    with tempfile.NamedTemporaryFile(suffix='.nbt', delete=False) as tmp:
                        tmp.write(data)
                        tmp.flush()
                        nbt_file = nbtlib.load(tmp.name)
                        os.unlink(tmp.name)
                nbtlib_time = time.perf_counter() - start

                print(f"  Ваш парсер: {your_time / 100:.6f} сек/оп (относительно: 1.00x)")
                print(f"  nbtlib:     {nbtlib_time / 100:.6f} сек/оп (относительно: {your_time / nbtlib_time:.2f}x)")
            except ImportError:
                print(f"  Ваш парсер: {your_time / 100:.6f} сек/оп")

        return test_cases


# ------------------------------------------------------------
# ИСПОЛЬЗОВАНИЕ
# ------------------------------------------------------------

if __name__ == "__main__":
    # Путь к вашему тестовому файлу .mca или .nbt
    TEST_FILE = r'C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft\overworld\3\r.0.0.mca'

    # Проверяем существует ли файл
    if not Path(TEST_FILE).exists():
        print(f"Файл {TEST_FILE} не найден!")
        print("Создаю тестовые данные...")

        # Создаем тестовые данные
        test_cases = ComprehensiveNBTBenchmark.create_test_data()

        # Сохраняем самый большой тест
        TEST_FILE = "test_large.nbt"
        with open(TEST_FILE, "wb") as f:
            f.write(test_cases['large_array'])

        print(f"Создан тестовый файл: {TEST_FILE}")

    # Запускаем основной бенчмарк
    benchmark = NBTBenchmark(TEST_FILE)
    benchmark.compare_all()

    # Запускаем микробенчмарки
    print("\n" + "=" * 80)
    print("ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ")
    print("=" * 80)

    # Микробенчмарки для вашего парсера
    from mc_chunk_analyzer.domain.services.ChunkAnalyzer import NBTTagReader

    test_cases = ComprehensiveNBTBenchmark.run_microbenchmarks(NBTTagReader)

    # Сравнение памяти
    print("\n" + "=" * 80)
    print("СРАВНЕНИЕ ИСПОЛЬЗОВАНИЯ ПАМЯТИ")
    print("=" * 80)

    import tracemalloc

    for name, data in test_cases.items():
        print(f"\nТест: {name}")

        # Ваш парсер
        tracemalloc.start()
        reader = NBTTagReader(data)
        result = reader.read()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"  Ваш парсер: {current / 1024:.2f} KB текущая, {peak / 1024:.2f} KB пиковая")

        # nbtlib (если есть)
        try:
            import nbtlib
            import tempfile
            import os

            tracemalloc.start()
            with tempfile.NamedTemporaryFile(suffix='.nbt', delete=False) as tmp:
                tmp.write(data)
                tmp.flush()
                nbt_file = nbtlib.load(tmp.name)
                os.unlink(tmp.name)
            current2, peak2 = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            print(f"  nbtlib:     {current2 / 1024:.2f} KB текущая, {peak2 / 1024:.2f} KB пиковая")
            print(f"  Отношение:  {current / current2:.2f}x по памяти")
        except ImportError:
            pass