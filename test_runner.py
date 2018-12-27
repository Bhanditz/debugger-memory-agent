import os
import time
import unittest
from datetime import datetime
from subprocess import check_output
from typing import Iterable, Optional, List
from unittest import TestCase


class JavaCompiler:
    def __init__(self, javac: str, output_path: str) -> None:
        self.__output = output_path
        self.__javac = javac

    def compile_java(self, source_files: List[str]):
        args = list()
        args.append(self.__javac)
        args.extend(['-d', self.__output])
        args.extend(source_files)
        check_output(args)


class Test:
    def __init__(self, name: str, output: str, src_dir: str) -> None:
        self.__name = name
        self.__output = output
        self.__path = '{}/{}'.format(src_dir, name)

    def name(self) -> str:
        return self.__name

    def expected_output(self) -> Optional[str]:
        return self.__output

    def src_path(self):
        return self.__path


class TestResult:
    def __init__(self, test: Test, output: str) -> None:
        self.__output = output
        self.__test = test

    def get_output(self) -> str:
        return self.__output

    def get_test(self) -> Test:
        return self.__test


class TestRunner:
    def __init__(self, java, build_dir: str, output_dir: str) -> None:
        self.__java = java
        self.__build_dir = build_dir
        self.__output_directory = output_dir

    def run(self, test: Test) -> TestResult:
        if not os.path.exists(self.__output_directory):
            os.makedirs(self.__output_directory)

        args = list()
        args.append(self.__java)
        args.append('-agentpath:./cmake-build-debug/native_memory_agent.dll')
        args.extend(['-classpath', self.__build_dir])
        args.append(test.name())

        out = check_output(args).decode("utf-8").replace('\r\n', '\n')

        with open('{}/{}.out'.format(self.__output_directory, test.name()), mode='w') as out_file:
            out_file.write(out)

        return TestResult(test, out)


class TestRepository:
    def __init__(self, path: str) -> None:
        assert os.path.exists(path), "Test repository is not found"
        assert os.path.isdir(path), "Test repository must be a directory"
        self.__path = path
        self.__ignored_dirs = {'common', 'memory'}

    def test_count(self) -> int:
        return len(list(self.__iterate_tests_files(self.test_src_dir())))

    def read_output(self, name) -> Optional[str]:
        try:
            with open('{}/{}.out'.format(self.__test_out_dir(), name), mode='r') as file:
                return file.read()
        except IOError:
            return None

    def write_output(self, name, output):
        with open('{}/{}.out'.format(self.__test_out_dir(), name), mode='w') as file:
            file.write(output)

    def iterate_tests(self) -> Iterable[Test]:
        src_dir = self.test_src_dir()
        for test_name in self.__iterate_tests_files(src_dir):
            yield Test(test_name, self.read_output(test_name), src_dir)

    def __iterate_tests_files(self, src_dir, package: str = '') -> Iterable[str]:
        for file_name in os.listdir(src_dir):
            path = os.path.join(src_dir, file_name)
            if os.path.isdir(path):
                if not self.__is_ignored_dir(file_name):
                    yield from self.__iterate_tests_files(path, self.__join_with_package(package, file_name))
            else:
                yield self.__join_with_package(package, file_name.split('.java')[0])

    def test_src_dir(self) -> str:
        return os.path.join(self.__path, 'src')

    def get_all_files_for_compilation(self) -> List[str]:
        result = list()
        for root, dirs, files in os.walk(os.path.join(self.__path, 'src')):
            for file in files:
                result.append(os.path.join(root, file))
        return result

    @staticmethod
    def __join_with_package(parent: str, child: str) -> str:
        return child if parent == '' else '{}.{}'.format(parent, child)

    def __test_out_dir(self) -> str:
        return os.path.join(self.__path, 'outs')

    def __is_ignored_dir(self, dir_name: str) -> bool:
        return dir_name in self.__ignored_dirs


test_repo = TestRepository('test_data')
timestamp = int(time.time())
timestamp = datetime.fromtimestamp(timestamp).strftime('%Y.%m.%d_%H.%M.%S')
build_directory = 'test_outs/{}/build'.format(timestamp)
output_directory = 'test_outs/{}/outs'.format(timestamp)


class NativeAgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.makedirs(build_directory)
        os.makedirs(output_directory)
        JavaCompiler("C:\\Program Files\\Java\\jdk1.8.0_151\\bin\\javac.exe", build_directory) \
            .compile_java(test_repo.get_all_files_for_compilation())


def to_test_name(value: str) -> str:
    return 'test_{}'.format(value.replace('.', '_').replace(' ', '_').lower())


def create_test(test: Test, runner: TestRunner):
    def do_test(self: TestCase):
        result = runner.run(test)
        actual = result.get_output()
        expected = test.expected_output()
        self.assertEqual(expected.strip(), actual.strip(), "outputs are mismatched")

    return do_test


def create_tests():
    runner = TestRunner("C:\\Program Files\\Java\\jdk1.8.0_151\\bin\\java.exe", build_directory, output_directory)

    for test in test_repo.iterate_tests():
        setattr(NativeAgentTests, to_test_name(test.name()), create_test(test, runner))


create_tests()

if __name__ == '__main__':
    unittest.main()
