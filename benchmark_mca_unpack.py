from mc_chunk_analyzer.domain.services.ChunkAnalyzer import McaParser
from mc_chunk_analyzer.domain.models.Region import RawRegion, TwoDimCord
from pathlib import Path
import time

# ----- LOAD FILE -----
p = Path(r'C:\Users\DNS\PycharmProjects\BedrockPatternFinder\minecraft\overworld\3\r.0.0.mca')
with open(p, "rb") as f:
    region_data = f.read()

region = RawRegion(region_data, TwoDimCord(0, 0), "Nether")
parser = McaParser()


# ----- BENCHMARK FUNCTION -----
def benchmark(func, runs=5):
    times = []
    for i in range(runs):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
        print(f"Run {i+1}: {times[-1]:.6f} sec")

    avg = sum(times) / runs
    best = min(times)
    worst = max(times)

    print("\n--- Benchmark Results ---")
    print(f"Runs: {runs}")
    print(f"Best:   {best:.6f} sec")
    print(f"Avg:    {avg:.6f} sec")
    print(f"Worst:  {worst:.6f} sec")


# ----- RUN BENCHMARK -----
benchmark(lambda: parser.parse(region))

print("\nDone!")
