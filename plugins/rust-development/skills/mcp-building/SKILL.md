---
name: mcp-building
description: "Build MCP servers for systemprompt.io with tools, artifacts, UI resources, and AI service integration"
---

# MCP Building

Build MCP servers for systemprompt.io. Reference implementation: `extensions/mcp/systemprompt/`.

## Core Principle

**MCP servers are Rust code and belong in `/extensions/mcp/`, not `/services/mcp/`.**

## Directory Structure

```
extensions/mcp/{name}/
├── Cargo.toml
├── module.yml
└── src/
    ├── main.rs             # Entry point
    ├── lib.rs              # Library for testing
    ├── server.rs           # ServerHandler implementation
    └── tools/
        ├── mod.rs          # Registration & dispatch
        └── {tool_name}/    # Each tool in subdirectory
            ├── mod.rs
            ├── handler.rs
            └── helpers.rs
```

## Cargo.toml

```toml
[package]
name = "systemprompt-mcp-my-server"
version = "1.0.0"
edition = "2021"

[[bin]]
name = "systemprompt-mcp-my-server"
path = "src/main.rs"

[lib]
path = "src/lib.rs"

[dependencies]
systemprompt = { workspace = true }
rmcp = { workspace = true }
tokio = { workspace = true, features = ["full"] }
axum = { workspace = true }
serde = { workspace = true, features = ["derive"] }
serde_json = { workspace = true }
anyhow = { workspace = true }
thiserror = { workspace = true }
tracing = { workspace = true }
```

## module.yml

```yaml
name: my-server
display_name: "My MCP Server"
version: "1.0.0"
description: "Provides tools for X, Y, Z"

server:
  port: 5003
  host: "0.0.0.0"

tools:
  - name: my_tool
    description: "Does something useful"
```

## Main Entry Point

```rust
use anyhow::{Context, Result};
use std::{env, sync::Arc};
use systemprompt::identifiers::McpServerId;
use systemprompt::models::{Config, ProfileBootstrap, SecretsBootstrap};
use systemprompt::system::AppContext;
use tokio::net::TcpListener;

const DEFAULT_SERVICE_ID: &str = "my-server";
const DEFAULT_PORT: u16 = 5050;

#[tokio::main]
async fn main() -> Result<()> {
    ProfileBootstrap::init().context("Failed to initialize profile")?;
    SecretsBootstrap::init().context("Failed to initialize secrets")?;
    Config::init().context("Failed to initialize configuration")?;

    let ctx = Arc::new(
        AppContext::new().await.context("Failed to initialize application context")?,
    );

    systemprompt::logging::init_logging(ctx.db_pool().clone());

    let service_id = McpServerId::from_env().unwrap_or_else(|_| {
        tracing::warn!("MCP_SERVICE_ID not set, using default: {DEFAULT_SERVICE_ID}");
        McpServerId::new(DEFAULT_SERVICE_ID)
    });

    let port = env::var("MCP_PORT")
        .ok()
        .and_then(|p| p.parse::<u16>().ok())
        .unwrap_or(DEFAULT_PORT);

    let server = systemprompt_mcp_my_server::MyServer::new(
        ctx.db_pool().clone(),
        service_id.clone(),
    );
    let router = systemprompt::mcp::create_router(server, ctx.db_pool());

    let addr = format!("0.0.0.0:{port}");
    let listener = TcpListener::bind(&addr).await?;
    tracing::info!(service_id = %service_id, addr = %addr, "MCP server listening");
    axum::serve(listener, router).await?;
    Ok(())
}
```

## ServerHandler Implementation

