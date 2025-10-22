# Performance Benchmark Specifications

**Project:** Unified Theming v1.0.0
**Week:** 3, Day 4 (Performance & Stress Testing)
**Author:** Claude Code
**Date:** October 21, 2025

---

## Executive Summary

This document defines performance benchmarks, stress test scenarios, and profiling requirements for the Unified Theming project. All benchmarks must pass before v0.5 release and must be maintained throughout the project lifecycle.

**Strategic Purpose:**
- Ensure responsive user experience (no perceived lag)
- Validate scalability (100+ themes, concurrent operations)
- Prevent performance regressions during development
- Identify bottlenecks early for optimization

---

## Performance Requirements

### Critical Path Operations

| Operation | Target | Acceptable | Unacceptable | Priority |
|-----------|--------|------------|--------------|----------|
| **Theme Discovery (100 themes)** | <3s | <5s | ≥5s | P0 |
| **Theme Discovery (500 themes)** | <15s | <20s | ≥20s | P0 |
| **Single Theme Parsing** | <30ms | <50ms | ≥50ms | P0 |
| **Color Extraction (per theme)** | <10ms | <20ms | ≥20ms | P0 |
| **Color Normalization (per color)** | <0.5ms | <1ms | ≥1ms | P1 |
| **Theme Application (all handlers)** | <1.5s | <2s | ≥2s | P0 |
| **CSS Generation (GTK4)** | <50ms | <100ms | ≥100ms | P1 |
| **kdeglobals Generation (Qt)** | <30ms | <50ms | ≥50ms | P1 |
| **Backup Creation** | <300ms | <500ms | ≥500ms | P0 |
| **Restore Operation** | <800ms | <1s | ≥1s | P0 |
| **CLI Startup Time** | <200ms | <300ms | ≥300ms | P1 |

**Measurement Method:** Average of 10 runs, excluding coldest and hottest (trim mean)

---

## Benchmark Definitions

### 1. Theme Discovery Benchmarks

**Purpose:** Validate theme scanning performance across multiple directories

#### Benchmark: `test_theme_discovery_100_themes`

**Setup:**
```python
# Create 100 valid themes in tmp directory
tmp_themes = create_test_themes(count=100, structure="complete")
# Structure: GTK2 + GTK3 + GTK4 + index.theme
```

**Test:**
```python
import time
from unified_theming.core.parser import UnifiedThemeParser

parser = UnifiedThemeParser()
start = time.perf_counter()
themes = parser.discover_themes(paths=[tmp_themes])
elapsed = time.perf_counter() - start

assert len(themes) == 100
assert elapsed < 5.0  # Target: <5s
```

**Success Criteria:**
- [ ] Discovers 100 themes correctly
- [ ] Completes in <5s (average of 10 runs)
- [ ] No memory leaks (memory usage returns to baseline)

---

#### Benchmark: `test_theme_discovery_500_themes`

**Setup:**
```python
tmp_themes = create_test_themes(count=500, structure="complete")
```

**Test:**
```python
start = time.perf_counter()
themes = parser.discover_themes(paths=[tmp_themes])
elapsed = time.perf_counter() - start

assert len(themes) == 500
assert elapsed < 20.0  # Target: <20s
```

**Success Criteria:**
- [ ] Discovers 500 themes correctly
- [ ] Completes in <20s
- [ ] Memory usage <500MB (reasonable for 500 themes)

---

#### Benchmark: `test_theme_discovery_incremental`

**Purpose:** Verify caching/incremental discovery (if implemented)

**Setup:**
```python
# First discovery: 100 themes
themes_initial = parser.discover_themes()

# Modify 1 theme (touch index.theme)
touch_theme_file(themes_path / "Adwaita/index.theme")

# Second discovery: should be faster (cached)
start = time.perf_counter()
themes_updated = parser.discover_themes()
elapsed = time.perf_counter() - start
```

**Success Criteria:**
- [ ] Second discovery <1s (10x faster than cold start)
- [ ] Detects modified theme correctly
- [ ] Cache invalidation works

---

### 2. Theme Parsing Benchmarks

**Purpose:** Validate single-theme parsing latency

#### Benchmark: `test_theme_parsing_latency`

**Setup:**
```python
# Use real theme (Adwaita-dark)
theme_path = Path("/usr/share/themes/Adwaita-dark")
```

