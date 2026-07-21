# Java Spring Project Blueprint

## Purpose

Use this blueprint when creating or modernizing a Java Spring Boot service. It captures current production-minded defaults while leaving room for existing repository conventions.

## Research Baseline

As of July 2026, the current Spring Boot reference documentation identifies Spring Boot 4.1.0 as stable. It requires Java 17 or later, supports Java 26, and explicitly supports Maven 3.6.3+ and Gradle 8.14+/9.x. For greenfield services in this repository, default to Java 21 and Maven because they are conservative, common production choices; allow the user or existing repo to override them.

Spring Boot 4's getting-started documentation uses `spring-boot-starter-webmvc` for servlet MVC applications. `spring-boot-starter-web` still exists but is documented as deprecated in favor of `spring-boot-starter-webmvc`, so new scaffolds should use `webmvc`.

## Discovery First

Before writing files, classify the target directory:

- Greenfield: empty directory or explicit request for a new Java/Spring service.
- Existing project: `pom.xml`, Gradle build files, Java sources, tests, Docker/Compose, CI, migration files, or git history already exist.

For existing projects, inspect and summarize:

- Build tool: Maven, Gradle Groovy DSL, Gradle Kotlin DSL, wrapper files, parent POMs, BOMs, plugins, Java release, packaging.
- Spring versions: Boot, Framework, Cloud, Security, Data, Modulith, Batch, or other release trains.
- Entrypoint and package layout: root application class, default package mistakes, component scan boundaries.
- API contracts: paths, methods, status codes, media types, response fields and field types, validation behavior, error shape, headers, and auth requirements.
- Configuration: `application.yml`, profile files, environment variables, secrets, config server, Vault, Kubernetes config, Docker env, or CI variables.
- Data layer: datasource, JPA/JDBC/R2DBC, migrations, transaction boundaries, schema generation, test database strategy.
- Observability: Actuator, exposed endpoints, metrics registry, tracing, logging format, correlation IDs, health/readiness/liveness probes.
- Security: resource server/client/session/basic/custom filters, CORS, CSRF, endpoint authorization, method security, tests.
- Local and deployment commands: IDE run configs, `mvn spring-boot:run`, Gradle tasks, Docker, Compose, Kubernetes, Procfile, systemd, CI.

Modernize by filling gaps rather than replacing working pieces.

## Greenfield Defaults

Use these defaults unless the user says otherwise:

- Java 21, Maven, Spring Boot 4.1.0, jar packaging.
- `spring-boot-starter-webmvc`, `spring-boot-starter-validation`, `spring-boot-starter-actuator`.
- `spring-boot-starter-test` plus `spring-boot-starter-webmvc-test`.
- Root package based on `groupId` plus sanitized project name, such as `com.example.inventoryservice`.
- `@SpringBootApplication` plus `@ConfigurationPropertiesScan` in the root package.
- `@ConfigurationProperties` for app-owned settings.
- `application.yml`, `application-local.yml`, `application-prod.yml`, and `.env.example`.
- Actuator exposure limited to `health,info`; add `prometheus` only when requested.
- Graceful shutdown and health probes.
- One small example REST controller showing validation and JSON behavior.
- `@RestControllerAdvice` that returns RFC 9457-style `ProblemDetail` responses for validation errors.
- `@SpringBootTest` context test and MockMvc API test.

## Package Layout

Spring Boot does not require a specific layout, but it recommends avoiding the default package, using reverse-domain package names, and placing the main application class in a root package above components.

Start simple:

```text
com.example.inventoryservice
  InventoryServiceApplication
  api
  config
  service
```

When real domains appear, prefer package-by-feature:

```text
com.example.inventoryservice
  InventoryServiceApplication
  ordering
    OrderController
    OrderService
    OrderRepository
    Order
  catalog
    ProductController
    ProductService
```

Avoid premature `controller/service/repository` mega-packages once the project has multiple domains.

## Configuration

Use environment-owned configuration:

- Keep common defaults in `application.yml`.
- Put local-only debug behavior in `application-local.yml`.
- Put production logging and strict health visibility in `application-prod.yml`.
- Do not hard-code secrets in profile files.
- Provide `.env.example` with variables such as `SPRING_PROFILES_ACTIVE`, `APP_GREETING_PREFIX`, and database placeholders when needed.
- Use `@ConfigurationProperties(prefix = "app")` with validation annotations for app settings.

