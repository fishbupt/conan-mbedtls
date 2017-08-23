from conans import ConanFile, CMake, tools


class MbedtlsConan(ConanFile):
    name = "mbedtls"
    version = "2.5.2"
    license = "MIT"
    url = "<Package recipe repository url here, for issues about the package>"
    build_policy = "missing"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
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
        flags = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else "-DBUILD_SHARED_LIBS=OFF"
        flags += " -DENABLE_PROGRAMS=OFF -DENABLE_TESTING=OFF -DENABLE_ZLIB_SUPPORT=OFF"
        flags += " -DCMAKE_INSTALL_PREFIX=%s" % self.package_folder
        if self.settings.os != "Windows" and self.options.fPIC:
            flags += " -DCMAKE_POSITION_INDEPENDENT_CODE=TURE"
        self.run('cmake mbedtls %s %s' % (cmake.command_line, flags))
        self.run("cmake --build . --target install %s" % cmake.build_config)

    def package_info(self):
        self.cpp_info.libs = ["mbedtls", "mbedx509", "mbedcrypto"]