**Test:**
```python
latencies = []
for _ in range(100):
    start = time.perf_counter()
    theme_info = parser.parse_theme(theme_path)
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

avg_latency = sum(latencies) / len(latencies)
p95_latency = sorted(latencies)[94]  # 95th percentile

assert avg_latency < 0.050  # <50ms average
assert p95_latency < 0.100  # <100ms p95
```

**Success Criteria:**
- [ ] Average parsing latency <50ms
- [ ] P95 latency <100ms (no outliers)
- [ ] No crashes on 100 iterations

---

### 3. Color Operation Benchmarks

**Purpose:** Validate color utilities performance (critical path for all handlers)

#### Benchmark: `test_color_normalization_latency`

**Setup:**
```python
from unified_theming.utils.color import normalize_color, ColorFormat

test_colors = [
    "#FF5733", "#3584E4", "#FFFFFF", "#000000",
    "rgb(255, 87, 51)", "rgba(53, 132, 228, 0.5)",
    "hsl(9, 100%, 60%)", "red", "blue", "green"
]
```

**Test:**
```python
latencies = []
for color in test_colors * 100:  # 1000 operations
    start = time.perf_counter()
    result = normalize_color(color, ColorFormat.HEX)
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

avg_latency = sum(latencies) / len(latencies)

assert avg_latency < 0.001  # <1ms per normalization
```

**Success Criteria:**
- [ ] Average latency <1ms per operation
- [ ] Total 1000 operations <1s

---

#### Benchmark: `test_color_extraction_from_css`

**Setup:**
```python
# Large CSS file with 50+ color definitions
css_content = generate_large_css(color_count=50)
```

**Test:**
```python
start = time.perf_counter()
color_palette = parser.extract_colors_from_css(css_content)
elapsed = time.perf_counter() - start

assert len(color_palette) == 50
assert elapsed < 0.020  # <20ms
```

**Success Criteria:**
- [ ] Extracts 50 colors in <20ms
- [ ] Handles @define-color, shade(), mix() functions

---

### 4. Theme Application Benchmarks

**Purpose:** Validate end-to-end theme application performance

#### Benchmark: `test_theme_application_e2e`

**Setup:**
```python
from unified_theming.core.manager import UnifiedThemeManager

manager = UnifiedThemeManager()
# Mock file I/O to isolate handler logic from disk speed
mock_file_operations()
```

**Test:**
```python
start = time.perf_counter()
result = manager.apply_theme("Adwaita-dark")
elapsed = time.perf_counter() - start

assert result.success is True
assert elapsed < 2.0  # <2s end-to-end
```

**Success Criteria:**
- [ ] Theme application completes in <2s
- [ ] All handlers execute (GTK/Qt/Flatpak/Snap)
- [ ] No blocking I/O delays

---

#### Benchmark: `test_theme_application_gtk_only`

**Purpose:** Measure single-handler performance

**Test:**
```python
start = time.perf_counter()
result = manager.apply_theme("Adwaita-dark", targets=["gtk"])
elapsed = time.perf_counter() - start

assert elapsed < 0.5  # <500ms for GTK only
```

**Success Criteria:**
- [ ] GTK-only application <500ms
- [ ] Qt-only application <400ms
- [ ] Flatpak-only application <300ms

---

### 5. Backup/Restore Benchmarks

**Purpose:** Validate config management performance

#### Benchmark: `test_backup_creation_latency`

**Setup:**
```python
from unified_theming.core.config import ConfigManager

config = ConfigManager()
# Populate config directories with realistic files
setup_realistic_config(gtk4_css_size="50KB", kvantum_size="200KB")
```

**Test:**
```python
latencies = []
for i in range(10):
    start = time.perf_counter()
    backup = config.create_backup(theme_name=f"Theme_{i}")
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

avg_latency = sum(latencies) / len(latencies)

assert avg_latency < 0.5  # <500ms average
```

**Success Criteria:**
- [ ] Average backup creation <500ms
- [ ] Handles large Kvantum themes (>200KB)
- [ ] No blocking file operations

---

#### Benchmark: `test_restore_operation_latency`

**Test:**
```python
backup = config.create_backup("TestTheme")

start = time.perf_counter()
success = config.restore_backup(backup.id)
elapsed = time.perf_counter() - start

assert success is True
assert elapsed < 1.0  # <1s restore
```

