---
name: java-spring-setup
description: Create, standardize, or modernize production-minded Java Spring Boot services and APIs with Maven, Spring Boot 4.x or compatible existing versions, Web MVC REST controllers, typed configuration properties, validation, Actuator health/metrics, structured logging profiles, tests, optional PostgreSQL/Flyway/Testcontainers, optional Docker/Compose, and conservative existing-project migration. Use whenever the user asks to scaffold a Java API, Spring Boot service, Spring MVC REST app, enterprise Java backend, production Spring project, Actuator/observability setup, database-backed Spring service, or modernization of an existing Spring repository. Prefer python-fastapi-setup for Python FastAPI services and cpp-project-setup for non-Spring C++ projects.
---

# Java Spring Setup

## Overview

Create or modernize Spring Boot services around a repeatable service pipeline:

```text
Maven -> Spring Boot -> Web MVC REST -> configuration -> validation -> Actuator -> tests -> deployment
```

Keep the scaffold boring in the productive way: explicit build metadata, root-package application class, typed settings, a small API slice, validation and error handling, production health/metrics endpoints, and tests that can run without external infrastructure unless the user explicitly asks for database-backed behavior.

## Workflow

1. Classify the target directory before writing files.
   - Treat it as greenfield if it is empty or the user clearly asks for a new Spring service.
   - Treat it as existing if it has `pom.xml`, `build.gradle`, `settings.gradle`, `src/main/java`, `src/test/java`, Docker files, CI, or git history.
   - For existing projects, inventory the current Boot version, Java version, build tool, package layout, endpoint contracts, configuration files, tests, database migrations, security model, Actuator exposure, Docker/CI, and local run commands before editing.

2. For greenfield scaffolds, default to Maven, Java 21, Spring Boot 4.1.0, jar packaging, Web MVC, validation, Actuator, structured production logging, and MockMvc tests.
   - Run from this skill directory:

```bash
python3 scripts/scaffold_java_spring_project.py \
  --name inventory-service \
  --out /path/to/workspace/inventory-service \
  --group-id com.example
```

   - Add `--with-docker` when the user wants a Dockerfile or Compose.
   - Add `--database postgres` when the user wants PostgreSQL, Flyway migrations, database configuration, Compose Postgres, and Testcontainers integration tests.
   - Add `--with-prometheus` when the service should expose `/actuator/prometheus`.
   - Read `references/java-spring-blueprint.md` before changing generated files or adding script options.

3. For existing projects, patch conservatively.
   - Preserve the current build tool unless the user asks to switch.
   - Preserve working endpoint paths, status codes, payload shapes, error formats, headers, and authentication behavior.
   - Add regression tests around endpoints before or during route/package moves.
   - Upgrade Boot or Java only when requested or when the current versions block the requested work.
   - Do not add a fake authentication system. If security is needed, identify whether the app should be an OAuth2 resource server, OAuth2 client, session app, or internal service first.

4. Keep package structure Spring-friendly.
   - Avoid the Java default package.
   - Put the `@SpringBootApplication` class in the root package above the app's controllers, services, repositories, entities, and config.
   - For greenfield services, prefer package-by-feature once real domains appear; keep placeholder/sample code small.

5. Keep configuration explicit and environment-owned.
   - Use `@ConfigurationProperties` records/classes for application settings.
   - Keep safe defaults in `application.yml`.
   - Use profile files such as `application-local.yml` and `application-prod.yml` for behavior differences.
   - Keep `.env.example` to placeholders and local defaults only; never commit secrets.

6. Add production controls without overexposing internals.
   - Include `spring-boot-starter-actuator`.
   - Expose only `health` and `info` by default; add `prometheus` only when requested.
   - Enable health probes and graceful shutdown settings.
   - Use structured JSON logging in the production profile when using current Spring Boot support.

7. Add tests and validation.
   - Add at least one context-load test and one web/API test.
   - Keep the default scaffold tests free of database, Docker, cloud, and network dependencies.
   - If PostgreSQL is requested, use Flyway and Testcontainers with Spring Boot service connections; report clearly that Docker is required for those integration tests.

## Default Structure

Prefer this layout for new services:

```text
src/
  main/
    java/com/example/service/
      InventoryServiceApplication.java
      api/
        ApiExceptionHandler.java
        GreetingController.java
        GreetingRequest.java
        GreetingResponse.java
      config/
        AppProperties.java
      service/
        GreetingService.java
    resources/
      application.yml
      application-local.yml
      application-prod.yml
  test/
    java/com/example/service/
      InventoryServiceApplicationTests.java
      api/GreetingControllerTest.java
pom.xml
.env.example
.editorconfig
.gitignore
README.md
```

Add `Dockerfile`, `.dockerignore`, `compose.yml`, `.github/workflows/ci.yml`, `db/migration/`, repositories, entities, or security config only when requested or already part of the service.

## Validation

Run the strongest available checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile skills/java-spring-setup/scripts/scaffold_java_spring_project.py
python3 skills/java-spring-setup/scripts/scaffold_java_spring_project.py --help

rm -rf /tmp/codex-skill-smoke/smoke_spring
python3 skills/java-spring-setup/scripts/scaffold_java_spring_project.py \
  --name smoke-spring \
  --out /tmp/codex-skill-smoke/smoke_spring

cd /tmp/codex-skill-smoke/smoke_spring
mvn test
mvn spring-boot:run
curl -fsS http://127.0.0.1:8080/actuator/health
```

For Docker:

```bash
docker compose up --build
curl -fsS http://127.0.0.1:8080/actuator/health
```

For PostgreSQL scaffolds, Docker is needed for Compose and Testcontainers. If Java, Maven, Docker, or network access for Maven dependencies is unavailable, report the exact command that could not run and why.

## References

- Read `references/java-spring-blueprint.md` when choosing Boot versions, dependency defaults, package layout, configuration, Actuator exposure, database migration, testing, Docker, or existing-project modernization details.
- Read the scaffold script before changing generated files, dependency lists, or generated command entry points.
