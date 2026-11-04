# PawnJIT

PawnJIT is a just-in-time (JIT) compiler for the Pawn scripting language, designed for open.mp servers.

It compiles Pawn bytecode into native machine code at runtime, reducing interpreter overhead and significantly improving script execution performance without requiring changes to existing scripts.

PawnJIT is approximately 5x faster than the standard Pawn VM, achieving an average speedup of 4.67x in benchmarks. Actual performance gains depend on the workload.

## Performance

Benchmark results comparing the standard Pawn VM against PawnJIT on the same machine.

| Benchmark | Pawn VM | PawnJIT | Speedup |
|---|---:|---:|---:|
| Arithmetic | 363.28 µs | 62.26 µs | **5.84x** |
| Loops | 262.70 µs | 41.99 µs | **6.26x** |
| Function Calls | 375.00 µs | 86.43 µs | **4.34x** |
| Control Flow | 244.14 µs | 78.13 µs | **3.13x** |
| Raw Calls | 44.43 µs | 11.05 µs | **4.02x** |
| Parity Stress | 337.89 µs | 73.73 µs | **4.58x** |
| Differential Fuzz | 91.31 µs | 17.27 µs | **5.29x** |

## sampctl

Install PawnJIT directly with sampctl (currently pinned to the packaging branch for testing):

```bash
sampctl install RaP-SoR/PawnJIT@sampctl-pawn-json
```

Or declare it manually in your package `pawn.json` and then run `sampctl ensure`:

```json
{
    "dependencies": [
        "RaP-SoR/PawnJIT@sampctl-pawn-json"
    ]
}
```

sampctl downloads the matching GitHub release asset and installs:

- Linux: `components/PawnJIT.so`
- Windows: `components/PawnJIT.dll` and `components/PawnJIT.pdb`

Keep the PDB next to the DLL when investigating crashes; it provides symbols for debuggers and crash dumps.

## Build

```bash
git clone --recurse-submodules https://github.com/RaP-SoR/PawnJIT.git
cd PawnJIT

# Windows
cmake -S . -B build -A Win32
cmake --build build --config Release

# Linux
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j$(nproc)
```

The binary ends up in `build/Release/PawnJIT.dll` on Windows and `build/PawnJIT.so` on Linux.
The Windows Release build also writes `PawnJIT.pdb` next to the DLL.
Use `Debug` for development or `RelWithDebInfo` for an optimized build with additional debug information.

## Release

A successful build on `master` publishes GitHub Release `v<version>`. `<version>` is `project(PawnJIT VERSION ...)` in `CMakeLists.txt`. The archive names and paths come from `pawn.json`, so the files on the release page are the ones a user downloads:

- `PawnJIT-<version>-linux.tar.gz` with `components/PawnJIT.so`, built on Ubuntu 24.04 (also runs on Debian 13)
- `PawnJIT-<version>-win32.zip` with `components/PawnJIT.dll` and `components/PawnJIT.pdb`, built on Windows Server 2022

A later build of the same version replaces those assets. Pull requests upload the same archives as workflow artifacts and do not publish a release. A tag `v<version>` publishes as well, and fails when it does not match the CMake version.

The build can also be started by hand: on GitHub open **Actions**, choose **Build**, then **Run workflow** on `master`. That publishes the same release. The button is available once this workflow file is on the default branch.

## License

The plugin code is licensed under [MPL 2.0](LICENSE).
Dependencies and borrowed SDK code keep their own licenses.