**Success Criteria:**
- [ ] Restore completes in <1s
- [ ] File integrity verified after restore

---

### 6. CLI Startup Benchmarks

**Purpose:** Validate CLI responsiveness

#### Benchmark: `test_cli_startup_time`

**Test:**
```bash
# Measure time from invocation to output
time unified-theming --help
# Expected: <300ms
```

**Python Test:**
```python
import subprocess
import time

latencies = []
for _ in range(10):
    start = time.perf_counter()
    subprocess.run(["unified-theming", "--help"], capture_output=True)
    elapsed = time.perf_counter() - start
    latencies.append(elapsed)

avg_latency = sum(latencies) / len(latencies)

assert avg_latency < 0.3  # <300ms
```

**Success Criteria:**
- [ ] CLI startup <300ms (cold start)
- [ ] Help text renders immediately
- [ ] No import delays

---

## Stress Test Scenarios

### 1. Concurrent Theme Applications

**Purpose:** Test thread safety and race conditions

**Test:**
```python
import threading

def apply_theme_worker(theme_name):
    manager = UnifiedThemeManager()
    result = manager.apply_theme(theme_name)
    return result

themes = ["Adwaita", "Adwaita-dark", "Breeze", "Breeze-Dark"]

threads = []
for theme in themes * 5:  # 20 concurrent applications
    t = threading.Thread(target=apply_theme_worker, args=(theme,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Validate: No crashes, no corrupted configs
assert all_configs_valid()
```

**Success Criteria:**
- [ ] No crashes during concurrent operations
- [ ] No config file corruption
- [ ] Results are consistent (no race conditions)

---

### 2. Low Memory Conditions

**Purpose:** Test graceful degradation under memory pressure

**Test:**
```python
import resource

# Limit process memory to 100MB
resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, -1))

try:
    themes = parser.discover_themes()  # May hit memory limit
    assert len(themes) > 0  # Should still discover some themes
except MemoryError:
    pytest.fail("Should handle low memory gracefully")
```

**Success Criteria:**
- [ ] No crashes under low memory (graceful error messages)
- [ ] Logs warning about memory constraints
- [ ] Partial results returned (not all-or-nothing)

---

### 3. Rapid Theme Switching

**Purpose:** Test stability during rapid operations

**Test:**
```python
themes = ["Adwaita", "Adwaita-dark"] * 10  # 20 switches

for theme in themes:
    result = manager.apply_theme(theme)
    assert result.success is True
    time.sleep(0.1)  # 100ms between switches

# Validate: Configs stable, no memory leaks
assert get_process_memory() < initial_memory * 1.5
```

**Success Criteria:**
- [ ] 20 theme switches complete without crashes
- [ ] Memory usage <150% of baseline (no major leaks)
- [ ] Final config is consistent

---

### 4. Corrupted Theme Handling

**Purpose:** Test resilience to malformed inputs

**Test:**
```python
corrupted_themes = create_corrupted_themes([
    "missing_index_theme",
    "malformed_css_syntax",
    "invalid_color_values",
    "symlink_loop",
    "permission_denied",
])

for theme_path in corrupted_themes:
    result = parser.parse_theme(theme_path)
    # Should return None or raise ThemeParseError, not crash
    assert result is None or isinstance(result, Exception)
```

**Success Criteria:**
- [ ] No crashes on corrupted themes
- [ ] User-friendly error messages
- [ ] Continues discovery (skips corrupted, processes valid)

---

### 5. Large Theme Directory Stress

**Purpose:** Test scalability limits

**Test:**
```python
# Create 1000 themes (stress test)
tmp_themes = create_test_themes(count=1000, structure="complete")

start = time.perf_counter()
themes = parser.discover_themes(paths=[tmp_themes])
elapsed = time.perf_counter() - start

assert len(themes) == 1000
# Acceptable degradation: 1000 themes in <60s
assert elapsed < 60.0
```

**Success Criteria:**
- [ ] Discovers 1000 themes in <60s
- [ ] Memory usage <1GB
- [ ] No crashes or timeouts

---

### 6. Filesystem Edge Cases

**Purpose:** Test handling of unusual filesystem scenarios

**Test Cases:**
- [ ] Theme path with spaces: `/themes/My Theme/`
- [ ] Theme path with unicode: `/themes/テーマ/`
- [ ] Symlinks to theme directories
- [ ] Read-only theme directories
- [ ] Theme on NFS/network mount (slow I/O)
- [ ] Theme on full disk (backup fails gracefully)

