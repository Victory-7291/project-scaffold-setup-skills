#!/usr/bin/env python3
"""Scaffold a production-minded Java Spring Boot service project."""

from __future__ import annotations

import argparse
import re
import stat
import textwrap
from pathlib import Path


DEFAULT_BOOT_VERSION = "4.1.0"
DEFAULT_JAVA_VERSION = "21"


def kebab_name(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-").lower()
    if not name:
        raise ValueError("project name must contain at least one letter or digit")
    if name[0].isdigit():
        name = f"service-{name}"
    return name


def java_package_part(value: str) -> str:
    part = re.sub(r"[^a-z0-9]+", "", value.lower())
    if not part:
        return "service"
    if part[0].isdigit():
        return f"service{part}"
    return part


def package_name(group_id: str, project_name: str, override: str | None) -> str:
    if override:
        package = override.strip()
    else:
        package = f"{group_id.strip()}.{java_package_part(project_name)}"
    parts = [p for p in package.split(".") if p]
    if not parts:
        raise ValueError("package name must contain at least one package part")
    cleaned = [java_package_part(part) for part in parts]
    return ".".join(cleaned)


def class_prefix(value: str) -> str:
    words = [part for part in re.split(r"[^A-Za-z0-9]+", value.strip()) if part]
    prefix = "".join(word[:1].upper() + word[1:] for word in words)
    if not prefix:
        prefix = "SpringService"
    if prefix[0].isdigit():
        prefix = f"Service{prefix}"
    return prefix


def title_name(value: str) -> str:
    words = [part for part in re.split(r"[^A-Za-z0-9]+", value.strip()) if part]
    return " ".join(word[:1].upper() + word[1:] for word in words) or "Spring Service"


def render(template: str, **values: str) -> str:
    result = textwrap.dedent(template).lstrip("\n")
    for key, value in values.items():
        result = result.replace(f"@{key}@", value)
    return result


def write_file(root: Path, relative: str, content: str, *, executable: bool = False, force: bool = False) -> None:
    path = root / relative
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists; rerun with --force to overwrite scaffold-owned files")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def xml_dependency(group_id: str, artifact_id: str, scope: str | None = None) -> str:
    scope_block = f"\n    <scope>{scope}</scope>" if scope else ""
    return render(
        """
        <dependency>
            <groupId>@GROUP_ID@</groupId>
            <artifactId>@ARTIFACT_ID@</artifactId>@SCOPE@
        </dependency>
        """,
        GROUP_ID=group_id,
        ARTIFACT_ID=artifact_id,
        SCOPE=scope_block,
    ).rstrip()


def indent_block(block: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in block.splitlines())


def database_dependencies(database: str) -> str:
    if database != "postgres":
        return ""
    deps = [
        xml_dependency("org.springframework.boot", "spring-boot-starter-data-jpa"),
        xml_dependency("org.postgresql", "postgresql", "runtime"),
        xml_dependency("org.flywaydb", "flyway-core"),
        xml_dependency("org.flywaydb", "flyway-database-postgresql"),
    ]
    return "\n\n" + "\n\n".join(indent_block(dep, 8) for dep in deps)


def database_test_dependencies(database: str) -> str:
    if database != "postgres":
        return ""
    deps = [
        xml_dependency("org.springframework.boot", "spring-boot-testcontainers", "test"),
        xml_dependency("org.testcontainers", "postgresql", "test"),
    ]
    return "\n\n" + "\n\n".join(indent_block(dep, 8) for dep in deps)


def prometheus_dependency(enabled: bool) -> str:
    if not enabled:
        return ""
    return "\n\n" + indent_block(xml_dependency("io.micrometer", "micrometer-registry-prometheus", "runtime"), 8)


def application_database_yaml(database: str, artifact_id: str) -> str:
    if database != "postgres":
        return ""
    db_name = java_package_part(artifact_id).replace("-", "_") or "app"
    block = render(
        """
        datasource:
          url: ${JDBC_DATABASE_URL:jdbc:postgresql://localhost:5432/@DB_NAME@}
          username: ${JDBC_DATABASE_USERNAME:@DB_NAME@}
          password: ${JDBC_DATABASE_PASSWORD:@DB_NAME@}
        jpa:
          hibernate:
            ddl-auto: validate
          open-in-view: false
        flyway:
          enabled: true
        """,
        DB_NAME=db_name,
    ).rstrip()
    return indent_block(block, 2)


def env_database(database: str, artifact_id: str) -> str:
    if database != "postgres":
        return ""
    db_name = java_package_part(artifact_id).replace("-", "_") or "app"
    return render(
        """
        JDBC_DATABASE_URL=jdbc:postgresql://localhost:5432/@DB_NAME@
        JDBC_DATABASE_USERNAME=@DB_NAME@
        JDBC_DATABASE_PASSWORD=@DB_NAME@
        """,
        DB_NAME=db_name,
    ).rstrip()


def compose_database(database: str, artifact_id: str) -> tuple[str, str, str]:
    if database != "postgres":
        return "", "", ""
    db_name = java_package_part(artifact_id).replace("-", "_") or "app"
    env = indent_block(
        render(
            """
            JDBC_DATABASE_URL: jdbc:postgresql://postgres:5432/@DB_NAME@
            JDBC_DATABASE_USERNAME: @DB_NAME@
            JDBC_DATABASE_PASSWORD: @DB_NAME@
            """,
            DB_NAME=db_name,
        ).rstrip(),
        6,
    )
    depends = indent_block(
        """
depends_on:
  postgres:
    condition: service_healthy
""".rstrip(),
        4,
    )
    service = "\n" + indent_block(
        render(
            """
            postgres:
              image: postgres:17-alpine
              environment:
                POSTGRES_DB: @DB_NAME@
                POSTGRES_USER: @DB_NAME@
                POSTGRES_PASSWORD: @DB_NAME@
              ports:
                - "5432:5432"
              healthcheck:
                test: ["CMD-SHELL", "pg_isready -U @DB_NAME@ -d @DB_NAME@"]
                interval: 10s
                timeout: 5s
                retries: 5
              volumes:
                - postgres-data:/var/lib/postgresql/data
            """,
            DB_NAME=db_name,
        ).rstrip(),
        2,
    ) + "\n\nvolumes:\n  postgres-data:"
    return env, depends, service


def testcontainers_config(package: str, class_name: str, database: str) -> tuple[str, str, str]:
    if database != "postgres":
        return "", "", ""
    imports = f"import {package}.support.PostgresTestConfiguration;\nimport org.springframework.context.annotation.Import;"
    annotation = "@Import(PostgresTestConfiguration.class)"
    source = render(
        """
        package @PACKAGE@.support;

        import org.springframework.boot.test.context.TestConfiguration;
        import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
        import org.springframework.context.annotation.Bean;
        import org.testcontainers.containers.PostgreSQLContainer;

        @TestConfiguration(proxyBeanMethods = false)
        public class PostgresTestConfiguration {

            @Bean
            @ServiceConnection
            PostgreSQLContainer<?> postgresContainer() {
                return new PostgreSQLContainer<>("postgres:17-alpine");
            }
        }
        """,
        PACKAGE=package,
        CLASS_NAME=class_name,
    )
    return imports, annotation, source


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a standard Java Spring Boot service scaffold.")
    parser.add_argument("--name", required=True, help="Project/service name, for example inventory-service")
    parser.add_argument("--out", help="Output directory. Defaults to ./<artifact-id>.")
    parser.add_argument("--group-id", default="com.example", help="Maven groupId. Defaults to com.example.")
    parser.add_argument("--package-name", help="Java root package. Defaults to <group-id>.<sanitized-name>.")
    parser.add_argument("--java-version", default=DEFAULT_JAVA_VERSION, help="Java release. Defaults to 21.")
    parser.add_argument("--spring-boot-version", default=DEFAULT_BOOT_VERSION, help="Spring Boot version. Defaults to 4.1.0.")
    parser.add_argument("--port", default="8080", help="HTTP port used in docs, config, and Compose.")
    parser.add_argument("--database", choices=["none", "postgres"], default="none", help="Optional database scaffold.")
    parser.add_argument("--with-docker", action="store_true", help="Add Dockerfile, .dockerignore, and compose.yml.")
    parser.add_argument("--with-prometheus", action="store_true", help="Add Prometheus registry and expose /actuator/prometheus.")
    parser.add_argument("--with-github-actions", action="store_true", help="Add a simple Maven CI workflow.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-owned files if they already exist.")
    args = parser.parse_args()

    artifact_id = kebab_name(args.name)
    package = package_name(args.group_id, args.name, args.package_name)
    package_dir = package.replace(".", "/")
    prefix = class_prefix(args.name)
    app_class = f"{prefix}Application"
    title = title_name(args.name)
    root = Path(args.out) if args.out else Path.cwd() / artifact_id
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    exposure = "health,info,prometheus" if args.with_prometheus else "health,info"
    db_yaml = application_database_yaml(args.database, artifact_id)
    db_env = env_database(args.database, artifact_id)
    compose_db_env, compose_depends, compose_db_service = compose_database(args.database, artifact_id)
    tc_import, tc_annotation, tc_source = testcontainers_config(package, app_class, args.database)

    values = {
        "ARTIFACT_ID": artifact_id,
        "GROUP_ID": args.group_id,
        "PACKAGE": package,
        "PACKAGE_DIR": package_dir,
        "APP_CLASS": app_class,
        "TITLE": title,
        "JAVA_VERSION": args.java_version,
        "SPRING_BOOT_VERSION": args.spring_boot_version,
        "PORT": str(args.port),
        "ACTUATOR_EXPOSURE": exposure,
        "PROMETHEUS_DEPENDENCY": prometheus_dependency(args.with_prometheus),
        "DATABASE_DEPENDENCIES": database_dependencies(args.database),
        "DATABASE_TEST_DEPENDENCIES": database_test_dependencies(args.database),
        "DATABASE_YAML": db_yaml,
        "DATABASE_ENV": db_env,
        "COMPOSE_DATABASE_ENV": compose_db_env,
        "COMPOSE_DEPENDS": compose_depends,
        "COMPOSE_DATABASE_SERVICE": compose_db_service,
        "TESTCONTAINERS_IMPORT": tc_import,
        "TESTCONTAINERS_ANNOTATION": tc_annotation,
        "DATABASE_NOTE": " PostgreSQL integration tests require Docker." if args.database == "postgres" else "",
        "PROMETHEUS_NOTE": " Prometheus metrics are available at `/actuator/prometheus`." if args.with_prometheus else "",
    }

    java_root = f"src/main/java/{package_dir}"
    test_root = f"src/test/java/{package_dir}"
    files: dict[str, tuple[str, bool]] = {
        "pom.xml": (
            render(
                """
                <?xml version="1.0" encoding="UTF-8"?>
                <project xmlns="http://maven.apache.org/POM/4.0.0"
                         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
                    <modelVersion>4.0.0</modelVersion>

                    <parent>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter-parent</artifactId>
                        <version>@SPRING_BOOT_VERSION@</version>
                        <relativePath/>
                    </parent>

                    <groupId>@GROUP_ID@</groupId>
                    <artifactId>@ARTIFACT_ID@</artifactId>
                    <version>0.1.0-SNAPSHOT</version>
                    <name>@TITLE@</name>
                    <description>Production-minded Spring Boot service scaffold</description>
                    <packaging>jar</packaging>

                    <properties>
                        <java.version>@JAVA_VERSION@</java.version>
                        <maven.compiler.release>@JAVA_VERSION@</maven.compiler.release>
                    </properties>

                    <dependencies>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-webmvc</artifactId>
                        </dependency>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-validation</artifactId>
                        </dependency>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-actuator</artifactId>
                        </dependency>@PROMETHEUS_DEPENDENCY@@DATABASE_DEPENDENCIES@

                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-test</artifactId>
                            <scope>test</scope>
                        </dependency>
                        <dependency>
                            <groupId>org.springframework.boot</groupId>
                            <artifactId>spring-boot-starter-webmvc-test</artifactId>
                            <scope>test</scope>
                        </dependency>@DATABASE_TEST_DEPENDENCIES@
                    </dependencies>

                    <build>
                        <plugins>
                            <plugin>
                                <groupId>org.springframework.boot</groupId>
                                <artifactId>spring-boot-maven-plugin</artifactId>
                            </plugin>
                            <plugin>
                                <groupId>org.apache.maven.plugins</groupId>
                                <artifactId>maven-enforcer-plugin</artifactId>
                                <version>3.5.0</version>
                                <executions>
                                    <execution>
                                        <id>enforce-java-and-maven</id>
                                        <goals>
                                            <goal>enforce</goal>
                                        </goals>
                                        <configuration>
                                            <rules>
                                                <requireJavaVersion>
                                                    <version>[@JAVA_VERSION@,)</version>
                                                </requireJavaVersion>
                                                <requireMavenVersion>
                                                    <version>[3.6.3,)</version>
                                                </requireMavenVersion>
                                            </rules>
                                        </configuration>
                                    </execution>
                                </executions>
                            </plugin>
                        </plugins>
                    </build>
                </project>
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/{app_class}.java": (
            render(
                """
                package @PACKAGE@;

                import org.springframework.boot.SpringApplication;
                import org.springframework.boot.autoconfigure.SpringBootApplication;
                import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

                @SpringBootApplication
                @ConfigurationPropertiesScan
                public class @APP_CLASS@ {

                    public static void main(String[] args) {
                        SpringApplication.run(@APP_CLASS@.class, args);
                    }
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/config/AppProperties.java": (
            render(
                """
                package @PACKAGE@.config;

                import jakarta.validation.constraints.NotBlank;
                import jakarta.validation.constraints.Size;

                import org.springframework.boot.context.properties.ConfigurationProperties;
                import org.springframework.validation.annotation.Validated;

                @Validated
                @ConfigurationProperties(prefix = "app")
                public record AppProperties(
                        @NotBlank @Size(max = 80) String greetingPrefix
                ) {
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/service/GreetingService.java": (
            render(
                """
                package @PACKAGE@.service;

                import org.springframework.stereotype.Service;

                import @PACKAGE@.config.AppProperties;

                @Service
                public class GreetingService {

                    private final AppProperties properties;

                    public GreetingService(AppProperties properties) {
                        this.properties = properties;
                    }

                    public String greetingFor(String name) {
                        return "%s, %s".formatted(this.properties.greetingPrefix(), name);
                    }
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/api/GreetingRequest.java": (
            render(
                """
                package @PACKAGE@.api;

                import jakarta.validation.constraints.NotBlank;
                import jakarta.validation.constraints.Size;

                public record GreetingRequest(
                        @NotBlank @Size(max = 80) String name
                ) {
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/api/GreetingResponse.java": (
            render(
                """
                package @PACKAGE@.api;

                public record GreetingResponse(String message) {
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/api/GreetingController.java": (
            render(
                """
                package @PACKAGE@.api;

                import jakarta.validation.Valid;
                import jakarta.validation.constraints.NotBlank;
                import jakarta.validation.constraints.Size;

                import org.springframework.http.MediaType;
                import org.springframework.validation.annotation.Validated;
                import org.springframework.web.bind.annotation.GetMapping;
                import org.springframework.web.bind.annotation.PathVariable;
                import org.springframework.web.bind.annotation.PostMapping;
                import org.springframework.web.bind.annotation.RequestBody;
                import org.springframework.web.bind.annotation.RequestMapping;
                import org.springframework.web.bind.annotation.RestController;

                import @PACKAGE@.service.GreetingService;

                @Validated
                @RestController
                @RequestMapping(path = "/api/v1/greetings", produces = MediaType.APPLICATION_JSON_VALUE)
                public class GreetingController {

                    private final GreetingService greetingService;

                    public GreetingController(GreetingService greetingService) {
                        this.greetingService = greetingService;
                    }

                    @GetMapping("/{name}")
                    public GreetingResponse greetByPath(
                            @PathVariable @NotBlank @Size(max = 80) String name
                    ) {
                        return new GreetingResponse(this.greetingService.greetingFor(name));
                    }

                    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
                    public GreetingResponse greetByBody(@Valid @RequestBody GreetingRequest request) {
                        return new GreetingResponse(this.greetingService.greetingFor(request.name()));
                    }
                }
                """,
                **values,
            ),
            False,
        ),
        f"{java_root}/api/ApiExceptionHandler.java": (
            render(
                """
                package @PACKAGE@.api;

                import java.util.List;
                import java.util.Map;

                import jakarta.validation.ConstraintViolationException;

                import org.springframework.http.HttpStatus;
                import org.springframework.http.ProblemDetail;
                import org.springframework.web.bind.MethodArgumentNotValidException;
                import org.springframework.web.bind.annotation.ExceptionHandler;
                import org.springframework.web.bind.annotation.RestControllerAdvice;

                @RestControllerAdvice
                public class ApiExceptionHandler {

                    @ExceptionHandler(MethodArgumentNotValidException.class)
                    ProblemDetail handleInvalidRequestBody(MethodArgumentNotValidException ex) {
                        ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
                        problem.setTitle("Request validation failed");
                        problem.setDetail("One or more request fields are invalid.");
                        List<Map<String, String>> violations = ex.getBindingResult().getFieldErrors().stream()
                                .map(error -> Map.of(
                                        "field", error.getField(),
                                        "message", error.getDefaultMessage() == null ? "invalid" : error.getDefaultMessage()))
                                .toList();
                        problem.setProperty("violations", violations);
                        return problem;
                    }

                    @ExceptionHandler(ConstraintViolationException.class)
                    ProblemDetail handleConstraintViolation(ConstraintViolationException ex) {
                        ProblemDetail problem = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
                        problem.setTitle("Request validation failed");
                        problem.setDetail("One or more request parameters are invalid.");
                        List<Map<String, String>> violations = ex.getConstraintViolations().stream()
                                .map(violation -> Map.of(
                                        "field", violation.getPropertyPath().toString(),
                                        "message", violation.getMessage()))
                                .toList();
                        problem.setProperty("violations", violations);
                        return problem;
                    }
                }
                """,
                **values,
            ),
            False,
        ),
        "src/main/resources/application.yml": (
            render(
                """
                server:
                  port: ${SERVER_PORT:@PORT@}
                  shutdown: graceful

                spring:
                  application:
                    name: @ARTIFACT_ID@
                  lifecycle:
                    timeout-per-shutdown-phase: 20s
                @DATABASE_YAML@

                management:
                  endpoints:
                    web:
                      exposure:
                        include: "@ACTUATOR_EXPOSURE@"
                  endpoint:
                    health:
                      probes:
                        enabled: true
                      show-details: never
                  info:
                    env:
                      enabled: true

                info:
                  application:
                    name: @ARTIFACT_ID@
                    version: 0.1.0-SNAPSHOT
                    java: @JAVA_VERSION@
                    spring-boot: @SPRING_BOOT_VERSION@

                app:
                  greeting-prefix: ${APP_GREETING_PREFIX:Hello}
                """,
                **values,
            ).replace("\nspring:\n  application", "\nspring:\n  application").replace("\n\nmanagement:", "\nmanagement:"),
            False,
        ),
        "src/main/resources/application-local.yml": (
            render(
                """
                management:
                  endpoint:
                    health:
                      show-details: always

                logging:
                  level:
                    @PACKAGE@: DEBUG
                """,
                **values,
            ),
            False,
        ),
        "src/main/resources/application-prod.yml": (
            render(
                """
                server:
                  forward-headers-strategy: framework

                logging:
                  structured:
                    format:
                      console: ecs

                management:
                  endpoint:
                    health:
                      show-details: never
                """,
                **values,
            ),
            False,
        ),
        ".env.example": (
            render(
                """
                SPRING_PROFILES_ACTIVE=local
                SERVER_PORT=@PORT@
                APP_GREETING_PREFIX=Hello
                @DATABASE_ENV@
                """,
                **values,
            ).replace("\n\n", "\n"),
            False,
        ),
        ".editorconfig": (
            render(
                """
                root = true

                [*]
                charset = utf-8
                end_of_line = lf
                insert_final_newline = true
                indent_style = space
                indent_size = 4

                [*.{yml,yaml}]
                indent_size = 2

                [*.md]
                trim_trailing_whitespace = false
                """,
                **values,
            ),
            False,
        ),
        ".gitignore": (
            render(
                """
                target/
                .idea/
                .vscode/
                *.iml
                .env
                .DS_Store
                hs_err_pid*
                replay_pid*
                .mvn/wrapper/maven-wrapper.jar
                """,
                **values,
            ),
            False,
        ),
        f"{test_root}/{app_class}Tests.java": (
            render(
                """
                package @PACKAGE@;

                @TESTCONTAINERS_IMPORT@
                import org.junit.jupiter.api.Test;
                import org.springframework.boot.test.context.SpringBootTest;

                @SpringBootTest
                @TESTCONTAINERS_ANNOTATION@
                class @APP_CLASS@Tests {

                    @Test
                    void contextLoads() {
                    }
                }
                """,
                **values,
            ).replace("\n\nimport org.junit", "\nimport org.junit").replace("\n@SpringBootTest\n\n", "\n@SpringBootTest\n"),
            False,
        ),
        f"{test_root}/api/GreetingControllerTest.java": (
            render(
                """
                package @PACKAGE@.api;

                @TESTCONTAINERS_IMPORT@
                import org.junit.jupiter.api.Test;
                import org.springframework.beans.factory.annotation.Autowired;
                import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
                import org.springframework.boot.test.context.SpringBootTest;
                import org.springframework.http.MediaType;
                import org.springframework.test.web.servlet.MockMvc;

                import static org.hamcrest.Matchers.hasSize;
                import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
                import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
                import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
                import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

                @SpringBootTest
                @AutoConfigureMockMvc
                @TESTCONTAINERS_ANNOTATION@
                class GreetingControllerTest {

                    @Autowired
                    private MockMvc mockMvc;

                    @Test
                    void greetsByPath() throws Exception {
                        this.mockMvc.perform(get("/api/v1/greetings/Ada"))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.message").value("Hello, Ada"));
                    }

                    @Test
                    void greetsByRequestBody() throws Exception {
                        this.mockMvc.perform(post("/api/v1/greetings")
                                        .contentType(MediaType.APPLICATION_JSON)
                                        .content("{\\"name\\":\\"Grace\\"}"))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$.message").value("Hello, Grace"));
                    }

                    @Test
                    void reportsValidationErrors() throws Exception {
                        this.mockMvc.perform(post("/api/v1/greetings")
                                        .contentType(MediaType.APPLICATION_JSON)
                                        .content("{\\"name\\":\\"\\"}"))
                                .andExpect(status().isBadRequest())
                                .andExpect(jsonPath("$.title").value("Request validation failed"))
                                .andExpect(jsonPath("$.violations", hasSize(1)));
                    }
                }
                """,
                **values,
            )
            .replace("\n\nimport org.junit", "\nimport org.junit")
            .replace("\n@SpringBootTest\n\n", "\n@SpringBootTest\n")
            .replace("\n@AutoConfigureMockMvc\n\n", "\n@AutoConfigureMockMvc\n"),
            False,
        ),
        "README.md": (
            render(
                """
                # @TITLE@

                Spring Boot service scaffold with Maven, Web MVC, validation, typed configuration, Actuator health/info, profile-aware logging, and tests.@DATABASE_NOTE@@PROMETHEUS_NOTE@

                ## Requirements

                - Java @JAVA_VERSION@ or newer
                - Maven 3.6.3 or newer
                - Docker only when running Compose or database integration tests

                ## Run Locally

                ```bash
                cp .env.example .env
                mvn spring-boot:run
                ```

                ## Test

                ```bash
                mvn test
                ```

                ## Smoke Check

                ```bash
                curl -fsS http://127.0.0.1:@PORT@/actuator/health
                curl -fsS http://127.0.0.1:@PORT@/api/v1/greetings/Ada
                ```

                ## Build

                ```bash
                mvn package
                java -jar target/@ARTIFACT_ID@-0.1.0-SNAPSHOT.jar
                ```

                The default HTTP Actuator exposure is `@ACTUATOR_EXPOSURE@`.
                """,
                **values,
            ),
            False,
        ),
    }

    if tc_source:
        files[f"{test_root}/support/PostgresTestConfiguration.java"] = (tc_source, False)
        if args.database == "postgres":
            files["src/main/resources/db/migration/V1__init.sql"] = (
                render(
                    """
                    create table if not exists app_schema_marker (
                        id bigint primary key,
                        description varchar(255) not null
                    );

                    insert into app_schema_marker (id, description)
                    values (1, 'Initial schema marker')
                    on conflict (id) do nothing;
                    """,
                    **values,
                ),
                False,
            )

    if args.with_docker:
        files.update(
            {
                ".dockerignore": (
                    render(
                        """
                        .git
                        target
                        .idea
                        .vscode
                        .env
                        *.iml
                        """,
                        **values,
                    ),
                    False,
                ),
                "Dockerfile": (
                    render(
                        """
                        ARG JAVA_VERSION=@JAVA_VERSION@

                        FROM maven:3.9-eclipse-temurin-${JAVA_VERSION} AS builder
                        WORKDIR /workspace
                        COPY pom.xml .
                        COPY src ./src
                        RUN mvn -B -DskipTests package

                        FROM eclipse-temurin:${JAVA_VERSION}-jre
                        WORKDIR /app
                        RUN apt-get update \\
                            && apt-get install -y --no-install-recommends curl \\
                            && rm -rf /var/lib/apt/lists/*
                        COPY --from=builder /workspace/target/@ARTIFACT_ID@-0.1.0-SNAPSHOT.jar /app/app.jar
                        EXPOSE @PORT@
                        USER 10001:10001
                        HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \\
                          CMD curl -fsS http://127.0.0.1:@PORT@/actuator/health || exit 1
                        ENTRYPOINT ["java", "-jar", "/app/app.jar"]
                        """,
                        **values,
                    ),
                    False,
                ),
                "compose.yml": (
                    render(
                        """
                        services:
                          app:
                            build: .
                            ports:
                              - "@PORT@:@PORT@"
                            environment:
                              SPRING_PROFILES_ACTIVE: local
                              SERVER_PORT: @PORT@
                              APP_GREETING_PREFIX: Hello
                        @COMPOSE_DATABASE_ENV@
                        @COMPOSE_DEPENDS@
                            healthcheck:
                              test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:@PORT@/actuator/health || exit 1"]
                              interval: 30s
                              timeout: 5s
                              retries: 5
                        @COMPOSE_DATABASE_SERVICE@
                        """,
                        **values,
                    ).replace("\n\n", "\n"),
                    False,
                ),
            }
        )

    if args.with_github_actions:
        files[".github/workflows/ci.yml"] = (
            render(
                """
                name: CI

                on:
                  push:
                    branches: [main]
                  pull_request:

                jobs:
                  test:
                    runs-on: ubuntu-latest
                    steps:
                      - uses: actions/checkout@v4
                      - uses: actions/setup-java@v4
                        with:
                          distribution: temurin
                          java-version: "@JAVA_VERSION@"
                          cache: maven
                      - run: mvn -B test
                """,
                **values,
            ),
            False,
        )

    for relative, (content, executable) in files.items():
        write_file(root, relative, content, executable=executable, force=args.force)

    print(f"Created Spring Boot scaffold at {root}")
    print("Test:        mvn test")
    print("Development: mvn spring-boot:run")
    print(f"Health:      curl -fsS http://127.0.0.1:{args.port}/actuator/health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
