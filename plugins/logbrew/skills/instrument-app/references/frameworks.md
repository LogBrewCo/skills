# Framework setup

The snippets below come from the README of each LogBrew SDK package. Each
package README has the full options, privacy limits, and recovery steps.
Read it before you change defaults. All packages are in
[LogBrewCo/sdk](https://github.com/LogBrewCo/sdk).

Install only the packages that the app needs: the core package for the
runtime, then the framework package. Use the package manager that the app
already uses. `logbrew setup --json` prints the install command for the
detected project in `install_plan.install_command`. The
[SDK guide](https://docs.logbrew.co/guides/sdk-ingestion#package-manager-installs)
shows the install command for each package manager.

## Packages

| Runtime or framework | Packages | Package README |
| --- | --- | --- |
| Node.js | `@logbrew/sdk`, `@logbrew/node` from npm | [`@logbrew/node`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-node) |
| Express | `@logbrew/sdk`, `@logbrew/node`, `@logbrew/express` from npm, with `express` | [`@logbrew/express`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-express) |
| Fastify | `@logbrew/sdk`, `@logbrew/node`, `@logbrew/fastify` from npm, with `fastify` | [`@logbrew/fastify`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-fastify) |
| NestJS | `@logbrew/sdk`, `@logbrew/node`, `@logbrew/nestjs` from npm, with `@nestjs/common`, `@nestjs/core`, `@nestjs/platform-express`, `reflect-metadata`, `rxjs` | [`@logbrew/nestjs`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-nestjs) |
| Next.js | `@logbrew/sdk`, `@logbrew/node`, `@logbrew/next` from npm, with `next`, `react`, `react-dom` | [`@logbrew/next`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-next) |
| React | `@logbrew/sdk`, `@logbrew/react` from npm, with `react` | [`@logbrew/react`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-react) |
| Browser | `@logbrew/sdk`, `@logbrew/browser` from npm | [`@logbrew/browser`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-browser) |
| Vue | `@logbrew/sdk`, `@logbrew/vue` from npm | [`@logbrew/vue`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-vue) |
| Angular | `@logbrew/sdk`, `@logbrew/angular` from npm | [`@logbrew/angular`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-angular) |
| Svelte and SvelteKit | `@logbrew/sdk`, `@logbrew/browser`, `@logbrew/svelte` from npm | [`@logbrew/svelte`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-svelte) |
| React Native | `@logbrew/sdk`, `@logbrew/react-native` from npm | [`@logbrew/react-native`](https://github.com/LogBrewCo/sdk/tree/main/js/logbrew-react-native) |
| Python | `logbrew-sdk` from PyPI | [`logbrew-sdk`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_py) |
| FastAPI | `logbrew-fastapi` from PyPI | [`logbrew-fastapi`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_fastapi) |
| Django | `logbrew-sdk`, `logbrew-django` from PyPI | [`logbrew-django`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_django) |
| Flask | `logbrew-sdk`, `logbrew-flask` from PyPI | [`logbrew-flask`](https://github.com/LogBrewCo/sdk/tree/main/python/logbrew_flask) |
| Go | Go module `github.com/LogBrewCo/sdk/go/logbrew` | [`go/logbrew`](https://github.com/LogBrewCo/sdk/tree/main/go/logbrew) |
| Gin | Go module `github.com/LogBrewCo/sdk/go/logbrew/gin` | [`go/logbrew/gin`](https://github.com/LogBrewCo/sdk/tree/main/go/logbrew/gin) |
| Ruby and Rails | `logbrew-sdk` gem in the Gemfile | [`logbrew-sdk`](https://github.com/LogBrewCo/sdk/tree/main/ruby/logbrew-ruby) |
| PHP, Laravel, Symfony | `logbrew/sdk` from Packagist | [`logbrew/sdk`](https://github.com/LogBrewCo/sdk/tree/main/php/logbrew-php) |
| Rust | `logbrew` crate with the `http` feature | [`logbrew`](https://github.com/LogBrewCo/sdk/tree/main/rust/logbrew) |
| Java and Spring | `co.logbrew:logbrew-sdk` from Maven Central | [`logbrew-java`](https://github.com/LogBrewCo/sdk/tree/main/java/logbrew-java) |
| Kotlin and Android | `co.logbrew:logbrew-kotlin` from Maven Central | [`logbrew-kotlin`](https://github.com/LogBrewCo/sdk/tree/main/kotlin/logbrew-kotlin) |
| .NET | `LogBrew` from NuGet | [`LogBrew`](https://github.com/LogBrewCo/sdk/tree/main/dotnet/logbrew-dotnet) |
| ASP.NET Core | `LogBrew.AspNetCore` from NuGet | [`LogBrew.AspNetCore`](https://github.com/LogBrewCo/sdk/tree/main/dotnet/logbrew-dotnet/src/LogBrew.AspNetCore) |
| Swift and Apple apps | Add `https://github.com/LogBrewCo/sdk.git` with SwiftPM and use the `LogBrew` product | [`logbrew-swift`](https://github.com/LogBrewCo/sdk/tree/main/swift/logbrew-swift) |
| Unity | `co.logbrew.unity` from OpenUPM | [`logbrew-unity`](https://github.com/LogBrewCo/sdk/tree/main/unity/logbrew-unity) |
| C | Source and header client | [`logbrew-c`](https://github.com/LogBrewCo/sdk/tree/main/c/logbrew-c) |
| C++ | CMake `FetchContent`; `logbrew setup --json` prints the block | [`logbrew-cpp`](https://github.com/LogBrewCo/sdk/tree/main/cpp/logbrew-cpp) |

## Express

```js
import express from "express";
import { logbrewMiddleware } from "@logbrew/express";

const app = express();
const logbrewServerApiKey = process.env.LOGBREW_SERVER_API_KEY;

if (logbrewServerApiKey) {
  app.use(logbrewMiddleware({
    serverApiKey: logbrewServerApiKey,
    onCaptureError(error) {
      console.error("LogBrew request capture failed", error);
    }
  }));
}
```

Register the error handler after the routes and before the app's own error
response handler:

```js
import { logbrewErrorHandler } from "@logbrew/express";

if (logbrewServerApiKey) {
  app.use(logbrewErrorHandler({
    serverApiKey: logbrewServerApiKey,
    onCaptureError(error) {
      console.error("LogBrew error capture failed", error);
    }
  }));
}
```

## Next.js (App Router)

```ts
// instrumentation.ts
import { createLogBrewNextRequestErrorHandler } from "@logbrew/next/instrumentation";

export const onRequestError = createLogBrewNextRequestErrorHandler({
  serverApiKey: process.env.LOGBREW_SERVER_API_KEY,
  onCaptureError(error) {
    console.error("LogBrew request-error capture failed", error);
  }
});
```

Issues get the release and environment from `LOGBREW_RELEASE` and
`LOGBREW_ENVIRONMENT`, or from `VERCEL_GIT_COMMIT_SHA` and `VERCEL_ENV`.
`LOGBREW_SERVICE_NAME` sets the service.

## React

Use a key of kind `browser` in `clientKey`.

```js
import React from "react";
import {
  LogBrewErrorBoundary,
  LogBrewProvider,
  createLogBrewReactClient
} from "@logbrew/react";

const client = createLogBrewReactClient({
  clientKey: "LOGBREW_CLIENT_KEY"
});

export function App() {
  return React.createElement(
    LogBrewProvider,
    { client },
    React.createElement(
      LogBrewErrorBoundary,
      {
        fallback: ({ error, resetError }) => React.createElement(
          "button",
          { onClick: resetError },
          `Retry after ${error instanceof Error ? error.message : "React error"}`
        ),
        metadata: { section: "checkout" },
        onError: (_error, _info, event) => {
          console.info("captured LogBrew issue", event.id);
        }
      },
      React.createElement(CheckoutButton)
    )
  );
}
```

## FastAPI

```python
import logging
import os

from fastapi import FastAPI
from logbrew_fastapi import init_logbrew

app = FastAPI()
logbrew = init_logbrew(
    app,
    api_key=os.environ["LOGBREW_API_KEY"],
    service_name="checkout-api",
)
client = logbrew.client
logger = logging.getLogger("checkout-api")
logger.addHandler(logbrew.logging_handler)
```

`environment` defaults to `LOGBREW_ENVIRONMENT`, then `production`. The
release comes from `LOGBREW_RELEASE` when it is set.

## Django

```python
# settings.py
MIDDLEWARE = [
    "logbrew_django.LogBrewDjangoMiddleware",
    *MIDDLEWARE,
]
```

```python
# app startup code, for example at the end of settings.py
import logging
import os

from logbrew_django import configure_logbrew, get_active_logbrew_trace
from logbrew_sdk import HttpTransport, LogBrewClient, LogBrewLoggingHandler

client = LogBrewClient.create(
    api_key=os.environ["LOGBREW_SERVER_API_KEY"],
)
logger = logging.getLogger("checkout-api")
logger.addHandler(LogBrewLoggingHandler(client, metadata={"service": "checkout-api"}))
configure_logbrew(client=client, transport=HttpTransport(), service_name="checkout-api")
```

Set `LOGBREW_ENVIRONMENT` and `LOGBREW_RELEASE` in the app's environment.

## Flask

```python
from flask import Flask
from logbrew_flask import init_logbrew

app = Flask(__name__)
logbrew = init_logbrew(app)
client = logbrew.client
```

The initializer reads `LOGBREW_SERVER_API_KEY`, `LOGBREW_SERVICE_NAME`,
`LOGBREW_ENVIRONMENT`, and `LOGBREW_RELEASE`.

## Gin

Catch `SIGTERM` so that queued events are sent when the host stops the
service. Go does not run deferred calls when a signal ends the process.

```go
package main

import (
  "context"
  "errors"
  "net/http"
  "os"
  "os/signal"
  "syscall"
  "time"

  "github.com/LogBrewCo/sdk/go/logbrew"
  logbrewgin "github.com/LogBrewCo/sdk/go/logbrew/gin"
  "github.com/gin-gonic/gin"
)

func main() {
  ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
  defer stop()

  transport, err := logbrew.NewHTTPTransport(logbrew.HTTPTransportConfig{})
  must(err)
  client, err := logbrew.NewAutomaticClient(logbrew.Config{
    APIKey: os.Getenv("LOGBREW_SERVER_API_KEY"),
  }, logbrew.AutomaticDeliveryConfig{
    Transport: transport,
  })
  must(err)

  middleware, err := logbrewgin.NewMiddleware(logbrewgin.Config{
    Client:                   client,
    CaptureRequestMetrics:   true,
    CaptureServerErrorIssues: true,
    Metadata: map[string]any{
      "service":     "checkout-api",
      "environment": "production",
    },
  })
  must(err)

  router := gin.New()
  router.Use(gin.Recovery(), middleware)

  server := &http.Server{Addr: ":8080", Handler: router}
  go func() {
    if err := server.ListenAndServe(); !errors.Is(err, http.ErrServerClosed) {
      panic(err)
    }
  }()

  <-ctx.Done()
  stop()
  shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
  defer cancel()
  serverErr := server.Shutdown(shutdownCtx)
  _, err = client.Shutdown(nil)
  must(errors.Join(serverErr, err))
}

func must(err error) {
  if err != nil {
    panic(err)
  }
}
```

## Rails

```ruby
# Gemfile
gem "logbrew-sdk", "~> 0.1.17"
```

```bash
bundle install
export LOGBREW_SERVER_API_KEY="your project-scoped server ingest key"
bin/rails server
```

No initializer is needed. Without `LOGBREW_SERVER_API_KEY`, the integration
stays off. `LOGBREW_SERVICE_NAME`, `LOGBREW_ENVIRONMENT`, and
`LOGBREW_RELEASE` set the service, environment, and release.

## ASP.NET Core

Set `LOGBREW_SERVER_API_KEY`, `LOGBREW_SERVICE_NAME`,
`LOGBREW_ENVIRONMENT`, and `LOGBREW_RELEASE` outside source control. Place
the middleware after routing:

```csharp
using LogBrew;

var builder = WebApplication.CreateBuilder(args);
builder.AddLogBrew();

var app = builder.Build();
app.UseRouting();
app.UseLogBrew();
app.MapGet("/", () => "ok");
app.Run();
```

## Other runtimes

Open the package README from the table. It shows the install and setup
code, and most READMEs have a "Read Events Back" section. Use the HTTP
transport of the released package; a recording or preview transport sends
nothing.