**Success Criteria:**
- [ ] Handles all edge cases without crashes
- [ ] Clear error messages for failures
- [ ] No data corruption

---

## Memory Leak Detection

### Test: `test_memory_leak_theme_discovery`

**Purpose:** Ensure theme discovery doesn't leak memory over multiple iterations

**Test:**
```python
import gc
import tracemalloc

tracemalloc.start()

baseline_memory = get_process_memory()

for _ in range(100):
    themes = parser.discover_themes()
    gc.collect()

final_memory = get_process_memory()
memory_growth = final_memory - baseline_memory

# Allow 10% growth (caching acceptable), not 2x
assert memory_growth < baseline_memory * 0.1
```

**Success Criteria:**
- [ ] Memory growth <10% after 100 iterations
- [ ] No unbounded growth (caching is fine, leaks are not)

---

### Test: `test_memory_leak_theme_application`

**Test:**
```python
baseline_memory = get_process_memory()

for _ in range(50):
    manager.apply_theme("Adwaita")
    manager.apply_theme("Adwaita-dark")
    gc.collect()

final_memory = get_process_memory()
memory_growth = final_memory - baseline_memory

assert memory_growth < baseline_memory * 0.15
```

**Success Criteria:**
- [ ] Memory growth <15% after 50 theme applications
- [ ] No file handle leaks

---

## Profiling Requirements

### CPU Profiling

**Tool:** `cProfile` + `snakeviz` (visualization)

**Test:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Profile theme discovery
themes = parser.discover_themes()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions

# Save for visualization
stats.dump_stats('theme_discovery.prof')
# View with: snakeviz theme_discovery.prof
```

**Analysis:**
- [ ] Identify top 5 CPU-intensive functions
- [ ] Check for unexpected O(n²) algorithms
- [ ] Validate no blocking I/O in CPU profile

---

### Memory Profiling

**Tool:** `memory_profiler` or `tracemalloc`

**Test:**
```python
from memory_profiler import profile

@profile
def profile_theme_discovery():
    parser = UnifiedThemeParser()
    themes = parser.discover_themes()
    return themes

profile_theme_discovery()
# Output shows memory usage per line
```

**Analysis:**
- [ ] Identify memory hotspots (large allocations)
- [ ] Check for unnecessary data duplication
- [ ] Validate theme data structures are efficient

---

### I/O Profiling

**Tool:** `strace` or `iotop` (Linux)

**Test:**
```bash
# Trace file operations during theme discovery
strace -c -e trace=file unified-theming list

# Output shows file I/O statistics
```

**Analysis:**
- [ ] Count of `open()` calls (should be ~number of themes)
- [ ] No redundant file reads (same file read multiple times)
- [ ] Efficient directory traversal (minimal `stat()` calls)

---

## Performance Regression Testing

### Continuous Benchmarking

**Tool:** `pytest-benchmark`

**Setup:**
```python
# tests/test_performance_benchmarks.py
def test_theme_discovery_benchmark(benchmark):
    parser = UnifiedThemeParser()
    result = benchmark(parser.discover_themes)
    assert len(result) > 0

# Run: pytest tests/test_performance_benchmarks.py --benchmark-only
```

**CI Integration:**
```yaml
# .github/workflows/benchmarks.yml
name: Performance Benchmarks
on: [push, pull_request]
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/test_performance_benchmarks.py --benchmark-json=output.json
      - name: Check regression
        run: |
          # Compare output.json to baseline, fail if >20% slower