```rust
use rmcp::model::{
    CallToolRequestParams, CallToolResult, Implementation, InitializeRequestParams,
    InitializeResult, ListToolsResult, PaginatedRequestParams, ProtocolVersion,
    ServerCapabilities, ServerInfo,
};
use rmcp::service::{RequestContext, RoleServer};
use rmcp::{ErrorData as McpError, ServerHandler};
use systemprompt::database::DbPool;
use systemprompt::identifiers::McpServerId;

#[derive(Clone)]
pub struct MyServer {
    db_pool: DbPool,
    service_id: McpServerId,
}

impl MyServer {
    #[must_use]
    pub fn new(db_pool: DbPool, service_id: McpServerId) -> Self {
        Self { db_pool, service_id }
    }
}

impl ServerHandler for MyServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            protocol_version: ProtocolVersion::V_2024_11_05,
            capabilities: ServerCapabilities::builder()
                .enable_tools()
                .build(),
            server_info: Implementation {
                name: format!("My Server ({})", self.service_id),
                version: env!("CARGO_PKG_VERSION").to_string(),
                icons: None,
                title: Some("My MCP Server".to_string()),
                website_url: None,
            },
            instructions: Some("This server provides tools for X, Y, Z.".to_string()),
        }
    }

    async fn list_tools(
        &self,
        _request: Option<PaginatedRequestParams>,
        _ctx: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, McpError> {
        Ok(ListToolsResult {
            tools: tools::list_tools(),
            next_cursor: None,
            meta: None,
        })
    }

    async fn call_tool(
        &self,
        request: CallToolRequestParams,
        ctx: RequestContext<RoleServer>,
    ) -> Result<CallToolResult, McpError> {
        let tool_name = request.name.to_string();
        tools::handle_tool_call(&tool_name, request, &self.db_pool).await
    }
}
```

## Tool Registration (tools/mod.rs)

```rust
use rmcp::model::{CallToolRequestParams, CallToolResult, Tool};
use rmcp::ErrorData as McpError;
use std::sync::Arc;
use systemprompt::database::DbPool;

pub mod my_tool;

pub fn list_tools() -> Vec<Tool> {
    vec![
        create_tool(
            "my_tool",
            "My Tool",
            "Does something useful. Provide 'input' parameter.",
            my_tool::input_schema(),
            my_tool::output_schema(),
        ),
    ]
}

fn create_tool(
    name: &str,
    title: &str,
    description: &str,
    // JSON: MCP protocol boundary -- Tool schema fields require serde_json::Value
    input_schema: serde_json::Value,
    output_schema: serde_json::Value,
) -> Tool {
    let input_obj = input_schema.as_object().cloned().unwrap_or_default();
    let output_obj = output_schema.as_object().cloned().unwrap_or_default();
    Tool {
        name: name.to_string().into(),
        title: Some(title.to_string()),
        description: Some(description.to_string().into()),
        input_schema: Arc::new(input_obj),
        output_schema: Some(Arc::new(output_obj)),
        annotations: None,
        icons: None,
        meta: None,
    }
}

pub async fn handle_tool_call(
    name: &str,
    request: CallToolRequestParams,
    db_pool: &DbPool,
) -> Result<CallToolResult, McpError> {
    match name {
        "my_tool" => my_tool::handle(db_pool, request).await,
        _ => Err(McpError::invalid_params(format!("Unknown tool: '{name}'"), None)),
    }
}
```

## Tool Module Pattern

**Tool arguments MUST be deserialized into typed structs with `#[derive(Deserialize)]`. Never extract fields manually from `serde_json::Map`.**

### mod.rs

```rust
mod handler;
mod helpers;

pub use handler::handle;
pub use helpers::{input_schema, output_schema};
```

### helpers.rs (Schemas)

```rust
use serde_json::json;

// JSON: MCP protocol boundary -- Tool schema must be serde_json::Value
pub fn input_schema() -> serde_json::Value {
    json!({
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "The input to process"
            }
        },
        "required": ["input"]
    })
}

// JSON: MCP protocol boundary -- Tool schema must be serde_json::Value
pub fn output_schema() -> serde_json::Value {
    json!({
        "type": "object",
        "properties": {
            "result": { "type": "string", "description": "The processed result" },
            "status": { "type": "string", "enum": ["success", "error"] }
        }
    })
}

use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct MyToolArgs {
    pub input: String,
    #[serde(default)]
    pub tags: Vec<String>,
}
```

### handler.rs

