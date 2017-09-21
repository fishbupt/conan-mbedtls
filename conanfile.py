from conans import ConanFile, CMake, tools


class MbedtlsConan(ConanFile):
    name = "mbedtls"
    version = "2.5.2"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    build_policy = "missing"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=False"
    generators = "cmake"

    def source(self):
        self.run("git clone https://github.com/ARMmbed/mbedtls.git")
        self.run("cd mbedtls && git checkout mbedtls-%s" % self.version)
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("mbedtls/CMakeLists.txt", "PROJECT(mbed TLS)", '''PROJECT(mbed TLS)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["USE_SHARED_MBEDTLS_LIBRARY"] = "ON"
        else:
            cmake.definitions["USE_STATIC_MBEDTLS_LIBRARY"] = "ON"

        if self.settings.os != "Windows" and self.options.fPIC:
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = "True"
        cmake.definitions["ENABLE_TESTING"] = "OFF"
        cmake.definitions["ENABLE_PROGRAMS"] = "OFF"
        cmake.definitions["ENABLE_ZLIB_SUPPORT"] = "OFF"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder

        cmake.configure(source_dir="mbedtls")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mbedtls", "mbedx509", "mbedcrypto"]