```

**Regression Detection:**
- [ ] Baseline established on main branch
- [ ] PRs compared against baseline
- [ ] Alert if >20% performance degradation

---

## Optimization Opportunities

### Identified Bottlenecks (From Profiling)

**1. Theme Discovery (Expected Bottleneck):**
- **Cause:** Sequential directory traversal + file I/O
- **Optimization:** Parallel scanning (ThreadPoolExecutor)
- **Expected Gain:** 2-3x speedup on multi-core systems

**2. CSS Parsing (Potential Bottleneck):**
- **Cause:** Regex parsing of large CSS files
- **Optimization:** Lazy parsing (only parse when colors needed)
- **Expected Gain:** 50% reduction in parsing time

**3. Color Translation (Minor Bottleneck):**
- **Cause:** Repeated RGB↔HSL conversions
- **Optimization:** Memoization/caching
- **Expected Gain:** 10-20% reduction in application time

---

### Optimization Checklist (Week 3, Day 4)

**If benchmarks fail:**
- [ ] Run profiler to identify bottleneck
- [ ] Implement targeted optimization (not premature)
- [ ] Re-run benchmarks to validate improvement
- [ ] Ensure optimization doesn't break tests

**Optimization Priorities:**
1. **P0:** Theme discovery (most user-visible)
2. **P1:** Theme application (second most user-visible)
3. **P2:** Color operations (micro-optimization, only if needed)

---

## Test Data Requirements

### Synthetic Test Themes

**Helper Function:**
```python
def create_test_themes(count: int, structure: str = "complete") -> Path:
    """
    Create synthetic themes for performance testing.

    Args:
        count: Number of themes to create
        structure: "complete" (GTK2+3+4), "minimal" (GTK3 only), "mixed"

    Returns:
        Path to directory containing test themes
    """
    tmp_dir = Path("/tmp/unified_theming_perf_test")
    tmp_dir.mkdir(exist_ok=True)

    for i in range(count):
        theme_name = f"PerfTestTheme_{i:04d}"
        theme_dir = tmp_dir / theme_name

        if structure == "complete":
            create_gtk2_structure(theme_dir)
            create_gtk3_structure(theme_dir)
            create_gtk4_structure(theme_dir)
        elif structure == "minimal":
            create_gtk3_structure(theme_dir)
        elif structure == "mixed":
            # Randomize structure
            pass

        create_index_theme(theme_dir, theme_name)

    return tmp_dir
```

---

### Real-World Themes

**Use actual system themes for realistic testing:**
- Adwaita / Adwaita-dark (GNOME default)
- Breeze / Breeze-Dark (KDE default)
- Arc / Arc-Dark (popular third-party)
- Materia (popular, complex CSS)
- Nordic (popular, custom colors)

**Validation:**
- [ ] Tests work with real system themes
- [ ] Performance realistic (not just synthetic themes)

---

## Acceptance Criteria (Week 3, Day 4)

### Benchmark Pass Rate

**MUST PASS (Blockers for v0.5):**
- [ ] Theme discovery (100 themes): <5s
- [ ] Theme discovery (500 themes): <20s
- [ ] Theme application e2e: <2s
- [ ] Backup creation: <500ms
- [ ] Restore operation: <1s

**SHOULD PASS (Acceptable if minor miss):**
- [ ] Theme parsing latency: <50ms (acceptable: <80ms)
- [ ] Color normalization: <1ms (acceptable: <2ms)
- [ ] CSS generation: <100ms (acceptable: <150ms)

**NICE TO HAVE:**
- [ ] CLI startup: <300ms
- [ ] Incremental discovery: <1s

---

### Stress Test Pass Rate

**MUST PASS:**
- [ ] Concurrent applications: No crashes, no corruption
- [ ] Rapid switching (20 switches): No crashes, memory stable
- [ ] Corrupted themes: No crashes, graceful errors

**SHOULD PASS:**
- [ ] Low memory: Graceful degradation
- [ ] Large directory (1000 themes): Completes in <60s
- [ ] Filesystem edge cases: Handles gracefully

---

### Memory Leak Tests

**MUST PASS:**
- [ ] Discovery memory growth: <10%
- [ ] Application memory growth: <15%
- [ ] No file handle leaks

---

## Deliverables (Week 3, Day 4)

1. **Test file:** `tests/test_performance_stress.py`
2. **Benchmark results:** `docs/benchmark_results_week3.md` (table of results)
3. **Profiling reports:** `docs/profiling/` (CPU/memory/I/O profiles)
4. **Optimization log:** `docs/optimization_log.md` (bottlenecks + fixes)

---

## Handoff to Opencode AI

**Trigger:** Git tag `qa/week3-performance`

**Validation by Opencode AI:**
- [ ] All P0 benchmarks pass
- [ ] All P0 stress tests pass
- [ ] Memory leak tests pass
- [ ] Profiling reports generated
- [ ] Performance meets v0.5 release criteria

**Output:** `docs/performance_validation_week3.md`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-21 | Initial benchmark specifications | Claude Code |

---

**These benchmarks ensure Unified Theming is fast, scalable, and production-ready.** ⚡