```rust
use rmcp::model::{CallToolRequestParams, CallToolResult, Content};
use rmcp::ErrorData as McpError;
use serde_json::json;
use systemprompt::database::DbPool;

use super::helpers::MyToolArgs;

pub async fn handle(
    _db_pool: &DbPool,
    request: CallToolRequestParams,
) -> Result<CallToolResult, McpError> {
    let args: MyToolArgs = request
        .arguments
        .as_ref()
        .ok_or_else(|| McpError::invalid_request("Missing arguments", None))
        .and_then(|map| {
            serde_json::from_value(serde_json::Value::Object(map.clone()))
                .map_err(|e| McpError::invalid_params(format!("Invalid arguments: {e}"), None))
        })?;

    let result = format!("Processed: {}", args.input);
    tracing::info!(input = %args.input, "Tool executed successfully");

    Ok(CallToolResult {
        content: vec![Content::text(format!("Result: {result}"))],
        // JSON: MCP protocol boundary -- structured_content is Option<serde_json::Value> per spec
        structured_content: Some(json!({ "result": result, "status": "success" })),
        is_error: Some(false),
        meta: None,
    })
}
```

## Artifacts and ToolResponse

**MCP tools do NOT save artifacts directly. Return artifact data in `structured_content` and the agent handles persistence.**

### Correct Pattern

```rust
use systemprompt::models::artifacts::{TextArtifact, ToolResponse};
use systemprompt::models::ExecutionMetadata;
use systemprompt::identifiers::{ArtifactId, McpExecutionId};

async fn handle_my_tool(
    request: CallToolRequestParams,
    ctx: &RequestContext,
    mcp_execution_id: &McpExecutionId,
) -> Result<CallToolResult, McpError> {
    let content = generate_content().await?;

    let artifact = TextArtifact::new(&content, ctx)
        .with_title("My Generated Content")
        .with_skill(skill_id, "My Skill");

    let metadata = ExecutionMetadata::with_request(ctx)
        .with_tool("my_tool")
        .with_skill(skill_id, "My Skill");

    let response = ToolResponse::new(
        ArtifactId::generate(),
        mcp_execution_id.clone(),
        artifact,
        metadata.clone(),
    );

    Ok(CallToolResult {
        content: vec![Content::text("Human readable summary")],
        structured_content: response.to_json().ok(),
        is_error: Some(false),
        meta: metadata.to_meta(),
    })
}
```

### Available Core Artifact Types

| Type | Use For |
|------|---------|
| `TextArtifact` | Blog posts, articles, documents |
| `ResearchArtifact` | Research with sources |
| `ImageArtifact` | Generated images |
| `TableArtifact` | Tabular data |
| `ListArtifact` | Lists |
| `ChartArtifact` | Charts and graphs |
| `CopyPasteTextArtifact` | Social content, snippets |
| `DashboardArtifact` | Dashboard layouts |

**DO NOT create custom artifact structs.** Use core types or request new ones in core.

## Progress Callback

```rust
pub type ProgressCallback = Box<
    dyn Fn(f64, Option<f64>, Option<String>) -> Pin<Box<dyn Future<Output = ()> + Send>>
        + Send + Sync,
>;

if let Some(ref notify) = progress {
    notify(50.0, Some(100.0), Some("Processing...".to_string())).await;
}
```

## UI Resources

### Enable Resources

```rust
capabilities: ServerCapabilities::builder()
    .enable_tools()
    .enable_resources()
    .build(),
```

### Resource URI Pattern

```
ui://{server_name}/{artifact_id}
```

### Implement Resource Templates

```rust
let template = ResourceTemplate {
    raw: RawResourceTemplate {
        uri_template: format!("ui://{SERVER_NAME}/{{artifact_id}}"),
        name: "artifact-ui".to_string(),
        description: Some("Interactive UI for artifacts.".to_string()),
        mime_type: Some(MCP_APP_MIME_TYPE.to_string()),
        ..Default::default()
    },
    annotations: None,
};
```

## AI Service Integration

```rust
use systemprompt::ai::{AiService, AiMessage, GoogleSearchParams, NoopToolProvider};
use systemprompt::loader::EnhancedConfigLoader;

let config_loader = EnhancedConfigLoader::from_env()?;
let services_config = config_loader.load()?;
let tool_provider = Arc::new(NoopToolProvider::new());
let ai_service = Arc::new(AiService::new(
    db_pool.clone(),
    &services_config.ai,
    tool_provider,
    None,
)?);

let params = GoogleSearchParams {
    messages: vec![
        AiMessage::system(&skill_content),
        AiMessage::user(&prompt),
    ],
    sampling: None,
    max_output_tokens: 8192,
    model: Some("gemini-2.5-flash"),
    urls: None,
    response_schema: None,
};

let response = ai_service.generate_with_google_search(params).await?;
```

