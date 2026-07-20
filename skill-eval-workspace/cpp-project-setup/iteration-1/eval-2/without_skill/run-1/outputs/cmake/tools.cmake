function(enable_clang_tidy target)
    find_program(CLANG_TIDY_EXE NAMES clang-tidy DOC "Path to clang-tidy executable")

    if(CLANG_TIDY_EXE)
        set(CLANG_TIDY_OPTIONS
            "${CLANG_TIDY_EXE}"
            --config-file=${CMAKE_SOURCE_DIR}/.clang-tidy
        )
        set_target_properties(${target} PROPERTIES CXX_CLANG_TIDY "${CLANG_TIDY_OPTIONS}")
        message(STATUS "clang-tidy enabled for target: ${target}")
    else()
        message(WARNING "clang-tidy requested but executable not found")
    endif()
endfunction()

function(add_format_target)
    find_program(CLANG_FORMAT_EXE NAMES clang-format DOC "Path to clang-format executable")

    if(CLANG_FORMAT_EXE)
        add_custom_target(format
            COMMAND ${CLANG_FORMAT_EXE} -i
                ${CMAKE_SOURCE_DIR}/include/**/*.hpp
                ${CMAKE_SOURCE_DIR}/src/**/*.cpp
                ${CMAKE_SOURCE_DIR}/tests/**/*.cpp
            WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
            COMMENT "Formatting source files with clang-format"
        )
    else()
        message(WARNING "clang-format requested but executable not found")
    endif()
endfunction()

add_format_target()
