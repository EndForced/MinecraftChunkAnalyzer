from mc_chunk_analyzer.domain.services.ChunkAnalyzer import McaParser, NBTTagReader
from mc_chunk_analyzer.domain.models.Region import RawRegion, TwoDimCord
from pathlib import Path
import cProfile
import pstats
from pstats import SortKey
import time

# ----- ИМПОРТЫ ВНЕ ПРОФИЛИРОВАНИЯ -----
print("Загрузка данных...")
start_load = time.time()

p = Path(r'C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft\overworld\3\r.0.0.mca')
with open(p, "rb") as f:
    region_data = f.read()

region = RawRegion(region_data, TwoDimCord((0, 0)), "Nether")
parser = McaParser()

# Парсим регион один раз
rg = parser.parse(region)
print(f"Загрузка заняла: {time.time() - start_load:.2f} сек")


# ----- ФУНКЦИЯ ДЛЯ ПРОФИЛИРОВАНИЯ -----
def profile_reading_all_chunks():
    """Читаем ВСЕ чанки для реальной нагрузки"""
    readers_created = 0
    chunks_read = 0

    # Начинаем профилирование
    pr = cProfile.Profile()
    pr.enable()

    # Читаем МНОГО чанков
    for cord, raw_chunk in rg.raw_chunks.items():
        if raw_chunk.raw_data:
            reader = NBTTagReader(raw_chunk.raw_data)
            readers_created += 1

            # Читаем данные
            result = reader.read()  # Это то, что мы хотим профилировать
            if result:
                chunks_read += 1

    pr.disable()

    print(f"\nПрочитано {chunks_read} чанков из {readers_created} созданных ридеров")

    # Анализируем результаты
    print("\n" + "=" * 80)
    print("АНАЛИЗ ПРОФИЛЯ reader.read():")
    print("=" * 80)

    stats = pstats.Stats(pr)
    stats.strip_dirs()

    # 1. Общая статистика
    print("\n📊 ОБЩАЯ СТАТИСТИКА:")
    stats.print_stats(20)  # топ-10 функций

    # 2. Только ваши функции
    print("\n🔍 ВАШИ ФУНКЦИИ (исключая импорты и системные):")
    for func in stats.stats:
        func_name = func[2]
        # Ищем функции из вашего кода
        if any(keyword in str(func_name).lower() for keyword in
               ['nbt', 'reader', 'chunk', 'analyzer', 'mc_chunk']):
            ncalls, tottime, cumtime, callers = stats.stats[func]
            if ncalls > 0 and tottime > 0.001:  # только значимые
                avg_time = tottime / ncalls
                print(f"  {func_name}:")
                print(f"    Вызовы: {ncalls}, Общее время: {tottime:.4f}s, Среднее: {avg_time:.6f}s")

    # 3. Сохраняем для snakeviz
    stats.dump_stats('profile_reader.prof')
    print(f"\n📁 Профиль сохранен в 'profile_reader.prof'")
    print("   Для визуализации: python -m snakeviz profile_reader.prof")


# ----- ЗАПУСК -----
if __name__ == "__main__":
    # Сначала проверяем производительность без профилирования
    print("Тестовый запуск без профилирования...")
    start = time.time()

    test_count = 0
    for cord, raw_chunk in list(rg.raw_chunks.items())[:10]:  # первые 10 чанков
        if raw_chunk.raw_data:
            reader = NBTTagReader(raw_chunk.raw_data)
            reader.read()
            test_count += 1

    test_time = time.time() - start
    print(f"10 чанков за {test_time:.3f} сек (~{test_time / 10:.4f} сек/чанк)")

    # Если слишком быстро - увеличиваем нагрузку
    if test_time < 0.1:
        print("Выполняется слишком быстро! Увеличиваем нагрузку...")


        def heavy_load():
            """Повторяем много раз для накопления времени"""
            total_reads = 0
            for _ in range(100):  # 100 итераций
                for cord, raw_chunk in rg.raw_chunks.items():
                    if raw_chunk.raw_data and total_reads < 1000:  # максимум 1000 чтений
                        reader = NBTTagReader(raw_chunk.raw_data)
                        reader.read()
                        total_reads += 1
            return total_reads


        # Профилируем увеличенную нагрузку
        pr = cProfile.Profile()
        pr.enable()
        total = heavy_load()
        pr.disable()

        print(f"Прочитано {total} чанков")

        stats = pstats.Stats(pr)
        stats.strip_dirs()
        print("\n📊 ПРОФИЛЬ ПРИ УВЕЛИЧЕННОЙ НАГРУЗКЕ:")
        stats.sort_stats(SortKey.TIME).print_stats(20)
        stats.dump_stats('profile_heavy.prof')

    else:
        # Запускаем профилирование всех чанков
        profile_reading_all_chunks()