Do not put `spring.profiles.active` inside profile-specific documents. Let environment variables, command-line args, IDE run configs, Compose, or deployment manifests activate profiles.

## API Design

For REST scaffolds:

- Use JSON explicitly with `produces = MediaType.APPLICATION_JSON_VALUE`.
- Use `@Valid` request records/classes and Jakarta Validation constraints.
- Return appropriate HTTP status codes, not always `200`.
- Use `ProblemDetail` for validation and domain errors instead of ad hoc string errors.
- Keep controllers thin; put simple business behavior in service classes.
- Keep sample endpoints obviously replaceable.

## Security

Do not add security just to look production-grade. A misleading auth scaffold is worse than no auth.

When the user asks for security:

- Identify whether the service is a stateless OAuth2 resource server, OAuth2 client, form-login/session app, internal service, or something else.
- For APIs protected by an identity provider, prefer Spring Security OAuth2 Resource Server with JWT issuer configuration.
- Permit health/readiness endpoints deliberately and secure sensitive Actuator endpoints.
- Configure CORS only for known browser origins.
- Keep CSRF enabled for browser/session apps; disable it only for stateless token APIs with a clear reason.
- Add security tests that prove public and protected endpoints behave as intended.

## Data

Add a database only when the user asks or the existing project already has one.

For PostgreSQL greenfield services:

- Add `spring-boot-starter-data-jpa`, PostgreSQL JDBC driver, Flyway, and PostgreSQL-specific Flyway support when required by the managed version.
- Set `spring.jpa.hibernate.ddl-auto=validate`; use Flyway for schema changes.
- Do not mix `schema.sql`/`data.sql` initialization with Flyway or Liquibase.
- Generate `src/main/resources/db/migration/V1__init.sql` as the first migration.
- Use Testcontainers and Spring Boot `@ServiceConnection` for integration tests.
- In Compose, expose Postgres for local development and pass datasource variables to the app.

## Observability

Baseline production controls:

- Include Actuator for production features.
- Expose only `health` and `info` over HTTP by default.
- Enable liveness/readiness health probes.
- Add `micrometer-registry-prometheus` and expose `prometheus` only when the user asks for Prometheus scraping.
- Use Spring Boot structured logging in `prod` when supported by the chosen Boot version.
- If tracing is requested, prefer Micrometer Tracing with OpenTelemetry and document required exporter/env settings.

## Docker

Only generate Docker/Compose when requested or already present.

For generated Dockerfiles:

- Build with Maven in a builder stage.
- Run the fat jar on an Eclipse Temurin JRE image.
- Use `java -jar`.
- Expose the app port.
- Add a health check against `/actuator/health`.
- Avoid baking secrets into the image.

For Compose:

- Add the app service when Docker is requested.
- Add PostgreSQL only when `--database postgres` is selected.
- Keep env values local and replaceable.

## Validation

Use the strongest available checks:

```bash
mvn test
mvn spring-boot:run
curl -fsS http://127.0.0.1:8080/actuator/health
```

For PostgreSQL projects:

```bash
docker compose up -d postgres
mvn test
docker compose down
```

For Docker projects:

```bash
docker compose up --build
curl -fsS http://127.0.0.1:8080/actuator/health
```

Report skipped checks exactly when Java, Maven, Docker, or dependency downloads are unavailable.

## Source Notes

- Spring Boot reference: system requirements, build systems, code structure, externalized configuration, profiles, logging, graceful shutdown, Actuator endpoints, observability, metrics, tracing, SQL databases, database initialization, testing, Testcontainers, and Maven plugin integration tests.
- Spring Initializr reference: project generation metadata, Maven/Gradle project types, dependency IDs, and generated-project conventions.
- Spring Security reference: Boot security auto-configuration, OAuth2 resource server, JWT issuer configuration, CSRF/CORS considerations.
- OWASP REST and Java Security cheat sheets: HTTPS, content-type handling, semantic status codes, CORS specificity, avoiding secrets in URLs, structured logging, and log injection prevention.