## RBAC Middleware

```rust
use systemprompt::mcp::middleware::enforce_rbac_from_registry;

let auth_result = enforce_rbac_from_registry(&ctx, service_id.as_str()).await?;
let authenticated_ctx = auth_result.expect_authenticated("Auth required")?;
let request_context = authenticated_ctx.context.clone();
```

## Tool Execution Tracking

```rust
use systemprompt::mcp::repository::ToolUsageRepository;
use systemprompt::mcp::models::{ToolExecutionRequest, ToolExecutionResult};

let mcp_execution_id = self.tool_usage_repo.start_execution(&execution_request).await?;
// ... execute tool ...
self.tool_usage_repo.complete_execution(&mcp_execution_id, &execution_result).await?;
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SYSTEMPROMPT_PROFILE` | Active profile configuration path |
| `JWT_SECRET` | JWT signing secret |
| `DATABASE_URL` | Database connection string |
| `MCP_SERVICE_ID` | Unique service identifier |
| `MCP_PORT` | Server listening port |
| `AI_CONFIG_PATH` | AI configuration file path |
| `SYSTEM_PATH` | System root directory path |

**Path Resolution**: Never hardcode absolute paths. Use `FilesConfig` for validated storage paths.

```rust
use systemprompt::files::FilesConfig;
FilesConfig::init().context("Failed to initialize FilesConfig")?;
let files_config = FilesConfig::get().context("Failed to get FilesConfig")?;
```

## Server Registration

### Create config file: `services/mcp/{name}.yaml`

```yaml
mcp_servers:
  my-server:
    binary: "systemprompt-mcp-my-server"
    package: "my-server"
    port: 5050
    endpoint: "http://localhost:8080/api/v1/mcp/my-server/mcp"
    enabled: true
    display_in_web: true
    description: "My MCP Server - does X, Y, Z"
    oauth:
      required: true
      scopes: ["admin"]
      audience: "mcp"
      client_id: null
```

### Add to `services/config/config.yaml` includes

```yaml
includes:
  - ../mcp/my-server.yaml
```

## Error Handling

```rust
use rmcp::ErrorData as McpError;

Err(McpError::invalid_params("Missing required parameter: topic", None))
Err(McpError::invalid_request("Arguments must be provided", None))
Err(McpError::internal_error(format!("Failed: {e}"), None))
```

## MCP Server Checklist

- [ ] Package name follows `systemprompt-mcp-{name}` pattern
- [ ] Located in `extensions/mcp/`
- [ ] `module.yml` with server metadata and tools
- [ ] Binary target defined in `Cargo.toml`
- [ ] Initializes logging and config
- [ ] Tools have unique names with input/output schemas
- [ ] Tool handlers validate all required parameters
- [ ] Returns both `content` and `structured_content`
- [ ] `is_error` always set
- [ ] Uses core artifact types (not custom structs)
- [ ] `ToolUsageRepository` records executions
- [ ] Registered in `services/mcp/{name}.yaml`
- [ ] `cargo clippy -p {crate} -- -D warnings` passes

## Quick Reference

| Task | Command |
|------|---------|
| Build all MCP | `systemprompt build mcp` |
| Build single | `cargo build -p systemprompt-mcp-{name}` |
| Build release | `systemprompt build mcp --release` |
| Check status | `systemprompt plugins mcp status` |
| List tools | `systemprompt plugins mcp tools` |
| Call tool | `systemprompt plugins mcp call {server} {tool} --args '{json}'` |
| Lint | `cargo clippy -p systemprompt-mcp-{name} -- -D warnings` |
| Format | `cargo fmt -p systemprompt-mcp-{name} -- --check` |

## Reference Implementations

| Concept | Location |
|---------|----------|
| MCP server | `extensions/mcp/systemprompt/` |
| MCP with AI | `extensions/mcp/content-manager/` |
| Tools | `extensions/mcp/systemprompt/src/tools/` |
| Server constructor | `extensions/mcp/systemprompt/src/server/` |
