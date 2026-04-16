---
name: cli-extension-building
description: "Build standalone CLI extension binaries for systemprompt.io with clap, manifest discovery, and subprocess integration"
---

# CLI Extension Building

Build standalone CLI extension binaries for systemprompt.io. Reference implementation: `extensions/cli/discord/`.

## Core Principle

CLI extensions are standalone binaries discovered via `manifest.yaml`. They run as separate processes launched by `systemprompt plugins run <name>`.

## Directory Structure

```
extensions/cli/{name}/
├── Cargo.toml
├── manifest.yaml
└── src/
    └── main.rs
```

## manifest.yaml

```yaml
extension:
  type: cli
  name: my-extension
  binary: systemprompt-my-extension
  description: "What this extension does"
  enabled: true
  commands:
    - name: do-something
      description: "Does something useful"
    - name: another-command
      description: "Another useful command"
```

## Cargo.toml

```toml
[package]
name = "systemprompt-my-extension"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "systemprompt-my-extension"
path = "src/main.rs"

[dependencies]
clap = { version = "4.4", features = ["derive"] }
tokio = { version = "1.47", features = ["full"] }
anyhow = "1.0"
thiserror = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_yaml = "0.9"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
```

## Main Entry Point

```rust
use clap::{Parser, Subcommand};
use tracing_subscriber::EnvFilter;

#[derive(Parser)]
#[command(name = "systemprompt-my-extension")]
#[command(about = "My CLI extension description")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    DoSomething {
        input: String,
        #[arg(long, short)]
        verbose: bool,
    },
    AnotherCommand {
        #[arg(long)]
        option: Option<String>,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .init();

    let cli = Cli::parse();

    match cli.command {
        Commands::DoSomething { input, verbose } => {
            do_something(&input, verbose).await?;
        }
        Commands::AnotherCommand { option } => {
            another_command(option).await?;
        }
    }

    Ok(())
}

async fn do_something(input: &str, verbose: bool) -> anyhow::Result<()> {
    println!("Processing: {}", input);
    Ok(())
}

async fn another_command(option: Option<String>) -> anyhow::Result<()> {
    Ok(())
}
```

## Environment Variables

The main CLI passes these environment variables to extensions:

| Variable | Description |
|----------|-------------|
| `SYSTEMPROMPT_PROFILE` | Path to active profile directory |
| `DATABASE_URL` | Database connection string |

```rust
fn get_profile_path() -> anyhow::Result<std::path::PathBuf> {
    std::env::var("SYSTEMPROMPT_PROFILE")
        .map(std::path::PathBuf::from)
        .map_err(|_| anyhow::anyhow!("SYSTEMPROMPT_PROFILE not set"))
}

fn get_database_url() -> anyhow::Result<String> {
    std::env::var("DATABASE_URL")
        .map_err(|_| anyhow::anyhow!("DATABASE_URL not set"))
}
```

## Configuration

Load extension config from the profile directory:

```rust
use serde::Deserialize;
use std::path::Path;

#[derive(Debug, Deserialize)]
struct MyConfig {
    api_key: String,
    enabled: bool,
}

fn load_config(profile_path: &Path) -> anyhow::Result<MyConfig> {
    let config_path = profile_path.join("extensions/my-extension.yaml");
    let content = std::fs::read_to_string(&config_path)?;
    let config: MyConfig = serde_yaml::from_str(&content)?;
    Ok(config)
}
```

## Error Handling

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum MyExtensionError {
    #[error("Configuration error: {0}")]
    Config(String),

    #[error("API error: {0}")]
    Api(String),

    #[error("Not found: {0}")]
    NotFound(String),
}
```

## Workspace Registration

Add to workspace `Cargo.toml`:

```toml
[workspace]
members = [
    "extensions/cli/my-extension",
]
```

## CLI Extension Checklist

- [ ] `manifest.yaml` with `type: cli` and command definitions
- [ ] Package name follows `systemprompt-{name}` pattern
- [ ] Binary name matches `manifest.yaml` binary field
- [ ] Located in `extensions/cli/`
- [ ] Uses clap with derive macros for argument parsing
- [ ] Initializes tracing for logging
- [ ] Returns `anyhow::Result<()>` from main
- [ ] Added to workspace members in root `Cargo.toml`
- [ ] No `unwrap()` - use `?` or `ok_or_else()`
- [ ] File length <= 300 lines
- [ ] Function length <= 75 lines
- [ ] `cargo clippy -p {crate} -- -D warnings` passes

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Extension not found | Check `manifest.yaml` exists in extension directory |
| Binary not found | Run `cargo build -p systemprompt-{name}` |
| Environment error | Verify CLI passes `SYSTEMPROMPT_PROFILE` and `DATABASE_URL` |
| Config file missing | Check profile path and extension config exists |

## Quick Reference

| Task | Command |
|------|---------|
| Build | `cargo build -p systemprompt-{name}` |
| Run directly | `cargo run -p systemprompt-{name} -- <args>` |
| Run via CLI | `systemprompt plugins run {name} <args>` |
| List extensions | `systemprompt plugins list --type cli` |
| Lint | `cargo clippy -p systemprompt-{name} -- -D warnings` |
| Format | `cargo fmt -p systemprompt-{name} -- --check` |

## Reference Implementations

| Concept | Location |
|---------|----------|
| CLI extension | `extensions/cli/discord/` |
| Manifest file | `extensions/cli/discord/manifest.yaml` |
| Main entry | `extensions/cli/discord/src/main.rs` |
