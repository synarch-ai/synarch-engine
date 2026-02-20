# C++ Core Guidance (Concise)

## Default Toolchain
- Language: C++20 (C++23 where supported)
- Build: CMake + Ninja; package manager Conan or vcpkg
- Compiler: Clang (preferred) or GCC; enable LTO for release
- CI: warnings as errors, reproducible builds

## Safety and Correctness
- Prefer RAII and smart pointers for ownership
- Use span/string_view for non-owning views
- Avoid UB: validate bounds, alignment, and lifetimes
- Use optional/expected for error handling instead of unchecked returns

## Concurrency
- Explicit thread model; avoid unbounded thread creation
- Use thread pools with bounded queues
- Prefer message passing or lock-free structures only when proven
- Protect shared state and document invariants

## Performance
- Profile before optimizing; use perf or vtune
- Reduce allocations in hot paths; use arenas where justified
- Keep data contiguous; avoid false sharing
- Use zero-copy I/O where safe

## Security Hardening
- Compile with stack protector, PIE, RELRO, FORTIFY
- Enable ASLR; consider seccomp/sandboxing for risky components
- Validate all untrusted inputs; avoid unsafe C APIs

## Testing
- Unit tests with Catch2 or GoogleTest
- Integration tests with realistic dependencies
- Fuzzing with libFuzzer or AFL for parsers
- Sanitizers in CI: ASan, UBSan, TSan
